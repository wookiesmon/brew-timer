"""Hyperliquid perpetuals adapter — ISOLATED MARGIN ONLY, long-only, reduce-only exits.

Uses the official ``hyperliquid-python-sdk`` (checked against 0.24.0). ``verify_sdk()``
re-checks every method/parameter at runtime and disables live trading on mismatch.

Exchange rules used (from Hyperliquid docs; re-verify before live use):
- Size precision: ``szDecimals`` from the universe metadata.
- Price precision (perps): at most 5 significant figures and at most
  (6 - szDecimals) decimals; integer prices are always valid.
- Minimum order value: $10 notional.
- Trigger (stop) orders trigger on the MARK price, not the last trade.
- Protective stop: trigger order with isMarket=False (stop-limit), tpsl="sl",
  reduce_only=True. Take-profits: reduce-only GTC limit sells.

Use an API wallet ("agent") private key: API wallets can trade but cannot withdraw.
"""
from __future__ import annotations

import hashlib
import inspect
import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import pandas as pd

from analysis import INTERVAL_SECONDS, candles_to_frame, drop_incomplete
from config import Settings
from models import (
    ExchangeOrder,
    FatalRiskError,
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

log = logging.getLogger("bot.hyperliquid")

HL_MIN_ORDER_NOTIONAL_USD = Decimal("10")
SUPPORTED_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "2h", "1d"}

REQUIRED_INFO = {
    "meta_and_asset_ctxs": set(),
    "candles_snapshot": {"name", "interval", "startTime", "endTime"},
    "user_state": {"address"},
    "frontend_open_orders": {"address"},
    "query_order_by_cloid": {"user", "cloid"},
    "user_fills": {"address"},
}
REQUIRED_EXCHANGE = {
    "order": {"name", "is_buy", "sz", "limit_px", "order_type", "reduce_only", "cloid"},
    "cancel": {"name", "oid"},
    "update_leverage": {"leverage", "name", "is_cross"},
}


def unavailable_message(coin: str) -> str:
    return f"{coin} is unavailable on Hyperliquid; no order will be submitted."


def verify_sdk() -> None:
    """Raise LiveTradingDisabled if the installed SDK lacks anything this adapter uses."""
    try:
        from hyperliquid.exchange import Exchange
        from hyperliquid.info import Info
        from hyperliquid.utils.signing import order_type_to_wire
        from hyperliquid.utils.types import Cloid
    except ImportError as exc:
        raise LiveTradingDisabled(f"hyperliquid-python-sdk not importable: {exc}") from exc
    for cls, required in ((Info, REQUIRED_INFO), (Exchange, REQUIRED_EXCHANGE)):
        for name, params in required.items():
            fn = getattr(cls, name, None)
            if fn is None:
                raise LiveTradingDisabled(f"hyperliquid SDK has no {cls.__name__}.{name}")
            missing = params - set(inspect.signature(fn).parameters)
            if missing:
                raise LiveTradingDisabled(f"{cls.__name__}.{name} lacks parameters {sorted(missing)}")
    try:
        wire = order_type_to_wire({"trigger": {"triggerPx": 1.0, "isMarket": False, "tpsl": "sl"}})
        assert wire["trigger"]["isMarket"] is False and wire["trigger"]["tpsl"] == "sl"
        Cloid("0x" + "0" * 32)
    except Exception as exc:  # noqa: BLE001
        raise LiveTradingDisabled(f"stop-limit trigger orders could not be verified in the SDK: {exc}") from exc


def cloid_for(client_order_id: str):
    """Hyperliquid client IDs must be 16-byte hex; derive one deterministically."""
    from hyperliquid.utils.types import Cloid

    return Cloid("0x" + hashlib.sha256(client_order_id.encode()).hexdigest()[:32])


def _dec(value: Any, field: str) -> Decimal:
    try:
        out = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise InvalidMetadata(f"invalid {field}: {value!r}") from exc
    if not out.is_finite():
        raise InvalidMetadata(f"invalid {field}: {value!r}")
    return out


def parse_universe(meta_and_ctxs: Any, coin: str) -> MarketMeta:
    if not (isinstance(meta_and_ctxs, list) and len(meta_and_ctxs) == 2):
        raise InvalidMetadata("unexpected metaAndAssetCtxs response")
    meta, ctxs = meta_and_ctxs
    universe = meta.get("universe") if isinstance(meta, dict) else None
    if not isinstance(universe, list) or not isinstance(ctxs, list):
        raise InvalidMetadata("metaAndAssetCtxs response has no universe")
    for idx, asset in enumerate(universe):
        if asset.get("name") != coin:
            continue
        if asset.get("isDelisted"):
            raise MarketUnavailable(f"{coin} is delisted on Hyperliquid; no order will be submitted.")
        sz_decimals = asset.get("szDecimals")
        max_leverage = asset.get("maxLeverage")
        if not isinstance(sz_decimals, int) or not (0 <= sz_decimals <= 6):
            raise InvalidMetadata(f"{coin}: invalid szDecimals {sz_decimals!r}")
        if not isinstance(max_leverage, int) or max_leverage < 1:
            raise InvalidMetadata(f"{coin}: invalid maxLeverage {max_leverage!r}")
        ctx = ctxs[idx] if idx < len(ctxs) else {}
        mark = ctx.get("markPx")
        mid = ctx.get("midPx")
        prev = ctx.get("prevDayPx")
        mark_d = _dec(mark, "markPx") if mark not in (None, "") else None
        change = None
        if mark_d is not None and prev not in (None, "", "0"):
            change = (mark_d / _dec(prev, "prevDayPx") - 1) * 100
        increment = Decimal(1).scaleb(-sz_decimals)
        return MarketMeta(
            venue=Venue.HYPERLIQUID,
            symbol=coin,
            base_asset=coin,
            quote_asset="USDC",
            product_type="PERP",
            tradable=mark_d is not None and mark_d > 0,
            status_detail="active" if mark_d else "no mark price (inactive)",
            size_increment=increment,
            min_size=increment,
            min_notional=HL_MIN_ORDER_NOTIONAL_USD,
            price_increment=None,
            sz_decimals=sz_decimals,
            max_leverage=max_leverage,
            only_isolated=bool(asset.get("onlyIsolated", False)),
            last_price=_dec(mid, "midPx") if mid not in (None, "") else mark_d,
            mark_price=mark_d,
            change_24h_pct=change,
            funding_rate=_dec(ctx["funding"], "funding") if ctx.get("funding") not in (None, "") else None,
        )
    raise MarketUnavailable(unavailable_message(coin))


STATUS_MAP = {
    "open": OrderStatus.OPEN,
    "triggered": OrderStatus.OPEN,
    "filled": OrderStatus.FILLED,
    "rejected": OrderStatus.REJECTED,
}


def map_status(raw: str) -> OrderStatus:
    if raw in STATUS_MAP:
        return STATUS_MAP[raw]
    if raw.lower().endswith("canceled") or raw.lower().endswith("cancelled"):
        return OrderStatus.CANCELLED
    if raw.lower().endswith("rejected"):
        return OrderStatus.REJECTED
    return OrderStatus.OPEN  # unknown: keep non-terminal to avoid duplicating orders


def parse_order_response(resp: Any) -> str:
    if not isinstance(resp, dict) or resp.get("status") != "ok":
        raise OrderRejected(f"Hyperliquid rejected order: {str(resp)[:200]}")
    try:
        status = resp["response"]["data"]["statuses"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise OrderRejected("unexpected Hyperliquid order response") from exc
    if "error" in status:
        raise OrderRejected(f"Hyperliquid rejected order: {status['error']}")
    for key in ("resting", "filled"):
        if key in status and "oid" in status[key]:
            return str(status[key]["oid"])
    raise OrderRejected(f"unexpected Hyperliquid order status: {status}")


class HyperliquidAdapter:
    venue = Venue.HYPERLIQUID
    exits_share_balance = False  # reduce-only exits do not reserve the position

    def __init__(self, settings: Settings, coin: str, *, authenticated: bool, info: Any = None,
                 exchange: Any = None, retrier: Optional[Retrier] = None):
        self.coin = coin
        self.settings = settings
        self.authenticated = authenticated
        self.retrier = retrier or Retrier(settings.max_retries)
        self.address = settings.hyperliquid_account_address
        from hyperliquid.utils import constants

        self.base_url = constants.TESTNET_API_URL if settings.hyperliquid_testnet else constants.MAINNET_API_URL
        self._info = info
        self._exchange = exchange
        if authenticated and exchange is None:
            if not (settings.hyperliquid_private_key and self.address):
                raise LiveTradingDisabled("HYPERLIQUID_PRIVATE_KEY and HYPERLIQUID_ACCOUNT_ADDRESS are required")

    @property
    def info(self):
        if self._info is None:
            from hyperliquid.info import Info

            self._info = Info(self.base_url, skip_ws=True, timeout=self.settings.api_timeout_seconds)
        return self._info

    @property
    def exchange(self):
        if not self.authenticated:
            raise LiveTradingDisabled("unauthenticated adapter cannot place orders")
        if self._exchange is None:
            from eth_account import Account
            from hyperliquid.exchange import Exchange

            wallet = Account.from_key(self.settings.hyperliquid_private_key.get_secret_value())
            self._exchange = Exchange(wallet, self.base_url, account_address=self.address,
                                      timeout=self.settings.api_timeout_seconds)
        return self._exchange

    # ----------------------------------------------------------- market data
    def get_market_meta(self) -> MarketMeta:
        return parse_universe(self.retrier.call(self.info.meta_and_asset_ctxs), self.coin)

    def get_candles(self, interval: str, count: int, now: Optional[datetime] = None) -> pd.DataFrame:
        if interval not in SUPPORTED_INTERVALS:
            raise ValueError(f"Hyperliquid interval {interval} not supported here")
        now = now or datetime.now(timezone.utc)
        end_ms = int(now.timestamp() * 1000)
        start_ms = end_ms - (count + 1) * INTERVAL_SECONDS[interval] * 1000
        raw = self.retrier.call(self.info.candles_snapshot, name=self.coin, interval=interval,
                                startTime=start_ms, endTime=end_ms)
        if not isinstance(raw, list):
            raise InvalidMetadata("unexpected candles response")
        rows = [{"time": int(c["t"]) // 1000, "open": c["o"], "high": c["h"], "low": c["l"],
                 "close": c["c"], "volume": c["v"]} for c in raw]
        df = drop_incomplete(candles_to_frame(rows), interval, now)
        if df.empty:
            raise InsufficientHistory(f"no candles returned for {self.coin}")
        return df.tail(count)

    # --------------------------------------------------------------- account
    def user_state(self) -> dict:
        if not self.address:
            raise LiveTradingDisabled("HYPERLIQUID_ACCOUNT_ADDRESS is required")
        state = self.retrier.call(self.info.user_state, address=self.address)
        if not isinstance(state, dict) or "marginSummary" not in state:
            raise InvalidMetadata("unexpected clearinghouseState response")
        return state

    def account_equity(self) -> Decimal:
        return _dec(self.user_state()["marginSummary"]["accountValue"], "accountValue")

    def position_info(self) -> Optional[dict]:
        for item in self.user_state().get("assetPositions") or []:
            pos = item.get("position") or {}
            if pos.get("coin") == self.coin and Decimal(str(pos.get("szi") or "0")) != 0:
                return pos
        return None

    def available_position(self) -> Decimal:
        pos = self.position_info()
        if pos is None:
            return Decimal(0)
        if (pos.get("leverage") or {}).get("type") != "isolated":
            raise FatalRiskError(f"{self.coin} position is not isolated margin; refusing to manage it")
        size = _dec(pos["szi"], "szi")
        if size < 0:
            raise FatalRiskError(f"{self.coin} position is short; this bot is long-only")
        return size

    def available_quote(self) -> Decimal:
        return _dec(self.user_state().get("withdrawable", "0"), "withdrawable")

    def exchange_liquidation_price(self) -> Optional[Decimal]:
        pos = self.position_info()
        if pos and pos.get("liquidationPx") not in (None, ""):
            return _dec(pos["liquidationPx"], "liquidationPx")
        return None

    def prepare_live(self, leverage: int) -> None:
        """Set ISOLATED margin at the configured leverage. Never cross."""
        if leverage < 1:
            raise LiveTradingDisabled("leverage must be >= 1")
        pos = self.position_info()
        if pos is not None and (pos.get("leverage") or {}).get("type") != "isolated":
            raise LiveTradingDisabled(f"existing {self.coin} position uses cross margin; close it first")
        resp = self.exchange.update_leverage(leverage, self.coin, is_cross=False)
        if not isinstance(resp, dict) or resp.get("status") != "ok":
            raise LiveTradingDisabled(f"could not set isolated {leverage}x leverage: {str(resp)[:200]}")

    # ---------------------------------------------------------------- orders
    def place_limit_buy(self, client_order_id: str, quantity: Decimal, price: Decimal) -> str:
        return parse_order_response(self.exchange.order(
            self.coin, True, float(quantity), float(price), {"limit": {"tif": "Gtc"}},
            reduce_only=False, cloid=cloid_for(client_order_id),
        ))

    def place_limit_sell(self, client_order_id: str, quantity: Decimal, price: Decimal, reduce_only: bool) -> str:
        if not reduce_only:
            raise OrderRejected("Hyperliquid exits must be reduce-only")
        return parse_order_response(self.exchange.order(
            self.coin, False, float(quantity), float(price), {"limit": {"tif": "Gtc"}},
            reduce_only=True, cloid=cloid_for(client_order_id),
        ))

    def place_stop_limit_sell(self, client_order_id: str, quantity: Decimal, trigger_price: Decimal,
                              limit_price: Decimal, reduce_only: bool) -> str:
        if not reduce_only:
            raise OrderRejected("Hyperliquid exits must be reduce-only")
        order_type = {"trigger": {"triggerPx": float(trigger_price), "isMarket": False, "tpsl": "sl"}}
        return parse_order_response(self.exchange.order(
            self.coin, False, float(quantity), float(limit_price), order_type,
            reduce_only=True, cloid=cloid_for(client_order_id),
        ))

    def _fills_for(self, oid: int) -> tuple[Decimal, Decimal, Decimal]:
        size = notional = fees = Decimal(0)
        for fill in self.retrier.call(self.info.user_fills, address=self.address) or []:
            if fill.get("oid") == oid and fill.get("coin") == self.coin:
                sz, px = Decimal(str(fill["sz"])), Decimal(str(fill["px"]))
                size += sz
                notional += sz * px
                fees += Decimal(str(fill.get("fee") or "0"))
        return size, notional, fees

    def get_order(self, client_order_id: str, exchange_order_id: Optional[str]) -> Optional[ExchangeOrder]:
        resp = self.retrier.call(self.info.query_order_by_cloid, user=self.address, cloid=cloid_for(client_order_id))
        if not isinstance(resp, dict) or resp.get("status") != "order":
            return None
        wrapper = resp.get("order") or {}
        order = wrapper.get("order") or {}
        raw_status = str(wrapper.get("status") or "unknown")
        oid = order.get("oid")
        orig, remaining = Decimal(str(order.get("origSz", "0"))), Decimal(str(order.get("sz", "0")))
        status = map_status(raw_status)
        filled = orig - remaining if status != OrderStatus.FILLED else orig
        avg = None
        fees = Decimal(0)
        if filled > 0 and oid is not None:
            f_size, f_notional, fees = self._fills_for(int(oid))
            if f_size > 0:
                avg = f_notional / f_size
            else:
                avg = Decimal(str(order.get("limitPx")))
                log.warning("no fills found for oid=%s; using limit price as average", oid)
        return ExchangeOrder(
            client_order_id=client_order_id,
            exchange_order_id=str(oid),
            status=status,
            side=Side.BUY if order.get("side") == "B" else Side.SELL,
            quantity=orig,
            filled_quantity=filled,
            avg_fill_price=avg,
            fees=fees,
            raw_status=raw_status,
        )

    def list_open_orders(self) -> list[ExchangeOrder]:
        orders = self.retrier.call(self.info.frontend_open_orders, address=self.address) or []
        out = []
        for o in orders:
            if o.get("coin") != self.coin:
                continue
            orig, sz = Decimal(str(o.get("origSz", "0"))), Decimal(str(o.get("sz", "0")))
            out.append(ExchangeOrder(
                client_order_id=o.get("cloid"),
                exchange_order_id=str(o["oid"]),
                status=OrderStatus.OPEN,
                side=Side.BUY if o.get("side") == "B" else Side.SELL,
                quantity=orig,
                filled_quantity=orig - sz,
                raw_status="open",
            ))
        return out

    def cancel_orders(self, exchange_order_ids: list[str]) -> dict[str, bool]:
        results = {}
        for oid in exchange_order_ids:
            try:
                resp = self.retrier.call(self.exchange.cancel, self.coin, int(oid))
                ok = isinstance(resp, dict) and resp.get("status") == "ok" and not any(
                    isinstance(s, dict) and "error" in s
                    for s in ((resp.get("response") or {}).get("data") or {}).get("statuses", [])
                )
            except Exception as exc:  # noqa: BLE001
                log.warning("cancel failed oid=%s error=%s", oid, type(exc).__name__)
                ok = False
            results[oid] = ok
        return results

    # ------------------------------------------------------------ pre-flight
    def signer_address(self) -> str:
        from eth_account import Account

        if not self.settings.hyperliquid_private_key:
            raise LiveTradingDisabled("HYPERLIQUID_PRIVATE_KEY is required")
        return Account.from_key(self.settings.hyperliquid_private_key.get_secret_value()).address

    def check_api_wallet(self) -> None:
        """Refuse the main wallet's key: only an API (agent) wallet is unable to withdraw."""
        if not self.address:
            raise LiveTradingDisabled("HYPERLIQUID_ACCOUNT_ADDRESS is required")
        if self.signer_address().lower() == self.address.lower():
            raise LiveTradingDisabled(
                "HYPERLIQUID_PRIVATE_KEY is the main account's key, which can withdraw funds; "
                "generate an API wallet and use its key instead")
