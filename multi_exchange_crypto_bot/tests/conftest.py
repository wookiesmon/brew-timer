"""Shared fixtures: synthetic candles, market metadata, settings and a fake adapter."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from analysis import MarketAnalysis, Zone, candles_to_frame
from config import Settings
from models import ExchangeOrder, MarketMeta, OrderStatus, Venue

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_candles(n: int = 300, start: float = 100.0, seed: int = 7, volume: float = 1000.0,
                 end: datetime = NOW) -> pd.DataFrame:
    """Mean-reverting synthetic hourly candles that close just before ``end``."""
    rng = np.random.default_rng(seed)
    t0 = int(end.timestamp()) - n * 3600
    rows, price = [], start
    for i in range(n):
        o = price
        c = o + 0.15 * (start - o) + rng.normal(0, 0.8)
        h = max(o, c) + abs(rng.normal(0, 0.4))
        l = min(o, c) - abs(rng.normal(0, 0.4))
        rows.append({"time": t0 + i * 3600, "open": o, "high": h, "low": l, "close": c, "volume": volume})
        price = c
    return candles_to_frame(rows)


def fake_analysis(price: float = 100.0, atr: float = 2.0, resistances=None, **over) -> MarketAnalysis:
    fields = dict(
        symbol="TEST-USD", interval="1h", candle_count=300, missing_candles=0, first_time=NOW, last_time=NOW,
        last_close=price, change_lookback_pct=0.0, change_24h_pct=0.0, high=price * 1.1, low=price * 0.9,
        atr=atr, ema20=price, ema50=price, ema200=price, rsi=50.0, volatility_per_candle_pct=1.0,
        volatility_annualized_pct=90.0, avg_volume=1000.0, volume_ratio=1.0, supports=[],
        resistances=resistances or [], extended=False, illiquid=False,
    )
    fields.update(over)
    return MarketAnalysis(**fields)


def cb_meta(**over) -> MarketMeta:
    fields = dict(
        venue=Venue.COINBASE, symbol="TEST-USD", base_asset="TEST", quote_asset="USD", product_type="SPOT",
        tradable=True, status_detail="online", size_increment=Decimal("0.01"), min_size=Decimal("0.01"),
        min_notional=Decimal("1"), price_increment=Decimal("0.0001"), last_price=Decimal("100"),
    )
    fields.update(over)
    return MarketMeta(**fields)


def hl_meta(**over) -> MarketMeta:
    fields = dict(
        venue=Venue.HYPERLIQUID, symbol="TEST", base_asset="TEST", quote_asset="USDC", product_type="PERP",
        tradable=True, status_detail="active", size_increment=Decimal("0.01"), min_size=Decimal("0.01"),
        min_notional=Decimal("10"), price_increment=None, sz_decimals=2, max_leverage=10, only_isolated=False,
        last_price=Decimal("100"), mark_price=Decimal("100"),
    )
    fields.update(over)
    return MarketMeta(**fields)


def make_settings(tmp_path: Path, **over) -> Settings:
    fields = dict(database_path=tmp_path / "bot.sqlite3", stop_file=tmp_path / "STOP")
    fields.update(over)
    return Settings(**fields)


def bar(ts: datetime, o, h, l, c, v=1000) -> dict:
    return {"time": ts, "open": Decimal(str(o)), "high": Decimal(str(h)), "low": Decimal(str(l)),
            "close": Decimal(str(c)), "volume": Decimal(str(v))}


class FakeAdapter:
    """Market data from a DataFrame; records every order call."""

    exits_share_balance = True

    def __init__(self, meta: MarketMeta, df: pd.DataFrame):
        self.meta = meta
        self.venue = meta.venue
        self.df = df
        self.placed: list[tuple] = []

    def get_market_meta(self):
        return self.meta

    def get_candles(self, interval, count, now=None):
        return self.df.tail(count)

    def _record(self, kind, *args):
        self.placed.append((kind, *args))
        return f"X{len(self.placed)}"

    def place_limit_buy(self, cid, qty, price):
        return self._record("buy", cid, qty, price)

    def place_limit_sell(self, cid, qty, price, reduce_only):
        return self._record("sell", cid, qty, price)

    def place_stop_limit_sell(self, cid, qty, trigger, limit, reduce_only):
        return self._record("stop", cid, qty, trigger, limit)

    def get_order(self, cid, exid):
        return ExchangeOrder(client_order_id=cid, exchange_order_id=exid or "X?", status=OrderStatus.OPEN)

    def list_open_orders(self):
        return []

    def cancel_orders(self, ids):
        return {i: True for i in ids}

    def available_position(self):
        return Decimal(0)

    def available_quote(self):
        return Decimal(100000)

    # pre-flight helpers used by --live/--preview/--check
    permissions = {"can_view": True, "can_trade": True, "can_transfer": False}

    def key_permissions(self):
        return dict(self.permissions)

    def check_key_permissions(self):
        from models import LiveTradingDisabled

        if not self.permissions.get("can_trade") or self.permissions.get("can_transfer"):
            raise LiveTradingDisabled("key permissions not trade-only")

    def preview_limit_buy(self, quantity, price):
        self.placed_previews = getattr(self, "placed_previews", 0) + 1
        return {"errors": [], "warnings": [], "order_total": str(quantity * price), "commission_total": "0"}


@pytest.fixture
def settings(tmp_path):
    return make_settings(tmp_path)


__all__ = ["NOW", "make_candles", "fake_analysis", "cb_meta", "hl_meta", "make_settings", "bar", "FakeAdapter",
           "Zone", "timedelta"]
