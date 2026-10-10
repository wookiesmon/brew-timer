"""Behaviour that matters once real money is involved."""
from decimal import Decimal

import pytest
import requests

import cli
import coinbase_adapter
import hyperliquid_adapter
from conftest import NOW, FakeAdapter, cb_meta, make_candles, make_settings
from execution import RunSession
from models import FatalRiskError, LiveTradingDisabled, Mode, OrderRole, OrderStatus, OrderType
from simulator import SimulatedExchange
from test_safety import H, Harness


# ------------------------------------------------------------ stop placement
def test_stop_is_a_limit_sell_when_price_already_below_trigger(tmp_path):
    h = Harness(tmp_path, max_daily_loss_usd=Decimal("1000"))
    h.step(100, NOW)
    h.candle(NOW, 100, 100.5, 96.5, 98)  # all entries fill
    h.step(h.plan.stop_trigger - Decimal("0.1"), NOW + H)  # price gapped under the trigger
    stop = h.orders(OrderRole.STOP, open_only=True)[0]
    assert stop.order_type == OrderType.LIMIT and stop.price == h.plan.stop_limit
    assert stop.quantity == h.db.position(h.run_id)[0]


class RejectingStops(SimulatedExchange):
    def place_stop_limit_sell(self, *args, **kwargs):
        from models import OrderRejected

        raise OrderRejected("INVALID_STOP_PRICE")


def test_repeatedly_rejected_stop_halts_the_bot(tmp_path):
    h = Harness(tmp_path, sim_cls=RejectingStops, max_daily_loss_usd=Decimal("1000"))
    h.step(100, NOW)
    h.candle(NOW, 100, 100.5, 96.5, 98)
    with pytest.raises(FatalRiskError, match="protective stop rejected"):
        for i in range(1, 6):
            h.step(98, NOW + i * H)
    assert len([o for o in h.orders(OrderRole.STOP) if o.status == OrderStatus.REJECTED]) == 3
    assert h.db.halt_reason("coinbase", "paper")


# --------------------------------------------------------------- run loop
def test_run_loop_survives_transient_errors(tmp_path):
    settings = make_settings(tmp_path)
    calls = {"n": 0}

    class Report:
        status, messages = "RUNNING", []
        position = avg_cost = realized = unrealized = Decimal(0)
        open_orders = 0

    def step(now):
        calls["n"] += 1
        if calls["n"] < 3:
            raise requests.exceptions.ConnectionError("blip")
        report = Report()
        report.status = "DONE"
        return report

    assert cli._run_loop(step, settings, once=False, label="t", sleep=lambda s: None) == cli.EXIT_OK
    assert calls["n"] == 3


def test_run_loop_gives_up_after_repeated_errors(tmp_path):
    settings = make_settings(tmp_path)

    def step(now):
        raise requests.exceptions.Timeout("down")

    assert cli._run_loop(step, settings, once=False, label="t", sleep=lambda s: None) == cli.EXIT_ERROR


# ---------------------------------------------------------------- sessions
def test_session_starts_next_run_after_close_up_to_max_runs(tmp_path):
    h = Harness(tmp_path, max_daily_loss_usd=Decimal("1000"))
    plans = {"n": 0}

    def factory(now):
        plans["n"] += 1
        return h.plan

    session = RunSession(db=h.db, gateway=h.sim, meta=h.meta, settings=h.settings, mode=Mode.PAPER,
                         plan_factory=factory, run_id=h.run_id, max_runs=2)
    h.clock["now"] = NOW
    session.step(Decimal("100"), NOW)
    h.candle(NOW, 100, 100.5, 96.5, 98)
    session.step(Decimal("98"), NOW + H)
    h.candle(NOW + H, 97.5, 97.6, 95.8, 96)  # stop fills -> run 1 closes
    h.clock["now"] = NOW + 2 * H
    assert session.step(Decimal("96"), NOW + 2 * H).status == "CLOSED"
    h.clock["now"] = NOW + 3 * H
    session.step(Decimal("100"), NOW + 3 * H)  # second run created and its entries placed
    assert plans["n"] == 1 and session.runs_started == 2
    runs = h.db.runs("coinbase", h.meta.symbol, "paper")
    assert [r["status"] for r in runs] == ["CLOSED", "ACTIVE"]


def test_session_waits_while_plans_are_refused(tmp_path):
    h = Harness(tmp_path)
    refused = h.plan.__class__.from_dict(h.plan.to_dict())
    refused.refused, refused.refusal_reasons = True, ["Market is extended"]
    session = RunSession(db=h.db, gateway=h.sim, meta=h.meta, settings=h.settings, mode=Mode.PAPER,
                         plan_factory=lambda now: refused, max_runs=1)
    h.db.set_run_status(h.run_id, "CLOSED", NOW)
    report = session.step(Decimal("100"), NOW)
    assert report.status == "WAITING" and "extended" in report.messages[0]


# ------------------------------------------------------------- credentials
def test_coinbase_key_with_transfer_permission_is_refused(tmp_path):
    class Client:
        def get_api_key_permissions(self):
            return {"can_view": True, "can_trade": True, "can_transfer": True}

    adapter = coinbase_adapter.CoinbaseAdapter(make_settings(tmp_path), "GTC-USD", authenticated=True, client=Client())
    with pytest.raises(LiveTradingDisabled, match="TRANSFER"):
        adapter.check_key_permissions()


def test_live_refuses_transfer_capable_key(tmp_path, monkeypatch):
    settings = make_settings(tmp_path, coinbase_live_trading=True, dry_run=False)
    fake = FakeAdapter(cb_meta(), make_candles())
    fake.permissions = {"can_view": True, "can_trade": True, "can_transfer": True}
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: fake)
    code = cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--live", "--once"],
                    input_fn=lambda p: "CONFIRM_LIVE", settings=settings)
    assert code == cli.EXIT_REFUSED and fake.placed == []


def test_hyperliquid_main_wallet_key_is_refused(tmp_path):
    from eth_account import Account

    acct = Account.create()
    settings = make_settings(tmp_path, hyperliquid_private_key=acct.key.hex(),
                             hyperliquid_account_address=acct.address)
    adapter = hyperliquid_adapter.HyperliquidAdapter(settings, "BTC", authenticated=True, info=object(), exchange=object())
    with pytest.raises(LiveTradingDisabled, match="main account"):
        adapter.check_api_wallet()
    agent = Account.create()
    ok = make_settings(tmp_path, hyperliquid_private_key=agent.key.hex(), hyperliquid_account_address=acct.address)
    hyperliquid_adapter.HyperliquidAdapter(ok, "BTC", authenticated=True, info=object(), exchange=object()).check_api_wallet()


# ------------------------------------------------------------ formatting
def test_coinbase_orders_never_use_scientific_notation(tmp_path):
    sent = {}

    class Client:
        def limit_order_gtc_buy(self, **kwargs):
            sent.update(kwargs)
            return {"success": True, "success_response": {"order_id": "x"}}

    adapter = coinbase_adapter.CoinbaseAdapter(make_settings(tmp_path), "PEPE-USD", authenticated=True, client=Client())
    adapter.place_limit_buy("cid", Decimal("1E+6"), Decimal("5E-7"))
    assert sent["base_size"] == "1000000" and sent["limit_price"] == "0.0000005"


# ----------------------------------------------------------- new commands
def test_preview_validates_without_placing(tmp_path, monkeypatch, capsys):
    settings = make_settings(tmp_path)
    fake = FakeAdapter(cb_meta(), make_candles())
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: fake)
    code = cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--preview"], settings=settings)
    assert code == cli.EXIT_OK and fake.placed == [] and fake.placed_previews == 3
    assert "nothing is placed" in capsys.readouterr().out


def test_check_reports_without_trading(tmp_path, monkeypatch, capsys):
    settings = make_settings(tmp_path)
    fake = FakeAdapter(cb_meta(), make_candles())
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: fake)
    code = cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--check"], settings=settings)
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK and fake.placed == []
    assert "[PASS] market listed and tradable" in out and "[SKIP] credentials" in out


def test_paper_with_max_runs_keeps_going(tmp_path, monkeypatch):
    settings = make_settings(tmp_path)
    fake = FakeAdapter(cb_meta(), make_candles())
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: fake)
    assert cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--paper", "--once", "--max-runs", "3"],
                    settings=settings) == cli.EXIT_OK
    with pytest.raises(SystemExit):
        cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--paper", "--max-runs", "0"], settings=settings)
