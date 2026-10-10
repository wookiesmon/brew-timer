"""Trend filter, breakeven / trailing stops, backtest statistics and the compare mode."""
from decimal import Decimal

import pytest

import cli
from conftest import NOW, FakeAdapter, cb_meta, fake_analysis, make_candles, make_settings
from metrics import max_drawdown, merge, trade_stats
from models import OrderRole, OrderType, Venue
from risk import build_plan, risk_inputs_from_settings, trend_filter_reasons
from test_safety import H, Harness


# ------------------------------------------------------------------ metrics
def test_trade_stats():
    s = trade_stats([Decimal(10), Decimal(-5), Decimal(-5), Decimal(20)], [Decimal(1)] * 4)
    assert (s.trades, s.wins, s.losses) == (4, 2, 2)
    assert s.net_pnl == 20 and s.profit_factor == 3 and s.expectancy == 5 and s.fees == 4
    assert s.win_rate == 50 and s.avg_win == 15 and s.avg_loss == -5
    assert not s.enough_trades
    assert trade_stats([]).profit_factor is None and trade_stats([]).expectancy is None
    assert merge([s, s]).net_pnl == 40


def test_max_drawdown():
    dd, pct = max_drawdown([Decimal(x) for x in (100, 120, 90, 130, 110)])
    assert dd == 30 and pct == 25


# ------------------------------------------------------------- trend filter
@pytest.mark.parametrize("mode,ema20,ema50,ema200,close,blocked", [
    ("off", 90, 100, 120, 80, False),
    ("ema", 101, 100, None, 100, False),
    ("ema", 99, 100, None, 100, True),
    ("ema200", 101, 100, 95, 100, False),
    ("ema200", 101, 100, 105, 100, True),
    ("ema200", 101, 100, None, 100, True),
])
def test_trend_filter(mode, ema20, ema50, ema200, close, blocked):
    analysis = fake_analysis(price=close, ema20=ema20, ema50=ema50, ema200=ema200)
    assert bool(trend_filter_reasons(analysis, mode)) == blocked


def test_trend_filter_refuses_plan(tmp_path):
    settings = make_settings(tmp_path, trend_filter="ema")
    plan = build_plan(fake_analysis(ema20=95.0, ema50=100.0), cb_meta(),
                      risk_inputs_from_settings(settings, Venue.COINBASE), NOW)
    assert plan.refused and any("Trend filter" in r for r in plan.refusal_reasons)


def test_invalid_trend_filter(tmp_path):
    with pytest.raises(ValueError):
        make_settings(tmp_path, trend_filter="vibes")


# ----------------------------------------------------- breakeven / trailing
def _reach_tp1(h):
    h.step(100, NOW)
    h.candle(NOW, 100, 100.5, 96.5, 98)  # all entries fill
    h.step(98, NOW + H)
    tp1 = h.plan.take_profits[0]
    h.step(tp1 + Decimal("0.05"), NOW + 2 * H)  # Coinbase: TP1 placed once price reaches it
    h.candle(NOW + 2 * H, tp1, tp1 + 1, tp1 - Decimal("0.1"), tp1 + Decimal("0.5"))  # TP1 fills
    return tp1


def test_breakeven_stop_after_tp1(tmp_path):
    h = Harness(tmp_path, breakeven_after_tp1=True, max_daily_loss_usd=Decimal("1000"))
    tp1 = _reach_tp1(h)
    h.step(tp1 + Decimal("0.5"), NOW + 3 * H)
    stop = h.orders(OrderRole.STOP, open_only=True)[0]
    _, avg_cost = h.db.position(h.run_id)
    assert stop.order_type == OrderType.STOP_LIMIT
    assert stop.trigger_price >= avg_cost > h.plan.stop_trigger
    assert stop.quantity == h.db.position(h.run_id)[0]


def test_without_breakeven_stop_stays_put(tmp_path):
    h = Harness(tmp_path, max_daily_loss_usd=Decimal("1000"))
    tp1 = _reach_tp1(h)
    h.step(tp1 + Decimal("0.5"), NOW + 3 * H)
    assert h.orders(OrderRole.STOP, open_only=True)[0].trigger_price == h.plan.stop_trigger


def test_trailing_stop_only_moves_up_and_replaces_tp3(tmp_path):
    h = Harness(tmp_path, breakeven_after_tp1=True, trail_atr_multiple=Decimal("1"),
                max_daily_loss_usd=Decimal("1000"))
    tp1 = _reach_tp1(h)
    h.step(tp1 + 5, NOW + 3 * H)  # new high: trail = high - 1 ATR (2.0)
    high_stop = h.orders(OrderRole.STOP, open_only=True)[0].trigger_price
    assert high_stop == tp1 + 5 - 2
    h.step(tp1 + 4, NOW + 4 * H)  # price dips but stays above the stop: no lowering
    assert h.orders(OrderRole.STOP, open_only=True)[0].trigger_price == high_stop
    assert not [o for o in h.orders(OrderRole.TAKE_PROFIT) if o.leg == "TP3"]


# ---------------------------------------------------------------- compare
def test_backtest_compare_and_products(tmp_path, monkeypatch, capsys):
    settings = make_settings(tmp_path)
    frames = {"A-USD": make_candles(n=260, seed=1), "B-USD": make_candles(n=260, seed=2)}
    monkeypatch.setattr(cli, "make_adapter", lambda venue, product, s, authenticated: FakeAdapter(
        cb_meta(symbol=product, price_increment=Decimal("0.01")), frames[product]))
    monkeypatch.setattr(cli, "COMPARE_GRID", cli.COMPARE_GRID[:2])
    code = cli.main(["--venue", "coinbase", "--backtest", "--products", "A-USD,B-USD", "--compare",
                     "--fee-pct", "1.2,0.045", "--candles", "260"], settings=settings)
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "Comparison across A-USD, B-USD" in out
    assert out.count("fee=1.2%") >= 2 and out.count("fee=0.045%") >= 2
    assert "OOS PF" in out


def test_single_backtest_report(tmp_path, monkeypatch, capsys):
    settings = make_settings(tmp_path)
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: FakeAdapter(
        cb_meta(price_increment=Decimal("0.01")), make_candles(n=300)))
    assert cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--backtest"], settings=settings) == cli.EXIT_OK
    out = capsys.readouterr().out
    assert "profit factor" in out and "buy & hold" in out and "out-of-sample" in out
