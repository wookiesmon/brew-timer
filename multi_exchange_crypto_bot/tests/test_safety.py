import logging
from datetime import timedelta
from decimal import Decimal

import pytest
import requests

import cli
import coinbase_adapter
import hyperliquid_adapter
from conftest import NOW, FakeAdapter, bar, cb_meta, fake_analysis, hl_meta, make_candles, make_settings
from database import Database
from execution import TradingEngine, create_run, run_backtest
from models import (
    FatalRiskError,
    InvalidMetadata,
    KillSwitchTriggered,
    LiveTradingDisabled,
    MarketUnavailable,
    Mode,
    OrderRejected,
    OrderRole,
    OrderStatus,
    Venue,
)
from risk import build_plan, risk_inputs_from_settings
from simulator import SimulatedExchange

H = timedelta(hours=1)


# ------------------------------------------------------------------ harness
class Harness:
    def __init__(self, tmp_path, venue=Venue.COINBASE, sim_cls=SimulatedExchange, **settings_over):
        self.settings = make_settings(tmp_path, **settings_over)
        self.meta = cb_meta() if venue == Venue.COINBASE else hl_meta()
        self.db = Database(":memory:")
        self.clock = {"now": NOW}
        inputs = risk_inputs_from_settings(self.settings, venue)
        self.plan = build_plan(fake_analysis(), self.meta, inputs, NOW)
        assert not self.plan.refused, self.plan.refusal_reasons
        self.sim = sim_cls(
            self.db, venue, self.meta.symbol, starting_quote=Decimal("2000"), fee_pct=inputs.fee_pct,
            participation_pct=self.settings.sim_volume_participation_pct, size_increment=self.meta.size_increment,
            clock=lambda: self.clock["now"],
        )
        self.run_id = create_run(self.db, self.plan, Mode.PAPER, NOW, run_id="t1")
        self.engine = self.new_engine()

    def new_engine(self):
        return TradingEngine(db=self.db, gateway=self.sim, meta=self.meta, settings=self.settings,
                             mode=Mode.PAPER, run_id=self.run_id)

    def step(self, price, at):
        self.clock["now"] = at
        return self.engine.step(Decimal(str(price)), at)

    def candle(self, at, o, h, l, c, v=1000):
        return self.sim.process_candle(bar(at, o, h, l, c, v))

    def orders(self, role=None, open_only=False):
        return [o for o in self.db.orders_for_run(self.run_id, open_only=open_only) if role is None or o.role == role]

    def fill_all_entries(self):
        self.step(100, NOW)
        self.candle(NOW, 100, 100.5, 96.5, 98)  # trades through all three entries
        return self.step(98, NOW + H)


# --------------------------------------------------------- duplicate orders
def test_duplicate_order_prevention_across_steps_and_restarts(tmp_path):
    h = Harness(tmp_path)
    h.step(100, NOW)
    h.step(100, NOW + timedelta(minutes=1))
    assert len(h.orders(OrderRole.ENTRY)) == 3
    h.engine = h.new_engine()  # simulated process restart: state comes from SQLite
    h.step(100, NOW + timedelta(minutes=2))
    assert len(h.orders(OrderRole.ENTRY)) == 3
    assert len(h.sim.list_open_orders()) == 3
    with pytest.raises(Exception):  # the UNIQUE constraint backs this up at the storage layer
        h.db.conn.execute("INSERT INTO orders (venue, product, mode, run_id, client_order_id, leg, role, order_type,"
                          " side, price, quantity, status, created_at, updated_at) SELECT venue, product, mode, run_id,"
                          " client_order_id, leg, role, order_type, side, price, quantity, status, created_at,"
                          " updated_at FROM orders LIMIT 1")


class TimeoutAfterAccept(SimulatedExchange):
    """Accepts the order, then raises as if the response was lost."""

    failed = False

    def place_limit_buy(self, client_order_id, quantity, price):
        oid = super().place_limit_buy(client_order_id, quantity, price)
        if not TimeoutAfterAccept.failed:
            TimeoutAfterAccept.failed = True
            raise requests.exceptions.ReadTimeout("lost response")
        return oid


def test_unknown_submission_is_looked_up_not_resent(tmp_path):
    TimeoutAfterAccept.failed = False
    h = Harness(tmp_path, sim_cls=TimeoutAfterAccept, api_error_cooldown_seconds=60)
    h.step(100, NOW)
    e1 = [o for o in h.orders() if o.leg == "E1"][0]
    assert e1.status == OrderStatus.SUBMIT_UNKNOWN
    assert len(h.orders(OrderRole.ENTRY)) == 1  # cooldown stopped further submissions
    h.step(100, NOW + timedelta(minutes=5))
    e1 = [o for o in h.orders() if o.leg == "E1"][0]
    assert e1.status == OrderStatus.OPEN and e1.exchange_order_id
    assert len(h.orders(OrderRole.ENTRY)) == 3
    assert len(h.sim.list_open_orders()) == 3  # E1 exists exactly once on the "exchange"


# ------------------------------------------------------------- partial fills
def test_partial_fills_size_the_stop_to_the_filled_quantity(tmp_path):
    h = Harness(tmp_path, sim_volume_participation_pct=Decimal("20"))
    h.step(100, NOW)
    h.candle(NOW, 100, 100, 98.9, 99, v=2)  # budget 0.4 of E1's 0.81
    h.step(99, NOW + H)
    e1 = [o for o in h.orders() if o.leg == "E1"][0]
    assert e1.filled_quantity == Decimal("0.4") and e1.status == OrderStatus.OPEN
    stops = h.orders(OrderRole.STOP, open_only=True)
    assert len(stops) == 1 and stops[0].quantity == Decimal("0.4")

    h.candle(NOW + H, 99, 99, 98.9, 99, v=2)
    h.step(99, NOW + 2 * H)
    stops = h.orders(OrderRole.STOP, open_only=True)
    assert len(stops) == 1 and stops[0].quantity == Decimal("0.8")
    assert [o.status for o in h.orders(OrderRole.STOP)] == [OrderStatus.CANCELLED, OrderStatus.OPEN]
    position, _ = h.db.position(h.run_id)
    assert position == Decimal("0.8")


def test_exits_never_exceed_position_on_coinbase(tmp_path):
    h = Harness(tmp_path)
    h.fill_all_entries()
    position, _ = h.db.position(h.run_id)
    assert position == Decimal("2.03")
    stop = h.orders(OrderRole.STOP, open_only=True)[0]
    assert stop.quantity == position
    assert stop.trigger_price == h.plan.stop_trigger and stop.price == h.plan.stop_limit
    assert not h.orders(OrderRole.TAKE_PROFIT)  # TPs wait until price reaches them (balance holds)

    tp1 = h.plan.take_profits[0]
    h.step(tp1 + Decimal("0.01"), NOW + 2 * H)
    open_sells = [o for o in h.orders(open_only=True) if o.role != OrderRole.ENTRY]
    assert sum(o.remaining for o in open_sells) <= position
    assert {o.leg for o in open_sells} == {"TP1", "SL"}
    assert [o for o in open_sells if o.leg == "TP1"][0].quantity == Decimal("0.81")
    assert [o for o in open_sells if o.leg == "SL"][0].quantity == Decimal("1.22")


def test_hyperliquid_exits_are_reduce_only_and_rest_together(tmp_path):
    h = Harness(tmp_path, venue=Venue.HYPERLIQUID)
    h.fill_all_entries()
    rows = h.db.conn.execute("SELECT * FROM sim_orders WHERE side = 'SELL' AND status = 'OPEN'").fetchall()
    assert len(rows) == 4 and all(r["reduce_only"] for r in rows)  # SL + TP1..TP3
    stop = h.orders(OrderRole.STOP, open_only=True)[0]
    assert stop.quantity == h.db.position(h.run_id)[0]


def test_stop_limit_can_fail_to_fill_on_a_gap(tmp_path):
    h = Harness(tmp_path)
    h.fill_all_entries()
    h.candle(NOW + H, 94, 94.5, 90, 91)  # opens below the 95.5 limit
    h.step(91, NOW + 2 * H)
    stop = h.orders(OrderRole.STOP)[-1]
    assert stop.status == OrderStatus.OPEN and stop.filled_quantity == 0


def test_run_closes_after_stop_fills(tmp_path):
    h = Harness(tmp_path, max_daily_loss_usd=Decimal("1000"))
    h.fill_all_entries()
    h.candle(NOW + H, 97.5, 97.6, 95.8, 96)
    report = h.step(96, NOW + 2 * H)
    assert report.status == "CLOSED" and report.position == 0 and report.realized < 0


# -------------------------------------------------------- kill switch / halt
def test_stop_file_cancels_orders_and_exits(tmp_path):
    h = Harness(tmp_path)
    h.step(100, NOW)
    assert len(h.sim.list_open_orders()) == 3
    (tmp_path / "STOP").write_text("")
    with pytest.raises(KillSwitchTriggered):
        h.step(100, NOW + H)
    assert h.sim.list_open_orders() == []
    assert h.db.get_run(h.run_id)["status"] == "KILLED"


def test_daily_loss_shutdown_keeps_the_stop_and_persists(tmp_path):
    h = Harness(tmp_path, max_daily_loss_usd=Decimal("5"))
    h.step(100, NOW)
    h.candle(NOW, 100, 100.5, 98.5, 99)  # only E1 fills
    h.step(99, NOW + H)
    with pytest.raises(FatalRiskError):
        h.step(90, NOW + 2 * H)  # mark-to-market loss beyond $5
    assert not h.orders(OrderRole.ENTRY, open_only=True)
    assert len(h.orders(OrderRole.STOP, open_only=True)) == 1  # protection is not removed
    assert h.db.halt_reason("coinbase", "paper")
    h.engine = h.new_engine()
    with pytest.raises(FatalRiskError):  # no automatic restart
        h.step(99, NOW + 3 * H)


def test_max_open_orders_is_enforced(tmp_path):
    h = Harness(tmp_path, max_open_orders=2)
    report = h.step(100, NOW)
    assert len(h.orders(OrderRole.ENTRY)) == 2
    assert any("MAX_OPEN_ORDERS" in m for m in report.messages)


# --------------------------------------------------------------- dry run / CLI
class NoOrders(FakeAdapter):
    def _record(self, *args):
        raise AssertionError("an order endpoint was called")


def test_paper_mode_never_submits_orders(tmp_path, monkeypatch):
    settings = make_settings(tmp_path)
    fake = NoOrders(cb_meta(), make_candles())
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: fake)
    code = cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--paper", "--once"], settings=settings)
    assert code == cli.EXIT_OK
    db = Database(settings.paper_database_path)
    run = db.active_run("coinbase", "TEST-USD", "paper")
    assert run is not None and len(db.orders_for_run(run["run_id"])) == 3  # simulated, not sent
    assert not settings.database_path.exists() or not Database(settings.database_path).runs("coinbase", "TEST-USD", "live")


def test_live_rejected_without_flags(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no adapter")))
    for over in ({}, {"coinbase_live_trading": True}, {"dry_run": False}):
        settings = make_settings(tmp_path, **over)
        assert cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--live"], settings=settings) == cli.EXIT_REFUSED


def test_live_rejected_while_kill_switch_present(tmp_path):
    settings = make_settings(tmp_path, coinbase_live_trading=True, dry_run=False)
    (tmp_path / "STOP").write_text("")
    with pytest.raises(LiveTradingDisabled):
        cli.check_live_gates(settings, Venue.COINBASE)


@pytest.mark.parametrize("typed,expected_orders", [("confirm_live", 0), ("", 0), ("CONFIRM_LIVE", 3)])
def test_live_requires_exact_confirmation(tmp_path, monkeypatch, typed, expected_orders):
    settings = make_settings(tmp_path, coinbase_live_trading=True, dry_run=False)
    fake = FakeAdapter(cb_meta(), make_candles())
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: fake)
    prompts = []

    def answer(prompt):
        prompts.append(prompt)
        return typed

    code = cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--live", "--once"],
                    input_fn=answer, settings=settings)
    assert "Type CONFIRM_LIVE to enable live trading: " in prompts
    assert len([p for p in fake.placed if p[0] == "buy"]) == expected_orders
    assert code == (cli.EXIT_OK if expected_orders else cli.EXIT_REFUSED)


def test_unsupported_hyperliquid_market_message(tmp_path, monkeypatch, capsys):
    meta = [{"universe": [{"name": "BTC", "szDecimals": 5, "maxLeverage": 40}]}, [{"markPx": "1"}]]

    class Info:
        def meta_and_asset_ctxs(self):
            return meta

    settings = make_settings(tmp_path)
    monkeypatch.setattr(cli, "make_adapter", lambda venue, product, s, authenticated: hyperliquid_adapter.HyperliquidAdapter(
        s, product, authenticated=False, info=Info()))
    code = cli.main(["--venue", "hyperliquid", "--product", "GTC", "--analyze"], settings=settings)
    assert code == cli.EXIT_UNAVAILABLE
    assert "GTC is unavailable on Hyperliquid; no order will be submitted." in capsys.readouterr().out


# ------------------------------------------------------------ venue adapters
def test_unsupported_coinbase_products(tmp_path):
    with pytest.raises(MarketUnavailable):
        coinbase_adapter.parse_product({"product_id": "BIT-31OCT26-CDE", "product_type": "FUTURE"})
    offline = coinbase_adapter.parse_product({
        "product_id": "OLD-USD", "product_type": "SPOT", "status": "delisted", "trading_disabled": True,
        "base_increment": "0.01", "base_min_size": "0.01", "quote_min_size": "1", "price_increment": "0.01"})
    with pytest.raises(MarketUnavailable):
        offline.validate()
    with pytest.raises(MarketUnavailable):
        cli.make_adapter(Venue.COINBASE, "GTC", make_settings(tmp_path), authenticated=False)

    class Client:
        def get_public_product(self, product_id):
            response = requests.Response()
            response.status_code = 404
            raise requests.exceptions.HTTPError("404", response=response)

    adapter = coinbase_adapter.CoinbaseAdapter(make_settings(tmp_path), "NOPE-USD", authenticated=False, client=Client())
    with pytest.raises(MarketUnavailable):
        adapter.get_market_meta()


def test_coinbase_missing_precision_is_invalid():
    with pytest.raises(InvalidMetadata):
        coinbase_adapter.parse_product({"product_id": "GTC-USD", "product_type": "SPOT", "status": "online",
                                        "base_min_size": "0.01", "quote_min_size": "1", "price_increment": "0.001"})


def test_coinbase_stop_limit_uses_stop_down_direction(tmp_path):
    calls = {}

    class Client:
        def stop_limit_order_gtc_sell(self, **kwargs):
            calls.update(kwargs)
            return {"success": True, "success_response": {"order_id": "abc"}}

    adapter = coinbase_adapter.CoinbaseAdapter(make_settings(tmp_path), "GTC-USD", authenticated=True, client=Client())
    assert adapter.place_stop_limit_sell("cid", Decimal("1.5"), Decimal("0.14"), Decimal("0.139"), False) == "abc"
    assert calls["stop_direction"] == "STOP_DIRECTION_STOP_DOWN"
    assert calls["stop_price"] == "0.14" and calls["limit_price"] == "0.139" and calls["base_size"] == "1.5"
    assert "leverage" not in calls and "margin_type" not in calls  # spot only


def test_coinbase_rejection_is_reported(tmp_path):
    class Client:
        def limit_order_gtc_buy(self, **kwargs):
            return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND", "message": "no"}}

    adapter = coinbase_adapter.CoinbaseAdapter(make_settings(tmp_path), "GTC-USD", authenticated=True, client=Client())
    with pytest.raises(OrderRejected, match="INSUFFICIENT_FUND"):
        adapter.place_limit_buy("cid", Decimal("1"), Decimal("0.1"))


class FakeHLExchange:
    def __init__(self):
        self.calls = []

    def order(self, name, is_buy, sz, limit_px, order_type, reduce_only=False, cloid=None):
        self.calls.append(("order", name, is_buy, sz, limit_px, order_type, reduce_only, str(cloid)))
        return {"status": "ok", "response": {"type": "order", "data": {"statuses": [{"resting": {"oid": 42}}]}}}

    def update_leverage(self, leverage, name, is_cross=True):
        self.calls.append(("update_leverage", leverage, name, is_cross))
        return {"status": "ok"}


class FakeHLInfo:
    def __init__(self, leverage_type="isolated", szi="1.0"):
        self.state = {"marginSummary": {"accountValue": "500"}, "withdrawable": "400", "assetPositions": [
            {"position": {"coin": "BTC", "szi": szi, "leverage": {"type": leverage_type, "value": 1}}}]}

    def user_state(self, address):
        return self.state


def _hl(tmp_path, info=None):
    settings = make_settings(tmp_path, hyperliquid_account_address="0x" + "1" * 40)
    exchange = FakeHLExchange()
    return hyperliquid_adapter.HyperliquidAdapter(settings, "BTC", authenticated=True, info=info or FakeHLInfo(),
                                                  exchange=exchange), exchange


def test_hyperliquid_isolated_margin_and_reduce_only_exits(tmp_path):
    adapter, exchange = _hl(tmp_path)
    adapter.prepare_live(1)
    assert exchange.calls[0] == ("update_leverage", 1, "BTC", False)  # is_cross=False -> isolated
    adapter.place_stop_limit_sell("cid-sl", Decimal("0.5"), Decimal("90"), Decimal("89"), reduce_only=True)
    _, _, is_buy, sz, px, order_type, reduce_only, cloid = exchange.calls[-1]
    assert not is_buy and reduce_only and px == 89.0
    assert order_type == {"trigger": {"triggerPx": 90.0, "isMarket": False, "tpsl": "sl"}}
    assert cloid.startswith("0x") and len(cloid) == 34
    with pytest.raises(OrderRejected):
        adapter.place_limit_sell("cid-tp", Decimal("0.5"), Decimal("110"), reduce_only=False)


def test_hyperliquid_cross_margin_position_is_refused(tmp_path):
    adapter, _ = _hl(tmp_path, info=FakeHLInfo(leverage_type="cross"))
    with pytest.raises(FatalRiskError):
        adapter.available_position()
    with pytest.raises(LiveTradingDisabled):
        adapter.prepare_live(1)


def test_hyperliquid_order_error_is_rejected():
    with pytest.raises(OrderRejected):
        hyperliquid_adapter.parse_order_response(
            {"status": "ok", "response": {"data": {"statuses": [{"error": "Order must have minimum value of $10."}]}}})


def test_installed_sdks_have_every_method_used():
    coinbase_adapter.verify_sdk()
    hyperliquid_adapter.verify_sdk()


def test_sdk_mismatch_disables_live_trading():
    class OldClient:
        def get_public_product(self, product_id):
            ...

    with pytest.raises(LiveTradingDisabled):
        coinbase_adapter.verify_sdk(OldClient)


# --------------------------------------------------------------- misc safety
def test_secrets_never_reach_logs(tmp_path, caplog):
    secret = "-----BEGIN EC PRIVATE KEY-----\nSUPERSECRETVALUE\n-----END EC PRIVATE KEY-----"
    settings = make_settings(tmp_path, coinbase_api_secret=secret)
    assert "SUPERSECRETVALUE" not in repr(settings)
    record = logging.LogRecord("x", logging.INFO, "", 0, "oops %s", (secret,), None)
    cli.RedactSecrets([secret]).filter(record)
    assert "SUPERSECRETVALUE" not in record.getMessage()


def test_backtest_runs_walk_forward(tmp_path):
    settings = make_settings(tmp_path)
    inputs = risk_inputs_from_settings(settings, Venue.COINBASE)
    meta = cb_meta(price_increment=Decimal("0.01"))
    result = run_backtest(make_candles(n=400), meta, settings, inputs, interval="1h")
    assert result.candles == 400
    assert result.stats.trades + (1 if result.open_position else 0) >= 1, "expected at least one simulated trade"
    assert result.stats.trades == result.in_sample.trades + result.out_of_sample.trades
