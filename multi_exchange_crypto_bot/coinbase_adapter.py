"""Coinbase Advanced Trade adapter — SPOT ONLY.

Uses the official ``coinbase-advanced-py`` RESTClient. Every method name and
parameter used below was checked against coinbase-advanced-py 1.8.4;
``verify_sdk()`` re-checks them at runtime and disables live trading if the
installed SDK differs.

Field mapping (Advanced Trade has no ``trading_enabled``/``min_market_funds``):
  trading enabled  <- status == "online" and not trading_disabled / is_disabled / view_only
  min_market_funds <- quote_min_size      max_market_funds <- quote_max_size
  price increment  <- price_increment (falls back to quote_increment)
"""
from __future__ import annotations

import inspect
import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import pandas as pd
import requests

from analysis import INTERVAL_SECONDS, candles_to_frame, drop_incomplete
from config import Settings
from models import (
    ExchangeOrder,
    InsufficientHistory,
    InvalidMetadata,
    LiveTradingDisabled,
    MarketMeta,
    MarketUnavailable,
    OrderRejected,
    OrderStatus,
    Side,
    Venue,
)
from retry import Retrier

log = logging.getLogger("bot.coinbase")

GRANULARITY = {
    "1m": "ONE_MINUTE", "5m": "FIVE_MINUTE", "15m": "FIFTEEN_MINUTE", "30m": "THIRTY_MINUTE",
    "1h": "ONE_HOUR", "2h": "TWO_HOUR", "1d": "ONE_DAY",
}
MAX_CANDLES_PER_REQUEST = 350
STOP_DIRECTION_DOWN = "STOP_DIRECTION_STOP_DOWN"

# Coinbase order status -> normalised status. Unknown statuses stay non-terminal so the
# engine never assumes an order is gone (which could cause a duplicate).
STATUS_MAP = {
    "PENDING": OrderStatus.OPEN,
    "QUEUED": OrderStatus.OPEN,
    "OPEN": OrderStatus.OPEN,
    "CANCEL_QUEUED": OrderStatus.OPEN,
    "EDIT_QUEUED": OrderStatus.OPEN,
    "FILLED": OrderStatus.FILLED,
    "CANCELLED": OrderStatus.CANCELLED,
    "EXPIRED": OrderStatus.EXPIRED,
    "FAILED": OrderStatus.REJECTED,
}

REQUIRED_SDK = {
    "get_public_product": {"product_id"},
    "get_public_candles": {"product_id", "start", "end", "granularity", "limit"},
    "get_accounts": {"limit", "cursor"},
    "get_order": {"order_id"},
    "list_orders": {"product_ids", "order_status", "limit", "cursor"},
    "limit_order_gtc_buy": {"client_order_id", "product_id", "base_size", "limit_price", "post_only"},
    "limit_order_gtc_sell": {"client_order_id", "product_id", "base_size", "limit_price", "post_only"},
    "stop_limit_order_gtc_sell": {"client_order_id", "product_id", "base_size", "limit_price", "stop_price", "stop_direction"},
    "cancel_orders": {"order_ids"},
}


def to_plain(obj: Any) -> Any:
    """SDK responses are objects with to_dict(); nested values may be objects too."""
    if hasattr(obj, "to_dict"):
        obj = obj.to_dict()
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_plain(v) for v in obj]
    return obj


def _dec(value: Any, field: str, required: bool = True) -> Optional[Decimal]:
    if value in (None, ""):
        if required:
            raise InvalidMetadata(f"missing {field}")
        return None
    try:
        out = Decimal(str(value))
    except InvalidOperation as exc:
        raise InvalidMetadata(f"invalid {field}: {value!r}") from exc
    if not out.is_finite():
        raise InvalidMetadata(f"invalid {field}: {value!r}")
    return out


def verify_sdk(client_cls: Any = None) -> None:
    """Raise LiveTradingDisabled if the installed SDK lacks a method or parameter we use."""
    if client_cls is None:
        from coinbase.rest import RESTClient as client_cls  # noqa: N813
    for name, params in REQUIRED_SDK.items():
        fn = getattr(client_cls, name, None)
        if fn is None:
            raise LiveTradingDisabled(f"coinbase-advanced-py has no RESTClient.{name}; check the SDK version")
        missing = params - set(inspect.signature(fn).parameters)
        if missing:
            raise LiveTradingDisabled(f"RESTClient.{name} lacks parameters {sorted(missing)}; check the SDK version")


def parse_product(raw: dict) -> MarketMeta:
    """Validate a get_public_product/get_product response and return MarketMeta."""
    product_id = raw.get("product_id")
    if not product_id:
        raise InvalidMetadata("product response has no product_id")
    product_type = str(raw.get("product_type") or "")
    if product_type != "SPOT":
        raise MarketUnavailable(f"{product_id} is not a Coinbase spot product (type {product_type or 'unknown'})")
    status = str(raw.get("status") or "")
    problems = []
    if status.lower() != "online":
        problems.append(f"status={status or 'missing'}")
    for flag in ("trading_disabled", "is_disabled", "view_only"):
        if raw.get(flag):
            problems.append(flag)
    price_increment = _dec(raw.get("price_increment") or raw.get("quote_increment"), "price_increment")
    return MarketMeta(
        venue=Venue.COINBASE,
        symbol=product_id,
        base_asset=str(raw.get("base_currency_id") or product_id.split("-")[0]),
        quote_asset=str(raw.get("quote_currency_id") or product_id.split("-")[-1]),
        product_type="SPOT",
        tradable=not problems,
        status_detail=", ".join(problems) or "online",
        size_increment=_dec(raw.get("base_increment"), "base_increment"),
        min_size=_dec(raw.get("base_min_size"), "base_min_size"),
        min_notional=_dec(raw.get("quote_min_size"), "quote_min_size"),
        price_increment=price_increment,
        max_notional=_dec(raw.get("quote_max_size"), "quote_max_size", required=False),
        limit_only=bool(raw.get("limit_only")),
        cancel_only=bool(raw.get("cancel_only")),
        post_only=bool(raw.get("post_only")),
        auction_mode=bool(raw.get("auction_mode")),
        last_price=_dec(raw.get("price"), "price", required=False),
        change_24h_pct=_dec(raw.get("price_percentage_change_24h"), "price_percentage_change_24h", required=False),
    )


def normalize_order(raw: dict) -> ExchangeOrder:
    status_raw = str(raw.get("status") or "UNKNOWN")
    filled = Decimal(str(raw.get("filled_size") or "0"))
    avg = raw.get("average_filled_price")
    side = raw.get("side")
    return ExchangeOrder(
        client_order_id=raw.get("client_order_id"),
        exchange_order_id=str(raw["order_id"]),
        status=STATUS_MAP.get(status_raw, OrderStatus.OPEN),
        side=Side(side) if side in ("BUY", "SELL") else None,
        filled_quantity=filled,
        avg_fill_price=Decimal(str(avg)) if avg not in (None, "", "0") and filled > 0 else None,
        fees=Decimal(str(raw.get("total_fees") or "0")),
        raw_status=status_raw,
    )


class CoinbaseAdapter:
    venue = Venue.COINBASE
    exits_share_balance = True  # resting sells place a hold on the base balance

    def __init__(self, settings: Settings, product_id: str, *, authenticated: bool, client: Any = None,
                 retrier: Optional[Retrier] = None):
        self.product_id = product_id
        self.authenticated = authenticated
        self.retrier = retrier or Retrier(settings.max_retries)
        self._meta: Optional[MarketMeta] = None
        if client is not None:
            self.client = client
        else:
            from coinbase.rest import RESTClient

            if authenticated:
                if not (settings.coinbase_api_key and settings.coinbase_api_secret):
                    raise LiveTradingDisabled("COINBASE_API_KEY and COINBASE_API_SECRET are required")
                self.client = RESTClient(
                    api_key=settings.coinbase_api_key.get_secret_value(),
                    api_secret=settings.coinbase_api_secret.get_secret_value(),
                    timeout=settings.api_timeout_seconds,
                )
            else:
                self.client = RESTClient(timeout=settings.api_timeout_seconds)

    # ----------------------------------------------------------- market data
    def get_market_meta(self) -> MarketMeta:
        try:
            raw = to_plain(self.retrier.call(self.client.get_public_product, product_id=self.product_id))
        except requests.exceptions.HTTPError as exc:
            code = getattr(exc.response, "status_code", None)
            if code in (400, 404):
                raise MarketUnavailable(f"{self.product_id} is not listed on Coinbase Advanced") from exc
            raise
        if not isinstance(raw, dict):
            raise InvalidMetadata("unexpected product response")
        self._meta = parse_product(raw)
        return self._meta

    def get_candles(self, interval: str, count: int, now: Optional[datetime] = None) -> pd.DataFrame:
        if interval not in GRANULARITY:
            raise ValueError(f"Coinbase does not support interval {interval}")
        now = now or datetime.now(timezone.utc)
        seconds = INTERVAL_SECONDS[interval]
        end = int(now.timestamp())
        rows: list[dict] = []
        while len(rows) < count:
            batch = min(MAX_CANDLES_PER_REQUEST, count - len(rows) + 1)
            start = end - batch * seconds
            resp = to_plain(self.retrier.call(
                self.client.get_public_candles, product_id=self.product_id, start=str(start), end=str(end),
                granularity=GRANULARITY[interval], limit=batch,
            ))
            candles = resp.get("candles") if isinstance(resp, dict) else None
            if candles is None:
                raise InvalidMetadata("unexpected candles response")
            if not candles:
                break
            rows.extend(
                {"time": c["start"], "open": c["open"], "high": c["high"], "low": c["low"],
                 "close": c["close"], "volume": c["volume"]}
                for c in candles
            )
            end = start
        df = drop_incomplete(candles_to_frame(rows), interval, now)
        if df.empty:
            raise InsufficientHistory(f"no candles returned for {self.product_id}")
        return df.tail(count)

    # --------------------------------------------------------------- account
    def _accounts(self) -> list[dict]:
        accounts, cursor = [], None
        for _ in range(20):
            resp = to_plain(self.retrier.call(self.client.get_accounts, limit=250, cursor=cursor))
            accounts.extend(resp.get("accounts") or [])
            if not resp.get("has_next"):
                break
            cursor = resp.get("cursor")
        return accounts

    def _available(self, currency: str) -> Decimal:
        for acct in self._accounts():
            if acct.get("currency") == currency:
                return Decimal(str((acct.get("available_balance") or {}).get("value") or "0"))
        return Decimal(0)

    def _require_meta(self) -> MarketMeta:
        if self._meta is None:
            self.get_market_meta()
        return self._meta

    def available_position(self) -> Decimal:
        return self._available(self._require_meta().base_asset)

    def available_quote(self) -> Decimal:
        return self._available(self._require_meta().quote_asset)

    # ---------------------------------------------------------------- orders
    @staticmethod
    def _order_id_from_create(resp: Any) -> str:
        data = to_plain(resp)
        if not isinstance(data, dict):
            raise OrderRejected("unexpected create-order response")
        if data.get("success"):
            order_id = (data.get("success_response") or {}).get("order_id") or data.get("order_id")
            if order_id:
                return str(order_id)
        err = data.get("error_response") or {}
        reason = err.get("preview_failure_reason") or err.get("error") or data.get("failure_reason") or "unknown"
        raise OrderRejected(f"Coinbase rejected order: {reason} {err.get('message', '')}".strip())

    def place_limit_buy(self, client_order_id: str, quantity: Decimal, price: Decimal) -> str:
        if not self.authenticated:
            raise LiveTradingDisabled("unauthenticated adapter cannot place orders")
        # Never retried: see retry.py.
        return self._order_id_from_create(self.client.limit_order_gtc_buy(
            client_order_id=client_order_id, product_id=self.product_id,
            base_size=str(quantity), limit_price=str(price), post_only=False,
        ))

    def place_limit_sell(self, client_order_id: str, quantity: Decimal, price: Decimal, reduce_only: bool) -> str:
        # Spot has no reduce-only flag; sells are bounded by the available base balance,
        # which the engine checks before calling this.
        if not self.authenticated:
            raise LiveTradingDisabled("unauthenticated adapter cannot place orders")
        return self._order_id_from_create(self.client.limit_order_gtc_sell(
            client_order_id=client_order_id, product_id=self.product_id,
            base_size=str(quantity), limit_price=str(price), post_only=False,
        ))

    def place_stop_limit_sell(self, client_order_id: str, quantity: Decimal, trigger_price: Decimal,
                              limit_price: Decimal, reduce_only: bool) -> str:
        if not self.authenticated:
            raise LiveTradingDisabled("unauthenticated adapter cannot place orders")
        return self._order_id_from_create(self.client.stop_limit_order_gtc_sell(
            client_order_id=client_order_id, product_id=self.product_id, base_size=str(quantity),
            limit_price=str(limit_price), stop_price=str(trigger_price), stop_direction=STOP_DIRECTION_DOWN,
        ))

    def _list_orders(self, **filters) -> list[dict]:
        orders, cursor = [], None
        for _ in range(10):
            resp = to_plain(self.retrier.call(
                self.client.list_orders, product_ids=[self.product_id], limit=250, cursor=cursor, **filters
            ))
            orders.extend(resp.get("orders") or [])
            if not resp.get("has_next"):
                break
            cursor = resp.get("cursor")
        return orders

    def get_order(self, client_order_id: str, exchange_order_id: Optional[str]) -> Optional[ExchangeOrder]:
        if exchange_order_id:
            resp = to_plain(self.retrier.call(self.client.get_order, order_id=exchange_order_id))
            raw = resp.get("order") if isinstance(resp, dict) else None
            return normalize_order(raw) if raw else None
        for raw in self._list_orders():
            if raw.get("client_order_id") == client_order_id:
                return normalize_order(raw)
        return None

    def list_open_orders(self) -> list[ExchangeOrder]:
        return [normalize_order(o) for o in self._list_orders(order_status=["OPEN"])]

    def cancel_orders(self, exchange_order_ids: list[str]) -> dict[str, bool]:
        if not exchange_order_ids:
            return {}
        resp = to_plain(self.retrier.call(self.client.cancel_orders, order_ids=list(exchange_order_ids)))
        results = {oid: False for oid in exchange_order_ids}
        for item in (resp.get("results") or []):
            if item.get("order_id") in results:
                results[item["order_id"]] = bool(item.get("success"))
                if not item.get("success"):
                    log.warning("cancel failed order_id=%s reason=%s", item.get("order_id"), item.get("failure_reason"))
        return results
