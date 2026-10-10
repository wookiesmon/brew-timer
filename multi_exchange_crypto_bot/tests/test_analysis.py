from datetime import timedelta
from decimal import Decimal

import pandas as pd
import pytest

from analysis import (
    MIN_CANDLES,
    analyze,
    atr,
    candles_to_frame,
    count_missing,
    drop_incomplete,
    rsi,
    swing_points,
)
from conftest import NOW, make_candles
from models import InsufficientHistory
from risk import ENTRY_WEIGHTS, staged_entries, weighted_average


def test_indicators_are_well_formed():
    df = make_candles()
    r = rsi(df["close"]).dropna()
    assert ((r >= 0) & (r <= 100)).all()
    a = atr(df).dropna()
    assert (a > 0).all()


def test_insufficient_history_is_refused():
    with pytest.raises(InsufficientHistory):
        analyze(make_candles(n=MIN_CANDLES - 1), "TEST-USD", "1h")


def test_incomplete_candle_is_dropped():
    df = make_candles(n=10)
    # The last candle opened one hour before NOW, so it is closed at NOW...
    assert len(drop_incomplete(df, "1h", NOW)) == 10
    # ...but still forming 30 minutes earlier.
    assert len(drop_incomplete(df, "1h", NOW - timedelta(minutes=30))) == 9


def test_missing_candles_and_bad_rows_are_handled():
    rows = [
        {"time": 0, "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 1},
        {"time": 3600, "open": "x", "high": 2, "low": 0.5, "close": 1.5, "volume": 1},  # unparsable -> dropped
        {"time": 7200, "open": 1, "high": 0.4, "low": 0.5, "close": 1.5, "volume": 1},  # high < low -> dropped
        {"time": 3 * 3600, "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": None},
        {"time": 3 * 3600, "open": 1, "high": 2, "low": 0.5, "close": 1.6, "volume": 2},  # duplicate time
    ]
    df = candles_to_frame(rows)
    assert len(df) == 2
    assert df["close"].iloc[-1] == 1.6
    assert count_missing(df, "1h") == 2


def test_swing_points_never_use_unconfirmed_candles():
    df = make_candles(n=120)
    spiked = df.copy()
    spiked.iloc[-1, spiked.columns.get_loc("high")] = 10_000.0  # newest candle cannot be confirmed yet
    highs, _ = swing_points(spiked, window=3)
    assert 10_000.0 not in highs


def test_analysis_outputs_levels():
    a = analyze(make_candles(), "TEST-USD", "1h")
    assert a.atr > 0 and a.candle_count == 300
    assert all(z.high < a.last_close for z in a.supports)
    assert all(z.low > a.last_close for z in a.resistances)
    assert a.change_24h_pct is not None


def test_extended_market_is_flagged():
    df = make_candles()
    last = df.index[-1]
    spike = pd.DataFrame(
        {"open": [df["close"].iloc[-1]], "high": [140.0], "low": [df["close"].iloc[-1]], "close": [139.0],
         "volume": [1000.0]}, index=[last + pd.Timedelta(hours=1)])
    a = analyze(pd.concat([df, spike]), "TEST-USD", "1h")
    assert a.extended
    assert "Market is extended; no automatic market entry will be created." in a.flags


def test_illiquid_market_is_flagged():
    df = make_candles()
    df.loc[df.index[-60:], "volume"] = 0.0
    assert analyze(df, "TEST-USD", "1h").illiquid


def test_staged_entries_and_weighted_average():
    entries = staged_entries(Decimal("100"), Decimal("2"))
    assert entries == [Decimal("99.0"), Decimal("98.0"), Decimal("97.0")]
    avg = weighted_average(entries, list(ENTRY_WEIGHTS))
    assert avg == Decimal("98.15")
