"""Venue-neutral execution engine, shared by paper, backtest and live modes.

The engine only talks to an OrderGateway (live adapter or simulator), so the code
that runs in paper mode is the code that runs live.

Order lifecycle per run:
  1. Entries E1..E3: GTC limit buys, submitted once (never re-submitted).
  2. Every step reconciles each non-terminal order with the venue, records fill
     deltas (partial fills included) and recomputes the position from fills.
  3. Exits are sized from *confirmed* fills only:
       - STOP: stop-limit sell for the protected quantity.
       - TP1..TP3: limit sells for 40/35/25% of the quantity bought.
     Coinbase spot: resting sells hold the base balance, so the stop and the TPs
     cannot both cover the full position. The stop covers everything; a TP is only
     placed once price reaches its level, after shrinking the stop to make room.
     Hyperliquid: exits are reduce-only, so TPs rest from the start alongside a
     full-size stop.
  4. The run closes when the position is flat and nothing is open.

Duplicate prevention: every order row is written (PENDING_SUBMIT) before the API
call, client IDs are deterministic per (run, leg, version) and UNIQUE in SQLite,
a leg is never re-submitted while a non-terminal row exists, and an order whose
submission outcome is unknown is looked up by client ID instead of resent.
"""
from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from analysis import INTERVAL_SECONDS, MIN_CANDLES, analyze
from config import Settings
from database import Database, iso
from models import (
    FatalRiskError,
    InsufficientHistory,
    KillSwitchTriggered,
    MarketMeta,
    Mode,
    OrderGateway,
    OrderRecord,
    OrderRejected,
    OrderRole,
    OrderStatus,
    OrderType,
    RiskRejected,
    Side,
    TradePlan,
)
from risk import (
    TP_WEIGHTS,
    RiskInputs,
    build_plan,
    check_order_capacity,
    check_position_notional,
    daily_loss_breached,
    kill_switch_active,
    meets_minimums,
    round_size,
    split_quantity,
)

log = logging.getLogger("bot.engine")

TP_LEGS = ("TP1", "TP2", "TP3")
STOP_LEG = "SL"
MAX_EXIT_REJECTIONS = 3
SUBMIT_LOOKUP_GRACE = timedelta(minutes=2)


def event(name: str, **fields) -> str:
    """key=value log line. Callers pass explicit fields only; never credentials."""
    return name + " " + " ".join(f"{k}={v}" for k, v in fields.items())


def new_run_id(venue: str, now: datetime) -> str:
    return f"{venue[:2]}{now:%Y%m%d%H%M%S}{secrets.token_hex(2)}"


def create_run(db: Database, plan: TradePlan, mode: Mode, now: datetime, run_id: Optional[str] = None) -> str:
    if plan.refused:
        raise RiskRejected("refused plans cannot be started: " + "; ".join(plan.refusal_reasons))
    run_id = run_id or new_run_id(plan.venue.value, now)
    db.create_run(run_id, plan.venue.value, plan.symbol, mode.value, plan, now)
    log.info(event("run_created", run_id=run_id, venue=plan.venue.value, product=plan.symbol, mode=mode.value))
    return run_id


@dataclass
class StepReport:
    status: str  # RUNNING | CLOSED
    position: Decimal
    avg_cost: Decimal
    realized: Decimal
    unrealized: Decimal
    open_orders: int
    messages: list[str] = field(default_factory=list)


class TradingEngine:
    def __init__(self, *, db: Database, gateway: OrderGateway, meta: MarketMeta, settings: Settings,
                 mode: Mode, run_id: str, stop_file: Optional[Path] = None):
        self.db = db
        self.gateway = gateway
        self.meta = meta
        self.settings = settings
        self.mode = mode
        self.run_id = run_id
        self.plan = db.run_plan(run_id)
        self.stop_file = Path(stop_file or settings.stop_file)
        self.fee = settings.fee_pct(meta.venue.value) / 100
        self.simulated = mode != Mode.LIVE
        self.untracked_open = 0
        self.messages: list[str] = []

    # -------------------------------------------------------------- helpers
    @property
    def venue(self) -> str:
        return self.meta.venue.value

    @property
    def product(self) -> str:
        return self.meta.symbol

    def _note(self, message: str) -> None:
        log.info(event("note", run_id=self.run_id, msg=repr(message)))
        self.messages.append(message)

    def _orders(self, *, role: Optional[OrderRole] = None, leg: Optional[str] = None,
                open_only: bool = False) -> list[OrderRecord]:
        rows = self.db.orders_for_run(self.run_id, open_only=open_only)
        return [r for r in rows if (role is None or r.role == role) and (leg is None or r.leg == leg)]

    def _start_cooldown(self, now: datetime) -> None:
        until = now + timedelta(seconds=self.settings.api_error_cooldown_seconds)
        self.db.set_cooldown(self.venue, self.mode.value, until)
        log.warning(event("api_cooldown", until=iso(until)))

    def _in_cooldown(self, now: datetime) -> bool:
        until = self.db.cooldown_until(self.venue, self.mode.value)
        return until is not None and now < until

    def _client_id(self, leg: str) -> str:
        return f"{self.run_id}-{leg}-{self.db.count_leg_versions(self.run_id, leg) + 1}"

    # --------------------------------------------------------------- submit
    def submit(self, leg: str, role: OrderRole, side: Side, order_type: OrderType, quantity: Decimal,
               price: Decimal, now: datetime, trigger: Optional[Decimal] = None) -> Optional[OrderRecord]:
        if kill_switch_active(self.stop_file):
            raise KillSwitchTriggered(f"kill switch file {self.stop_file} exists")
        if self._orders(leg=leg, open_only=True):
            return None  # never duplicate a live leg
        if self._in_cooldown(now):
            return None  # an earlier call in this step failed; let reconciliation catch up first
        try:
            open_count = len(self.db.open_orders(self.venue, self.mode.value)) + self.untracked_open
            check_order_capacity(open_count, 1, self.settings.max_open_orders)
            if side == Side.BUY:
                position, _ = self.db.position(self.run_id)
                pending = sum((r.remaining for r in self._orders(role=OrderRole.ENTRY, open_only=True)), Decimal(0))
                check_position_notional(position + pending + quantity, price, self.settings.max_position_notional_usd)
        except RiskRejected as exc:
            self._note(f"{leg} not submitted: {exc}")
            return None

        record = self.db.insert_order(
            venue=self.venue, product=self.product, mode=self.mode.value, run_id=self.run_id,
            client_order_id=self._client_id(leg), leg=leg, role=role, order_type=order_type, side=side,
            price=price, trigger_price=trigger, quantity=quantity, now=now,
        )
        reduce_only = not self.gateway.exits_share_balance
        try:
            if side == Side.BUY:
                exchange_id = self.gateway.place_limit_buy(record.client_order_id, quantity, price)
            elif order_type == OrderType.LIMIT:
                exchange_id = self.gateway.place_limit_sell(record.client_order_id, quantity, price, reduce_only)
            else:
                exchange_id = self.gateway.place_stop_limit_sell(
                    record.client_order_id, quantity, trigger, price, reduce_only
                )
        except OrderRejected as exc:
            self.db.update_order(record.id, now, status=OrderStatus.REJECTED, error=str(exc)[:500])
            self._note(f"{leg} rejected: {exc}")
            return None
        except Exception as exc:  # noqa: BLE001 - outcome unknown; look it up, never resend blindly
            self.db.update_order(record.id, now, status=OrderStatus.SUBMIT_UNKNOWN,
                                 error=f"{type(exc).__name__}: {str(exc)[:300]}")
            log.error(event("submit_unknown", leg=leg, client_order_id=record.client_order_id,
                            error=type(exc).__name__))
            self._start_cooldown(now)
            return None
        record = self.db.update_order(record.id, now, exchange_order_id=exchange_id, status=OrderStatus.OPEN)
        log.info(event(
            "order_submitted", product=self.product, mode=self.mode.value, leg=leg, side=side.value,
            type=order_type.value, qty=quantity, price=price, trigger=trigger,
            client_order_id=record.client_order_id, order_id=exchange_id, simulated=self.simulated,
        ))
        return record

    # ------------------------------------------------------------ reconcile
    def _apply(self, record: OrderRecord, snapshot, now: datetime) -> OrderRecord:
        delta = snapshot.filled_quantity - record.filled_quantity
        if delta > 0:
            prev_notional = (record.avg_fill_price or Decimal(0)) * record.filled_quantity
            new_avg = snapshot.avg_fill_price or record.price
            fill_price = (new_avg * snapshot.filled_quantity - prev_notional) / delta
            fee_delta = max(snapshot.fees - record.fees, Decimal(0))
            realized = self.db.record_fill(
                venue=self.venue, product=self.product, mode=self.mode.value, run_id=self.run_id,
                client_order_id=record.client_order_id, side=record.side, quantity=delta, price=fill_price,
                fee=fee_delta, simulated=self.simulated, now=now,
            )
            log.info(event(
                "fill", simulated=self.simulated, leg=record.leg, side=record.side.value, qty=delta,
                price=fill_price, fee=fee_delta, realized=realized, order_id=snapshot.exchange_order_id,
            ))
        return self.db.update_order(
            record.id, now, exchange_order_id=snapshot.exchange_order_id,
            filled_quantity=max(snapshot.filled_quantity, record.filled_quantity),
            avg_fill_price=snapshot.avg_fill_price if snapshot.avg_fill_price is not None else record.avg_fill_price,
            fees=max(snapshot.fees, record.fees), status=snapshot.status,
        )

    def reconcile(self, now: datetime) -> None:
        for record in self._orders(open_only=True):
            try:
                snapshot = self.gateway.get_order(record.client_order_id, record.exchange_order_id)
            except Exception as exc:  # noqa: BLE001
                log.error(event("reconcile_error", client_order_id=record.client_order_id, error=type(exc).__name__))
                self._start_cooldown(now)
                continue
            if snapshot is None:
                if record.status in (OrderStatus.PENDING_SUBMIT, OrderStatus.SUBMIT_UNKNOWN):
                    if now - datetime.fromisoformat(record.created_at) > SUBMIT_LOOKUP_GRACE:
                        self.db.update_order(record.id, now, status=OrderStatus.REJECTED,
                                             error="not found on the exchange after submission")
                        self._note(f"{record.leg} was never accepted by the exchange")
                else:
                    log.warning(event("order_missing", client_order_id=record.client_order_id))
                continue
            self._apply(record, snapshot, now)
        try:
            tracked = {r.exchange_order_id for r in self.db.open_orders(self.venue, self.mode.value) if r.exchange_order_id}
            self.untracked_open = sum(1 for o in self.gateway.list_open_orders() if o.exchange_order_id not in tracked)
        except Exception as exc:  # noqa: BLE001
            log.error(event("list_open_error", error=type(exc).__name__))
            self._start_cooldown(now)
        if self.untracked_open:
            self._note(f"{self.untracked_open} open order(s) on {self.product} are not managed by this bot; "
                       "they count toward MAX_OPEN_ORDERS and are left untouched")

    def cancel_and_confirm(self, records: list[OrderRecord], now: datetime) -> bool:
        """Cancel, then re-read each order. True only if every one is now terminal."""
        ids = [r.exchange_order_id for r in records if r.exchange_order_id]
        if ids:
            try:
                self.gateway.cancel_orders(ids)
            except Exception as exc:  # noqa: BLE001
                log.error(event("cancel_error", error=type(exc).__name__))
                self._start_cooldown(now)
                return False
        done = True
        for record in records:
            try:
                snapshot = self.gateway.get_order(record.client_order_id, record.exchange_order_id)
            except Exception:  # noqa: BLE001
                done = False
                continue
            if snapshot is not None:
                record = self._apply(record, snapshot, now)
            done = done and record.status.terminal
            log.info(event("cancel", leg=record.leg, order_id=record.exchange_order_id, status=record.status.value))
        return done

    def emergency_cancel(self, now: datetime, *, keep_stop: bool = False) -> None:
        records = [r for r in self._orders(open_only=True) if not (keep_stop and r.role == OrderRole.STOP)]
        self.cancel_and_confirm(records, now)

    # ---------------------------------------------------------------- rules
    def _exit_phase(self, last_price: Decimal) -> bool:
        """True once something was bought and price reached TP1, or any exit has filled."""
        exits_filled = any(r.filled_quantity > 0 for r in self._orders() if r.role != OrderRole.ENTRY)
        reached_tp1 = bool(self.plan.take_profits) and last_price >= self.plan.take_profits[0]
        return exits_filled or (reached_tp1 and self.db.total_bought(self.run_id) > 0)

    def manage_entries(self, now: datetime, last_price: Decimal) -> None:
        open_entries = self._orders(role=OrderRole.ENTRY, open_only=True)
        expired = now - datetime.fromisoformat(self.db.get_run(self.run_id)["created_at"]) > timedelta(
            hours=self.settings.entry_ttl_hours)
        if open_entries and (expired or self._exit_phase(last_price)):
            self._note("cancelling unfilled entries (" + ("entry TTL reached" if expired else "exit phase") + ")")
            self.cancel_and_confirm(open_entries, now)
            return
        if expired or self._exit_phase(last_price):
            return
        for planned in self.plan.entries:
            if not self._orders(leg=planned.leg):  # each entry leg is submitted at most once
                self.submit(planned.leg, OrderRole.ENTRY, Side.BUY, OrderType.LIMIT, planned.quantity,
                            planned.price, now)

    def desired_take_profits(self, position: Decimal, last_price: Decimal) -> dict[str, tuple[Decimal, Decimal]]:
        """leg -> (quantity still to sell, price)."""
        if not self.plan.take_profits:
            return {}
        bought = self.db.total_bought(self.run_id)
        tranches = split_quantity(bought, TP_WEIGHTS, self.meta)
        desired: dict[str, tuple[Decimal, Decimal]] = {}
        budget = position
        for leg, tranche, level in zip(TP_LEGS, tranches, self.plan.take_profits):
            sold = sum((r.filled_quantity for r in self._orders(leg=leg)), Decimal(0))
            need = round_size(self.meta, min(tranche - sold, budget))
            if need <= 0 or not meets_minimums(self.meta, need, level):
                continue
            is_open = bool(self._orders(leg=leg, open_only=True))
            if self.gateway.exits_share_balance and last_price < level and not is_open:
                continue  # Coinbase: only free the stop's balance once the level is reached
            desired[leg] = (need, level)
            budget -= need
        return desired

    def manage_exits(self, now: datetime, last_price: Decimal) -> None:
        position, _ = self.db.position(self.run_id)
        open_exits = [r for r in self._orders(open_only=True) if r.role != OrderRole.ENTRY]
        if position < self.meta.size_increment:
            if open_exits:
                self.cancel_and_confirm(open_exits, now)
            return

        desired_tps = self.desired_take_profits(position, last_price)
        tp_total = sum((q for q, _ in desired_tps.values()), Decimal(0))
        stop_qty = round_size(self.meta, position - tp_total if self.gateway.exits_share_balance else position)
        inc = self.meta.size_increment

        for record in [r for r in open_exits if r.role == OrderRole.TAKE_PROFIT]:
            want = desired_tps.get(record.leg)
            if want is None or abs(record.remaining - want[0]) >= inc:
                self.cancel_and_confirm([record], now)
        stops = [r for r in open_exits if r.role == OrderRole.STOP]
        for record in stops:
            if abs(record.remaining - stop_qty) >= inc:
                if not self.cancel_and_confirm([record], now):
                    self._note("stop resize pending: old stop not yet confirmed cancelled")
                    return

        for leg, (quantity, level) in desired_tps.items():
            if self._orders(leg=leg, open_only=True):
                continue
            if sum(1 for r in self._orders(leg=leg) if r.status == OrderStatus.REJECTED) >= MAX_EXIT_REJECTIONS:
                self._note(f"{leg} rejected {MAX_EXIT_REJECTIONS} times; not retrying (the stop still protects)")
                continue
            if self.gateway.exits_share_balance and quantity > self.gateway.available_position():
                self._note(f"{leg} waiting: base balance not yet released by the exchange")
                continue
            self.submit(leg, OrderRole.TAKE_PROFIT, Side.SELL, OrderType.LIMIT, quantity, level, now)

        if self._orders(leg=STOP_LEG, open_only=True):
            return
        if stop_qty <= 0:
            return
        if not meets_minimums(self.meta, stop_qty, self.plan.stop_limit):
            self._note(f"residual {stop_qty} is below the exchange minimum and cannot carry a stop order")
            return
        if self.gateway.exits_share_balance:
            available = self.gateway.available_position()
            if stop_qty > available:
                stop_qty = round_size(self.meta, available)
                if not meets_minimums(self.meta, stop_qty, self.plan.stop_limit):
                    self._note("stop waiting: base balance not yet available")
                    return
        self._halt_if_stop_keeps_failing(now)
        if last_price <= self.plan.stop_trigger:
            # A stop order below the market would be rejected (or trigger at once). Place what a
            # triggered stop-limit becomes: a limit sell at the stop-limit price.
            self._note("price is already at or below the stop trigger: protecting with a limit sell "
                       "at the stop-limit price (what a triggered stop-limit becomes)")
            self.submit(STOP_LEG, OrderRole.STOP, Side.SELL, OrderType.LIMIT, stop_qty, self.plan.stop_limit, now)
            return
        self.submit(STOP_LEG, OrderRole.STOP, Side.SELL, OrderType.STOP_LIMIT, stop_qty,
                    self.plan.stop_limit, now, trigger=self.plan.stop_trigger)

    def _halt_if_stop_keeps_failing(self, now: datetime) -> None:
        rejected = [r for r in self._orders(leg=STOP_LEG) if r.status == OrderStatus.REJECTED]
        if len(rejected) >= MAX_EXIT_REJECTIONS:
            reason = (f"protective stop rejected {len(rejected)} times (last: {rejected[-1].error}); "
                      "the position needs manual attention")
            self.emergency_cancel(now, keep_stop=True)
            self.db.set_halt(self.venue, self.mode.value, reason)
            self.db.set_run_status(self.run_id, "HALTED", now)
            log.critical(event("halt", reason=repr(reason)))
            raise FatalRiskError(reason)

    def check_daily_loss(self, now: datetime, last_price: Decimal) -> None:
        position, avg_cost = self.db.position(self.run_id)
        unrealized = position * (last_price - avg_cost) - position * last_price * self.fee
        realized = self.db.realized_today(self.venue, self.mode.value, now)
        if daily_loss_breached(realized, unrealized, self.settings.max_daily_loss_usd):
            reason = (f"daily loss limit breached: realized {realized:.2f}, unrealized {unrealized:.2f}, "
                      f"limit {self.settings.max_daily_loss_usd}")
            # Entries and take-profits are cancelled; the protective stop is kept on purpose.
            self.emergency_cancel(now, keep_stop=True)
            self.db.set_halt(self.venue, self.mode.value, reason)
            self.db.set_run_status(self.run_id, "HALTED", now)
            log.critical(event("halt", reason=repr(reason)))
            raise FatalRiskError(reason)

    # ----------------------------------------------------------------- step
    def step(self, last_price: Decimal, now: Optional[datetime] = None) -> StepReport:
        now = now or datetime.now(timezone.utc)
        self.messages = []
        if kill_switch_active(self.stop_file):
            self.emergency_cancel(now)
            self.db.set_run_status(self.run_id, "KILLED", now)
            position, _ = self.db.position(self.run_id)
            log.critical(event("kill_switch", run_id=self.run_id, open_position=position))
            raise KillSwitchTriggered(
                f"STOP file found: bot-managed orders cancelled. Open position {position} {self.meta.base_asset} "
                "is now UNPROTECTED (no stop order)."
            )
        halted = self.db.halt_reason(self.venue, self.mode.value)
        if halted:
            raise FatalRiskError(f"bot is halted: {halted}. Review, then run --clear-halt.")

        self.reconcile(now)
        self.check_daily_loss(now, last_price)
        if not self._in_cooldown(now):
            self.manage_entries(now, last_price)
            self.manage_exits(now, last_price)
        else:
            self._note("API error cooldown active: no new orders this step")

        position, avg_cost = self.db.position(self.run_id)
        open_orders = self._orders(open_only=True)
        status = "RUNNING"
        entries_done = all(r.status.terminal for r in self._orders(role=OrderRole.ENTRY)) and bool(
            self._orders(role=OrderRole.ENTRY))
        if position < self.meta.size_increment and not open_orders and entries_done:
            status = "CLOSED"
            self.db.set_run_status(self.run_id, "CLOSED", now)
            log.info(event("run_closed", run_id=self.run_id, realized=self.db.realized_for_run(self.run_id)))
        return StepReport(
            status=status,
            position=position,
            avg_cost=avg_cost,
            realized=self.db.realized_for_run(self.run_id),
            unrealized=position * (last_price - avg_cost),
            open_orders=len(open_orders),
            messages=list(self.messages),
        )


class RunSession:
    """Drives one run at a time. When a run closes and ``max_runs`` allows, the next plan
    comes from ``plan_factory`` (which returns None while no setup is allowed)."""

    def __init__(self, *, db: Database, gateway: OrderGateway, meta: MarketMeta, settings: Settings, mode: Mode,
                 plan_factory: Callable[[datetime], Optional[TradePlan]], run_id: Optional[str] = None,
                 max_runs: int = 1, stop_file: Optional[Path] = None):
        if max_runs < 1:
            raise ValueError("max_runs must be at least 1")
        self.db, self.gateway, self.meta, self.settings, self.mode = db, gateway, meta, settings, mode
        self.plan_factory = plan_factory
        self.max_runs = max_runs
        self.stop_file = stop_file
        self.engine: Optional[TradingEngine] = None
        self.runs_started = 0
        if run_id is not None:
            self._attach(run_id)

    def _attach(self, run_id: str) -> None:
        self.engine = TradingEngine(db=self.db, gateway=self.gateway, meta=self.meta, settings=self.settings,
                                    mode=self.mode, run_id=run_id, stop_file=self.stop_file)
        self.runs_started += 1

    @property
    def plan(self) -> Optional[TradePlan]:
        return self.engine.plan if self.engine else None

    def _idle_report(self, status: str, message: str) -> StepReport:
        return StepReport(status=status, position=Decimal(0), avg_cost=Decimal(0), realized=Decimal(0),
                          unrealized=Decimal(0), open_orders=0, messages=[message])

    def step(self, last_price: Decimal, now: datetime) -> StepReport:
        if self.engine is None:
            if self.runs_started >= self.max_runs:
                return self._idle_report("DONE", f"{self.runs_started} run(s) completed")
            if kill_switch_active(Path(self.stop_file or self.settings.stop_file)):
                raise KillSwitchTriggered("STOP file found; no new run started")
            halted = self.db.halt_reason(self.meta.venue.value, self.mode.value)
            if halted:
                raise FatalRiskError(f"bot is halted: {halted}. Review, then run --clear-halt.")
            plan = self.plan_factory(now)
            if plan is None or plan.refused:
                reason = "; ".join(plan.refusal_reasons) if plan else "no plan available"
                return self._idle_report("WAITING", f"no new run: {reason}")
            self._attach(create_run(self.db, plan, self.mode, now))
        report = self.engine.step(last_price, now)
        if report.status == "CLOSED":
            self.engine = None
            if self.runs_started >= self.max_runs:
                report.status = "DONE"
        return report


# --------------------------------------------------------------- backtest
@dataclass
class BacktestResult:
    runs: list[dict]
    total_realized: Decimal
    open_position: Decimal
    unrealized: Decimal
    max_drawdown: Decimal
    candles: int
    skipped_plans: dict[str, int]


def candle_row(ts: pd.Timestamp, row) -> dict:
    return {"time": ts.to_pydatetime(), **{k: Decimal(str(row[k])) for k in ("open", "high", "low", "close", "volume")}}


def run_backtest(
    df: pd.DataFrame, meta: MarketMeta, settings: Settings, inputs: RiskInputs, *, interval: str,
    warmup: int = MIN_CANDLES, stop_file: Optional[Path] = None,
) -> BacktestResult:
    """Walk-forward replay: at each closed candle the plan is built from past candles
    only, then the simulator matches orders against the *next* candle."""
    from simulator import SimulatedExchange

    if len(df) <= warmup + 1:
        raise InsufficientHistory(f"backtest needs more than {warmup + 1} candles, got {len(df)}")
    db = Database(":memory:")
    seconds = INTERVAL_SECONDS[interval]
    clock = {"now": df.index[warmup].to_pydatetime()}
    sim = SimulatedExchange(
        db, meta.venue, meta.symbol, starting_quote=inputs.account_equity, fee_pct=inputs.fee_pct,
        participation_pct=settings.sim_volume_participation_pct, size_increment=meta.size_increment,
        clock=lambda: clock["now"], leverage=inputs.leverage,
    )
    stop_file = stop_file or Path("__backtest_has_no_kill_switch__")
    engine: Optional[TradingEngine] = None
    skipped: dict[str, int] = {}
    equity_curve: list[Decimal] = []
    counter = 0
    for i in range(warmup, len(df) - 1):
        ts = df.index[i]
        now = (ts + pd.Timedelta(seconds=seconds)).to_pydatetime()
        clock["now"] = now
        last_price = Decimal(str(df["close"].iloc[i]))
        if engine is None:
            try:
                analysis = analyze(df.iloc[: i + 1], meta.symbol, interval)
            except InsufficientHistory:
                continue
            plan = build_plan(analysis, meta, inputs, now)
            if plan.refused:
                key = plan.refusal_reasons[0]
                skipped[key] = skipped.get(key, 0) + 1
            else:
                counter += 1
                run_id = create_run(db, plan, Mode.BACKTEST, now, run_id=f"bt{counter:04d}")
                engine = TradingEngine(db=db, gateway=sim, meta=meta, settings=settings, mode=Mode.BACKTEST,
                                       run_id=run_id, stop_file=stop_file)
        if engine is not None:
            try:
                report = engine.step(last_price, now)
            except FatalRiskError:
                db.clear_halt(meta.venue.value, Mode.BACKTEST.value)  # daily limit: stand aside until next run
                engine = None
            else:
                if report.status == "CLOSED":
                    engine = None
        nxt = df.index[i + 1]
        sim.process_candle(candle_row(nxt, df.iloc[i + 1]))
        quote, base = sim.balances()
        equity_curve.append(quote + base * Decimal(str(df["close"].iloc[i + 1])))

    last_close = Decimal(str(df["close"].iloc[-1]))
    runs, total = [], Decimal(0)
    open_position = unrealized = Decimal(0)
    for row in db.runs(meta.venue.value, meta.symbol, Mode.BACKTEST.value):
        position, avg_cost = db.position(row["run_id"])
        realized = db.realized_for_run(row["run_id"])
        total += realized
        if position > 0:
            open_position += position
            unrealized += position * (last_close - avg_cost)
        runs.append({"run_id": row["run_id"], "created_at": row["created_at"], "status": row["status"],
                     "bought": db.total_bought(row["run_id"]), "realized": realized, "open_position": position})
    peak, max_dd = Decimal(0), Decimal(0)
    for value in equity_curve:
        peak = max(peak, value)
        max_dd = max(max_dd, peak - value)
    db.close()
    return BacktestResult(runs=runs, total_realized=total, open_position=open_position, unrealized=unrealized,
                          max_drawdown=max_dd, candles=len(df), skipped_plans=skipped)
