"""Optional CoinGecko market-data checks: coin screening and a pre-trade sanity check.

CoinGecko is a data aggregator, not a venue: nothing here places or sizes orders.
Entries, stops and fills always use the exchange's own prices and candles.

Endpoints used (CoinGecko API v3; re-verify against https://docs.coingecko.com):
  GET /search?query=SYM                              resolve a symbol to a coin id
  GET /coins/markets?vs_currency=usd&ids=...         price, 24h volume, market cap
  GET /coins/markets?vs_currency=usd&order=volume_desc&per_page=250&page=N   screening
  GET /coins/{id}/tickers?exchange_ids=gdax          per-exchange volume (Coinbase = "gdax")

Auth: a free Demo key goes in the ``x-cg-demo-api-key`` header on api.coingecko.com;
a paid key goes in ``x-cg-pro-api-key`` on pro-api.coingecko.com.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Callable, Optional

import requests

from config import Settings
from models import BotError, MarketMeta, Venue
from retry import Retrier

log = logging.getLogger("bot.coingecko")

DEMO_BASE_URL = "https://api.coingecko.com/api/v3"
PRO_BASE_URL = "https://pro-api.coingecko.com/api/v3"
STALE_AFTER = timedelta(minutes=15)
USD_QUOTES = {"USD", "USDC", "USDT"}
# Response cache lifetimes in seconds. The free Demo plan has a monthly call cap, and a bot
# polling every 30s would exhaust it in days without caching. Prices are cached briefly;
# exchange volume and symbol lookups change slowly.
CACHE_TTL = {"/search": 24 * 3600, "/coins/markets": 300, "/tickers": 3600}


class CoinGeckoError(BotError):
    """CoinGecko data was unavailable or unusable."""


def _dec(value: Any) -> Optional[Decimal]:
    if value in (None, ""):
        return None
    try:
        out = Decimal(str(value))
    except Exception:  # noqa: BLE001
        return None
    return out if out.is_finite() else None


def parse_coin_id_overrides(raw: str) -> dict[str, str]:
    """'GTC=gitcoin,BTC=bitcoin' -> {'GTC': 'gitcoin', 'BTC': 'bitcoin'}."""
    out = {}
    for part in (raw or "").split(","):
        if "=" in part:
            sym, coin_id = part.split("=", 1)
            if sym.strip() and coin_id.strip():
                out[sym.strip().upper()] = coin_id.strip()
    return out


class CoinGeckoClient:
    def __init__(self, settings: Settings, *, session: Any = None, retrier: Optional[Retrier] = None,
                 clock: Callable[[], float] = time.monotonic):
        self.settings = settings
        pro = settings.coingecko_plan == "pro"
        self.base_url = PRO_BASE_URL if pro else DEMO_BASE_URL
        self.headers = {"accept": "application/json"}
        if settings.coingecko_api_key is not None:
            header = "x-cg-pro-api-key" if pro else "x-cg-demo-api-key"
            self.headers[header] = settings.coingecko_api_key.get_secret_value()
        self.session = session or requests.Session()
        self.retrier = retrier or Retrier(settings.max_retries)
        self.overrides = parse_coin_id_overrides(settings.coingecko_coin_ids)
        self.clock = clock
        self._cache: dict[tuple, tuple[float, Any]] = {}
        self.calls = 0

    @staticmethod
    def _ttl(path: str) -> float:
        for prefix, ttl in CACHE_TTL.items():
            if path.startswith(prefix) or path.endswith(prefix):
                return ttl
        return 60

    def _get(self, path: str, **params) -> Any:
        key = (path, tuple(sorted(params.items())))
        cached = self._cache.get(key)
        if cached and cached[0] > self.clock():
            return cached[1]
        value = self._fetch(path, params)
        self._cache[key] = (self.clock() + self._ttl(path), value)
        return value

    def _fetch(self, path: str, params: dict) -> Any:
        self.calls += 1

        def call():
            resp = self.session.get(f"{self.base_url}{path}", params=params, headers=self.headers,
                                    timeout=self.settings.api_timeout_seconds)
            resp.raise_for_status()
            return resp.json()

        return self.retrier.call(call)

    # ------------------------------------------------------------- lookups
    def resolve_coin_id(self, symbol: str) -> str:
        """Exact symbol match with the best market-cap rank; COINGECKO_COIN_IDS overrides it.
        Many coins share a ticker symbol, so set an override when the match is ambiguous."""
        symbol = symbol.upper()
        if symbol in self.overrides:
            return self.overrides[symbol]
        data = self._get("/search", query=symbol)
        coins = [c for c in (data or {}).get("coins", []) if str(c.get("symbol", "")).upper() == symbol]
        if not coins:
            raise CoinGeckoError(f"CoinGecko has no coin with symbol {symbol}")
        coins.sort(key=lambda c: c.get("market_cap_rank") or 10**9)
        if len(coins) > 1:
            log.info("symbol %s matches %d CoinGecko coins; using %s (set COINGECKO_COIN_IDS to override)",
                     symbol, len(coins), coins[0].get("id"))
        return str(coins[0]["id"])

    def market(self, coin_id: str) -> dict:
        rows = self._get("/coins/markets", vs_currency="usd", ids=coin_id)
        if not isinstance(rows, list) or not rows:
            raise CoinGeckoError(f"no CoinGecko market data for {coin_id}")
        return rows[0]

    def top_markets(self, pages: int = 1) -> list[dict]:
        rows: list[dict] = []
        for page in range(1, pages + 1):
            batch = self._get("/coins/markets", vs_currency="usd", order="volume_desc", per_page=250, page=page)
            if not isinstance(batch, list) or not batch:
                break
            rows.extend(batch)
        return rows

    def venue_volume_usd(self, coin_id: str, exchange_id: str) -> Decimal:
        """24h USD volume of the coin's USD/USDC/USDT pairs on one exchange."""
        data = self._get(f"/coins/{coin_id}/tickers", exchange_ids=exchange_id)
        total = Decimal(0)
        for t in (data or {}).get("tickers", []):
            if str(t.get("target", "")).upper() not in USD_QUOTES or t.get("is_stale") or t.get("is_anomaly"):
                continue
            total += _dec((t.get("converted_volume") or {}).get("usd")) or Decimal(0)
        return total


# ------------------------------------------------------------- pre-trade check
@dataclass
class MarketCheck:
    coin_id: str
    reference_price: Optional[Decimal]
    venue_price: Optional[Decimal]
    deviation_pct: Optional[Decimal]
    total_volume_usd: Optional[Decimal]
    venue_volume_usd: Optional[Decimal]
    market_cap_usd: Optional[Decimal]
    last_updated: Optional[str]
    problems: list[str] = field(default_factory=list)  # any problem refuses new plans
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def check_market(client: CoinGeckoClient, meta: MarketMeta, settings: Settings, *,
                 planned_notional: Optional[Decimal] = None,
                 now: Optional[datetime] = None) -> MarketCheck:
    """Compare the venue against CoinGecko's cross-exchange view. Never raises for data
    problems: they come back as ``problems`` so the caller fails closed."""
    now = now or datetime.now(timezone.utc)
    venue_price = meta.mark_price or meta.last_price
    try:
        coin_id = client.resolve_coin_id(meta.base_asset)
        row = client.market(coin_id)
    except (CoinGeckoError, requests.exceptions.RequestException, ValueError) as exc:
        return MarketCheck("?", None, venue_price, None, None, None, None, None,
                           problems=[f"CoinGecko check unavailable ({type(exc).__name__}: {exc})"[:200]])

    check = MarketCheck(
        coin_id=coin_id,
        reference_price=_dec(row.get("current_price")),
        venue_price=venue_price,
        deviation_pct=None,
        total_volume_usd=_dec(row.get("total_volume")),
        venue_volume_usd=None,
        market_cap_usd=_dec(row.get("market_cap")),
        last_updated=row.get("last_updated"),
    )

    stale = True
    if check.last_updated:
        try:
            updated = datetime.fromisoformat(str(check.last_updated).replace("Z", "+00:00"))
            stale = now - updated > STALE_AFTER
        except ValueError:
            pass
    if stale:
        check.notes.append("CoinGecko price is stale or undated; price comparison skipped")
    elif check.reference_price and venue_price:
        check.deviation_pct = abs(venue_price - check.reference_price) / check.reference_price * 100
        if check.deviation_pct > settings.coingecko_max_price_deviation_pct:
            check.problems.append(
                f"{meta.venue.value} price {venue_price} differs from CoinGecko {check.reference_price} by "
                f"{check.deviation_pct:.2f}% (> {settings.coingecko_max_price_deviation_pct}%)")

    if check.total_volume_usd is None or check.total_volume_usd < settings.coingecko_min_volume_usd:
        check.problems.append(
            f"24h volume across all exchanges {check.total_volume_usd} USD is below "
            f"COINGECKO_MIN_VOLUME_USD={settings.coingecko_min_volume_usd}")

    if meta.venue == Venue.COINBASE:
        try:
            check.venue_volume_usd = client.venue_volume_usd(coin_id, settings.coingecko_coinbase_exchange_id)
        except (requests.exceptions.RequestException, ValueError) as exc:
            check.problems.append(f"Coinbase volume unavailable from CoinGecko ({type(exc).__name__})")
        else:
            if check.venue_volume_usd < settings.coingecko_min_venue_volume_usd:
                check.problems.append(
                    f"Coinbase 24h volume {check.venue_volume_usd:.0f} USD is below "
                    f"COINGECKO_MIN_VENUE_VOLUME_USD={settings.coingecko_min_venue_volume_usd}; "
                    "stops are more likely to slip or not fill")
            if planned_notional and check.venue_volume_usd > 0:
                share = planned_notional / check.venue_volume_usd * 100
                if share > settings.coingecko_max_volume_share_pct:
                    check.problems.append(
                        f"planned position is {share:.2f}% of Coinbase's 24h volume "
                        f"(> COINGECKO_MAX_VOLUME_SHARE_PCT={settings.coingecko_max_volume_share_pct})")
    else:
        check.notes.append("Hyperliquid perp volume is not on CoinGecko's spot tickers; venue-volume check skipped "
                           "(CoinGecko price is spot, so a small perp basis is normal)")
    return check


# ------------------------------------------------------------------ screening
@dataclass
class ScreenRow:
    symbol: str
    coin_id: str
    name: str
    price: Optional[Decimal]
    change_24h_pct: Optional[Decimal]
    total_volume_usd: Optional[Decimal]
    market_cap_usd: Optional[Decimal]
    venue_symbol: str
    venue_volume_usd: Optional[Decimal] = None
    ambiguous: bool = False


def screen(client: CoinGeckoClient, venue_symbols: dict[str, str], settings: Settings, *, limit: int = 20,
           pages: int = 2, venue_volume_for: int = 10, venue: Venue = Venue.COINBASE,
           progress: Optional[Callable[[str], None]] = None) -> list[ScreenRow]:
    """Rank coins tradable on the venue by 24h volume across all exchanges.

    ``venue_symbols`` maps base asset (e.g. 'GTC') to the venue's product id ('GTC-USD' or 'GTC').
    When several CoinGecko coins share a symbol, the one with the largest volume wins and the
    row is marked ambiguous.
    """
    rows: dict[str, ScreenRow] = {}
    seen: dict[str, int] = {}
    for coin in client.top_markets(pages):
        sym = str(coin.get("symbol", "")).upper()
        if sym not in venue_symbols:
            continue
        seen[sym] = seen.get(sym, 0) + 1
        volume = _dec(coin.get("total_volume"))
        if volume is None or volume < settings.coingecko_min_volume_usd:
            continue
        if sym in rows:  # list is volume-sorted, so the first match is the liquid one
            rows[sym].ambiguous = True
            continue
        if sym in client.overrides and client.overrides[sym] != coin.get("id"):
            continue
        rows[sym] = ScreenRow(
            symbol=sym, coin_id=str(coin.get("id")), name=str(coin.get("name", "")),
            price=_dec(coin.get("current_price")),
            change_24h_pct=_dec(coin.get("price_change_percentage_24h")),
            total_volume_usd=volume, market_cap_usd=_dec(coin.get("market_cap")),
            venue_symbol=venue_symbols[sym],
        )
    ranked = sorted(rows.values(), key=lambda r: r.total_volume_usd or 0, reverse=True)[:limit]
    for row in ranked:
        row.ambiguous = row.ambiguous or seen.get(row.symbol, 0) > 1
    if venue == Venue.COINBASE:
        for row in ranked[:venue_volume_for]:
            if progress:
                progress(row.symbol)
            try:
                row.venue_volume_usd = client.venue_volume_usd(row.coin_id, settings.coingecko_coinbase_exchange_id)
            except (requests.exceptions.RequestException, ValueError) as exc:
                log.warning("venue volume for %s unavailable: %s", row.symbol, type(exc).__name__)
    return ranked
