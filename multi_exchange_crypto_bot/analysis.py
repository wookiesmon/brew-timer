"""Rule-based market analysis from historical candles only.

Nothing here predicts prices. Every level is derived from closed candles with a
documented rule, so the output can be reproduced by hand.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from models import InsufficientHistory

INTERVAL_SECONDS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "2h": 7200, "1d": 86400}
MIN_CANDLES = 100  # EMA(50) and swing detection need a meaningful warm-up
TARGET_CANDLES = 300
SWING_WINDOW = 3
CONSOLIDATION_LOOKBACK = 24
EXTENDED_ATR_MULTIPLE = 2.0
ILLIQUID_VOLUME_RATIO = 0.10
ZERO_VOLUME_MAX_FRACTION = 0.20


@dataclass(frozen=True)
class Zone:
    low: float
    high: float
    touches: int
    source: str

    @property
    def mid(self) -> float:
        return (self.low + self.high) / 2


@dataclass
class MarketAnalysis:
    symbol: str
    interval: str
    candle_count: int
    missing_candles: int
    first_time: datetime
    last_time: datetime
    last_close: float
    change_lookback_pct: float
    change_24h_pct: Optional[float]
    high: float
    low: float
    atr: float
    ema20: float
    ema50: float
    rsi: float
    volatility_per_candle_pct: float
    volatility_annualized_pct: float
    avg_volume: float
    volume_ratio: float
    supports: list[Zone]
    resistances: list[Zone]
    extended: bool
    illiquid: bool
    score: dict[str, int] = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)


# ----------------------------------------------------------------- data prep
def candles_to_frame(rows: Iterable[dict]) -> pd.DataFrame:
    """Normalise rows with keys time (unix seconds), open, high, low, close, volume."""
    df = pd.DataFrame(list(rows))
    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    required = {"time", "open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"candles missing columns {sorted(missing)}")
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["time"] = pd.to_datetime(pd.to_numeric(df["time"], errors="coerce"), unit="s", utc=True)
    df = df.dropna(subset=["time", "open", "high", "low", "close"])
    df["volume"] = df["volume"].fillna(0.0)
    df = df[(df["high"] >= df["low"]) & (df["close"] > 0)]
    df = df.drop_duplicates(subset="time", keep="last").sort_values("time").set_index("time")
    return df[["open", "high", "low", "close", "volume"]]


def drop_incomplete(df: pd.DataFrame, interval: str, now: datetime) -> pd.DataFrame:
    """Remove the still-forming candle so no partial (future-dependent) data is used."""
    if df.empty:
        return df
    seconds = INTERVAL_SECONDS[interval]
    now_ts = pd.Timestamp(now.astimezone(timezone.utc))
    closes = df.index + pd.Timedelta(seconds=seconds)
    return df[closes <= now_ts]


def count_missing(df: pd.DataFrame, interval: str) -> int:
    if len(df) < 2:
        return 0
    seconds = INTERVAL_SECONDS[interval]
    span = (df.index[-1] - df.index[0]).total_seconds()
    expected = int(span // seconds) + 1
    return max(expected - len(df), 0)


# ---------------------------------------------------------------- indicators
def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100 - 100 / (1 + rs)
    out = out.where(avg_loss != 0, 100.0)
    return out.where(avg_gain.notna())


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Wilder's Average True Range."""
    prev_close = df["close"].shift(1)
    true_range = pd.concat(
        [df["high"] - df["low"], (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()], axis=1
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def swing_points(df: pd.DataFrame, window: int = SWING_WINDOW) -> tuple[list[float], list[float]]:
    """Fractal swing highs/lows. A swing at i is confirmed by ``window`` later candles,
    all of which are already closed, so no future data is used."""
    highs, lows = df["high"].to_numpy(), df["low"].to_numpy()
    swing_highs, swing_lows = [], []
    for i in range(window, len(df) - window):
        lo, hi = i - window, i + window + 1
        if highs[i] == highs[lo:hi].max():
            swing_highs.append(float(highs[i]))
        if lows[i] == lows[lo:hi].min():
            swing_lows.append(float(lows[i]))
    return swing_highs, swing_lows


def cluster_levels(levels: list[tuple[float, str]], tolerance: float) -> list[Zone]:
    """Group nearby levels into zones; more touches = more meaningful."""
    zones: list[Zone] = []
    for value, source in sorted(levels):
        if zones and value - zones[-1].high <= tolerance:
            last = zones[-1]
            sources = last.source if source in last.source.split("+") else f"{last.source}+{source}"
            zones[-1] = Zone(low=last.low, high=value, touches=last.touches + 1, source=sources)
        else:
            zones.append(Zone(low=value, high=value, touches=1, source=source))
    return zones


# ------------------------------------------------------------------- analyze
def analyze(
    df: pd.DataFrame, symbol: str, interval: str, change_24h_pct: Optional[float] = None,
    lookback: int = TARGET_CANDLES,
) -> MarketAnalysis:
    if interval not in INTERVAL_SECONDS:
        raise ValueError(f"unsupported interval {interval}")
    df = df.tail(lookback)
    if len(df) < MIN_CANDLES:
        raise InsufficientHistory(
            f"{symbol}: {len(df)} closed candles available, at least {MIN_CANDLES} required"
        )

    close = df["close"]
    atr_series = atr(df)
    ema20_series = ema(close, 20)
    ema50_series = ema(close, 50)
    rsi_series = rsi(close)
    last_close = float(close.iloc[-1])
    last_atr = float(atr_series.iloc[-1])
    last_ema20 = float(ema20_series.iloc[-1])
    last_ema50 = float(ema50_series.iloc[-1])
    last_rsi = float(rsi_series.iloc[-1])
    if not all(np.isfinite([last_atr, last_ema20, last_ema50, last_rsi])) or last_atr <= 0:
        raise InsufficientHistory(f"{symbol}: indicators could not be computed from the available candles")

    seconds = INTERVAL_SECONDS[interval]
    log_returns = np.log(close / close.shift(1)).dropna()
    vol_per_candle = float(log_returns.tail(50).std()) if len(log_returns) > 2 else 0.0
    periods_per_year = 365 * 86400 / seconds
    vol_annual = vol_per_candle * float(np.sqrt(periods_per_year))

    volume = df["volume"]
    avg_volume = float(volume.tail(50).mean())
    recent_volume = float(volume.tail(5).mean())
    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0.0
    zero_volume_fraction = float((volume.tail(50) <= 0).mean())

    if change_24h_pct is None:
        per_day = max(int(86400 // seconds), 1)
        if len(close) > per_day:
            change_24h_pct = (last_close / float(close.iloc[-1 - per_day]) - 1) * 100

    swing_highs, swing_lows = swing_points(df)
    recent = df.tail(CONSOLIDATION_LOOKBACK)
    support_levels = [(v, "swing_low") for v in swing_lows if v < last_close]
    resistance_levels = [(v, "swing_high") for v in swing_highs if v > last_close]
    if float(recent["high"].max() - recent["low"].min()) <= 3 * last_atr:
        support_levels.append((float(recent["low"].min()), "consolidation_low"))
        resistance_levels.append((float(recent["high"].max()), "consolidation_high"))
    for k in (1.0, 2.0):
        if last_close - k * last_atr > 0:
            support_levels.append((last_close - k * last_atr, f"atr_{k:g}"))
        resistance_levels.append((last_close + k * last_atr, f"atr_{k:g}"))
    tolerance = 0.5 * last_atr
    supports = sorted(cluster_levels(support_levels, tolerance), key=lambda z: -z.high)
    resistances = sorted(
        (z for z in cluster_levels(resistance_levels, tolerance) if z.low > last_close),
        key=lambda z: z.low,
    )

    extended = last_close > last_ema20 + EXTENDED_ATR_MULTIPLE * last_atr
    illiquid = avg_volume <= 0 or volume_ratio < ILLIQUID_VOLUME_RATIO or zero_volume_fraction > ZERO_VOLUME_MAX_FRACTION

    # Transparent, informational score (0/1 per rule). It never forces a trade.
    score = {
        "trend_ema20_above_ema50": int(last_ema20 > last_ema50),
        "rsi_between_35_and_65": int(35 <= last_rsi <= 65),
        "not_extended_vs_ema20": int(not extended),
        "volume_ratio_at_least_0_5": int(volume_ratio >= 0.5),
        "atr_below_10pct_of_price": int(last_atr < 0.10 * last_close),
    }
    flags = []
    if extended:
        flags.append("Market is extended; no automatic market entry will be created.")
    if illiquid:
        flags.append("Market looks illiquid (low or missing volume); no entry plan will be created.")
    missing = count_missing(df, interval)
    if missing:
        flags.append(f"{missing} candle(s) missing from the series (exchange had no trades or data gap).")
    if len(df) < TARGET_CANDLES * 2 // 3:
        flags.append(f"Only {len(df)} candles available; levels are less reliable.")

    return MarketAnalysis(
        symbol=symbol,
        interval=interval,
        candle_count=len(df),
        missing_candles=missing,
        first_time=df.index[0].to_pydatetime(),
        last_time=df.index[-1].to_pydatetime(),
        last_close=last_close,
        change_lookback_pct=(last_close / float(close.iloc[0]) - 1) * 100,
        change_24h_pct=change_24h_pct,
        high=float(df["high"].max()),
        low=float(df["low"].min()),
        atr=last_atr,
        ema20=last_ema20,
        ema50=last_ema50,
        rsi=last_rsi,
        volatility_per_candle_pct=vol_per_candle * 100,
        volatility_annualized_pct=vol_annual * 100,
        avg_volume=avg_volume,
        volume_ratio=volume_ratio,
        supports=supports,
        resistances=resistances,
        extended=extended,
        illiquid=illiquid,
        score=score,
        flags=flags,
    )
