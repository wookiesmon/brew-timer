"""Command-line interface. Run as ``python -m main`` from this directory."""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional

import requests

from analysis import TARGET_CANDLES, MarketAnalysis, analyze
from config import ConfigError, Settings, load_settings
from database import Database
from execution import TradingEngine, create_run, run_backtest
from models import (
    BotError,
    FatalRiskError,
    InsufficientHistory,
    InvalidMetadata,
    KillSwitchTriggered,
    LiveTradingDisabled,
    MarketMeta,
    MarketUnavailable,
    Mode,
    TradePlan,
    Venue,
)
from risk import SCENARIO_LABEL, RiskInputs, build_plan, kill_switch_active, risk_inputs_from_settings

log = logging.getLogger("bot.cli")
CONFIRM_TEXT = "CONFIRM_LIVE"
CONFIRM_LEVERAGE_TEXT = "CONFIRM_LEVERAGE"

EXIT_OK, EXIT_ERROR, EXIT_UNAVAILABLE, EXIT_KILLED, EXIT_HALTED, EXIT_REFUSED = 0, 1, 2, 3, 4, 5


# ------------------------------------------------------------------ logging
class RedactSecrets(logging.Filter):
    """Defence in depth: blank out any configured secret that reaches a log record."""

    def __init__(self, secrets: list[str]):
        super().__init__()
        self.secrets = [s for s in secrets if s and len(s) >= 8]

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for secret in self.secrets:
            if secret in message:
                message = message.replace(secret, "***REDACTED***")
        record.msg, record.args = message, ()
        return True


def setup_logging(level: str, settings: Optional[Settings]) -> None:
    logging.Formatter.converter = time.gmtime
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)sZ %(levelname)s %(name)s %(message)s", "%Y-%m-%dT%H:%M:%S"))
    if settings is not None:
        secrets = [s.get_secret_value() for s in (settings.coinbase_api_key, settings.coinbase_api_secret,
                                                  settings.hyperliquid_private_key) if s is not None]
        handler.addFilter(RedactSecrets(secrets))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
    for noisy in ("urllib3", "websocket"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


# ------------------------------------------------------------------ parsing
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m main", description=(
        "Rule-based crypto planner with paper trading and gated live execution. "
        "Coinbase = spot only. Hyperliquid = isolated-margin perpetuals, 1x by default."))
    p.add_argument("--venue", choices=[v.value for v in Venue])
    p.add_argument("--product", help="Coinbase product (e.g. BTC-USD) or Hyperliquid coin (e.g. BTC)")
    actions = p.add_mutually_exclusive_group(required=True)
    actions.add_argument("--analyze", action="store_true", help="print analysis and plan; never trades")
    actions.add_argument("--paper", action="store_true", help="paper-trade with live market data")
    actions.add_argument("--backtest", action="store_true", help="walk-forward replay on historical candles")
    actions.add_argument("--live", action="store_true", help="live trading (requires every safety gate)")
    actions.add_argument("--status", action="store_true", help="show stored state and exchange state")
    actions.add_argument("--cancel-open", action="store_true", help="cancel open orders for the product")
    actions.add_argument("--reset-paper", action="store_true", help="delete paper state for the product")
    actions.add_argument("--clear-halt", action="store_true", help="clear a daily-loss halt after review")
    p.add_argument("--equity", help="account equity in USD (default ACCOUNT_EQUITY_USD)")
    p.add_argument("--max-allocation", help="maximum USD to deploy (capped by MAX_ALLOCATION_PCT)")
    p.add_argument("--max-loss", help="maximum planned loss in USD (capped by MAX_PLANNED_LOSS_PCT)")
    p.add_argument("--risk-pct", help="optional risk percentage of equity (<= MAX_PLANNED_LOSS_PCT)")
    p.add_argument("--ask", action="store_true", help="prompt for equity, allocation and loss")
    p.add_argument("--once", action="store_true", help="paper/live: run a single step and exit")
    p.add_argument("--candles", type=int, default=1000, help="backtest: number of candles to fetch")
    p.add_argument("--yes", action="store_true", help="skip the --cancel-open confirmation")
    p.add_argument("--env-file", default=".env")
    p.add_argument("--log-level", default="INFO")
    return p


def _decimal_arg(raw: Optional[str], name: str) -> Optional[Decimal]:
    if raw in (None, ""):
        return None
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ConfigError(f"{name} must be a number") from exc
    if not value.is_finite() or value <= 0:
        raise ConfigError(f"{name} must be a positive number")
    return value


def _ask(prompt: str, default: Optional[Decimal], input_fn: Callable[[str], str]) -> Optional[Decimal]:
    raw = input_fn(f"{prompt} [{default if default is not None else 'default'}]: ").strip()
    return _decimal_arg(raw, prompt) if raw else default


def gather_risk_inputs(args, settings: Settings, venue: Venue, input_fn: Callable[[str], str],
                       live_equity: Optional[Decimal] = None) -> RiskInputs:
    equity = _decimal_arg(args.equity, "--equity")
    allocation = _decimal_arg(args.max_allocation, "--max-allocation")
    max_loss = _decimal_arg(args.max_loss, "--max-loss")
    risk_pct = _decimal_arg(args.risk_pct, "--risk-pct")
    if args.ask:
        equity = _ask("Account equity (USD)", equity or settings.account_equity_usd, input_fn)
        allocation = _ask("Maximum allocation (USD)", allocation, input_fn)
        max_loss = _ask("Maximum acceptable planned loss (USD)", max_loss, input_fn)
        risk_pct = _ask("Optional risk percentage of equity", risk_pct, input_fn)
    if live_equity is not None:
        equity = min(equity or settings.account_equity_usd, live_equity)
    return risk_inputs_from_settings(settings, venue, equity=equity, max_allocation_usd=allocation,
                                     max_planned_loss_usd=max_loss, risk_pct=risk_pct)


# ------------------------------------------------------------------ adapters
def make_adapter(venue: Venue, product: str, settings: Settings, *, authenticated: bool):
    if venue == Venue.COINBASE:
        from coinbase_adapter import CoinbaseAdapter

        if "-" not in product:
            raise MarketUnavailable(f"{product} is not a Coinbase product id (expected e.g. BTC-USD)")
        return CoinbaseAdapter(settings, product.upper(), authenticated=authenticated)
    from hyperliquid_adapter import HyperliquidAdapter

    return HyperliquidAdapter(settings, product.upper(), authenticated=authenticated)


def verify_sdk(venue: Venue) -> None:
    if venue == Venue.COINBASE:
        from coinbase_adapter import verify_sdk as check
    else:
        from hyperliquid_adapter import verify_sdk as check
    check()


# ------------------------------------------------------------------ printing
def fmt(value, places: int = 8) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, Decimal):
        q = value.quantize(Decimal(1).scaleb(-places)) if value.as_tuple().exponent < -places else value
        text = format(q.normalize(), "f")
        return text
    if isinstance(value, float):
        return f"{value:.{places}g}"
    return str(value)


def print_meta(meta: MarketMeta) -> None:
    print("\n=== Market metadata ===")
    rows = [
        ("venue", meta.venue.value), ("product", meta.symbol), ("type", meta.product_type),
        ("base / quote", f"{meta.base_asset} / {meta.quote_asset}"), ("tradable", meta.tradable),
        ("status", meta.status_detail), ("size increment", fmt(meta.size_increment)),
        ("price increment", fmt(meta.price_increment) if meta.price_increment else
         f"5 significant figures, max {6 - (meta.sz_decimals or 0)} decimals"),
        ("min size", fmt(meta.min_size)), ("min notional", fmt(meta.min_notional)),
        ("max notional", fmt(meta.max_notional)), ("limit only", meta.limit_only),
        ("cancel only", meta.cancel_only), ("post only", meta.post_only), ("auction mode", meta.auction_mode),
    ]
    if meta.venue == Venue.HYPERLIQUID:
        rows += [("szDecimals", meta.sz_decimals), ("max leverage", meta.max_leverage),
                 ("only isolated", meta.only_isolated), ("mark price", fmt(meta.mark_price)),
                 ("funding rate (hourly)", fmt(meta.funding_rate))]
    for k, v in rows:
        print(f"  {k:<22} {v}")


def print_analysis(a: MarketAnalysis) -> None:
    print("\n=== Market analysis (historical candles only) ===")
    print(f"  candles               {a.candle_count} x {a.interval}  ({a.first_time:%Y-%m-%d %H:%M} -> "
          f"{a.last_time:%Y-%m-%d %H:%M} UTC, {a.missing_candles} missing)")
    print(f"  last close            {fmt(a.last_close)}")
    print(f"  24h change            {'n/a' if a.change_24h_pct is None else f'{a.change_24h_pct:.2f}%'}")
    print(f"  lookback change       {a.change_lookback_pct:.2f}%   high {fmt(a.high)}  low {fmt(a.low)}")
    print(f"  ATR(14)               {fmt(a.atr)}  ({a.atr / a.last_close * 100:.2f}% of price)")
    print(f"  EMA(20) / EMA(50)     {fmt(a.ema20)} / {fmt(a.ema50)}")
    print(f"  RSI(14)               {a.rsi:.1f}")
    print(f"  volatility            {a.volatility_per_candle_pct:.2f}% per candle, "
          f"{a.volatility_annualized_pct:.0f}% annualised")
    print(f"  volume                avg {a.avg_volume:.4g}, recent/avg ratio {a.volume_ratio:.2f}")
    print("  support zones         " + ("; ".join(
        f"{fmt(z.low)}-{fmt(z.high)} ({z.source}, {z.touches}x)" for z in a.supports[:4]) or "none"))
    print("  resistance zones      " + ("; ".join(
        f"{fmt(z.low)}-{fmt(z.high)} ({z.source}, {z.touches}x)" for z in a.resistances[:4]) or "none"))
    print("  rule score            " + ", ".join(f"{k}={v}" for k, v in a.score.items())
          + f"  (total {sum(a.score.values())}/{len(a.score)}; informational only)")
    for flag in a.flags:
        print(f"  ! {flag}")


def print_plan(plan: TradePlan, meta: MarketMeta) -> None:
    print("\n=== Proposed plan (scenario) ===")
    print(f"  {SCENARIO_LABEL}")
    if plan.refused:
        print("  PLAN REFUSED - no orders will be created:")
        for reason in plan.refusal_reasons:
            print(f"    - {reason}")
    print(f"\n  {'leg':<5}{'side':<6}{'price':>16}{'quantity':>18}{'notional':>14}")
    for e in plan.entries:
        print(f"  {e.leg:<5}{e.side.value:<6}{fmt(e.price):>16}{fmt(e.quantity):>18}{fmt(e.notional, 2):>14}")
    print(f"\n  weighted avg entry    {fmt(plan.weighted_avg_entry)}")
    print(f"  stop trigger          {fmt(plan.stop_trigger)}")
    print(f"  stop-limit price      {fmt(plan.stop_limit)}   (separate from the trigger)")
    print(f"  R (avg - trigger)     {fmt(plan.r_value)}")
    if plan.take_profits:
        print(f"  TP1 (1R)              {fmt(plan.take_profits[0])}")
        print(f"  TP2 (2R)              {fmt(plan.take_profits[1])}")
        print(f"  TP3                   {fmt(plan.take_profits[2])}  ({plan.tp3_source})")
    print("  Take-profit levels are scenarios, not forecasts. Upside is unbounded in theory; "
          "so is the chance of never reaching a level.")
    print("\n=== Risk ===")
    print(f"  total quantity        {fmt(plan.total_quantity)} {meta.base_asset}  (binding limit: {plan.sizing_binding})")
    print(f"  risk-based quantity   {fmt(plan.risk_based_quantity, 6)}   allocation-based {fmt(plan.allocation_based_quantity, 6)}")
    print(f"  capital deployed      {fmt(plan.capital_deployed, 2)} (max notional exposure)")
    if meta.venue == Venue.HYPERLIQUID:
        print(f"  leverage / margin     {plan.leverage}x isolated / {fmt(plan.margin_required, 2)} margin "
              f"for {fmt(plan.capital_deployed, 2)} notional")
        print(f"  est. liquidation      {fmt(plan.liquidation_price)} (conservative approximation; "
              "the exchange figure is used once a position exists)")
    print(f"  planned-loss budget   {fmt(plan.max_planned_loss_budget, 2)}")
    print(f"  loss at stop trigger  {fmt(plan.planned_loss_at_trigger, 2)}")
    print(f"  est. fees             {fmt(plan.estimated_fees, 2)}   est. slippage {fmt(plan.estimated_slippage, 2)}")
    print(f"  worst-case loss       {fmt(plan.worst_case_loss, 2)}  (stop-limit fills at its limit + fees + slippage)")
    for w in plan.warnings:
        print(f"  ! {w}")


def print_intended_orders(plan: TradePlan, venue: Venue) -> None:
    print("\n=== Intended orders ===")
    for e in plan.entries:
        print(f"  {e.leg}: GTC limit BUY {fmt(e.quantity)} @ {fmt(e.price)}")
    print("  After fills are confirmed (sized to the filled quantity only):")
    print(f"  SL : stop-limit SELL, trigger {fmt(plan.stop_trigger)}, limit {fmt(plan.stop_limit)}"
          + (" (reduce-only)" if venue == Venue.HYPERLIQUID else ""))
    for i, tp in enumerate(plan.take_profits, start=1):
        print(f"  TP{i}: limit SELL @ {fmt(tp)}" + (" (reduce-only, resting)" if venue == Venue.HYPERLIQUID
                                                 else " (placed when price reaches the level)"))


# ------------------------------------------------------------------ helpers
def load_meta(adapter) -> MarketMeta:
    meta = adapter.get_market_meta()
    meta.validate()
    return meta


def analyze_market(adapter, meta: MarketMeta, settings: Settings, now: datetime) -> MarketAnalysis:
    df = adapter.get_candles(settings.candle_interval, TARGET_CANDLES, now)
    change = float(meta.change_24h_pct) if meta.change_24h_pct is not None else None
    return analyze(df, meta.symbol, settings.candle_interval, change)


def make_sim(db: Database, meta: MarketMeta, settings: Settings, inputs: RiskInputs, clock):
    from simulator import SimulatedExchange

    return SimulatedExchange(
        db, meta.venue, meta.symbol, starting_quote=inputs.account_equity, fee_pct=inputs.fee_pct,
        participation_pct=settings.sim_volume_participation_pct, size_increment=meta.size_increment,
        clock=clock, leverage=inputs.leverage,
    )


def paper_tick(adapter, sim, db: Database, engine: TradingEngine, settings: Settings, now: datetime):
    from execution import candle_row

    key = f"sim_cursor:{engine.venue}:{engine.product}"
    cursor = db.get_state(key)
    df = adapter.get_candles(settings.candle_interval, 50, now)
    fills = []
    for ts, row in df.iterrows():
        if cursor is None or ts.to_pydatetime() > datetime.fromisoformat(cursor):
            if cursor is not None:
                fills += sim.process_candle(candle_row(ts, row))
            cursor = ts.to_pydatetime().isoformat()
    db.set_state(key, cursor)
    for f in fills:
        print(f"  [SIMULATED FILL] {f['side']} {fmt(f['quantity'])} @ {fmt(f['price'])} fee {fmt(f['fee'], 4)}")
    last_price = Decimal(str(df["close"].iloc[-1]))
    return engine.step(last_price, now)


def print_report(report) -> None:
    print(f"  status={report.status} position={fmt(report.position)} avg_cost={fmt(report.avg_cost)} "
          f"realized={fmt(report.realized, 2)} unrealized={fmt(report.unrealized, 2)} open_orders={report.open_orders}")
    for m in report.messages:
        print(f"  - {m}")


# ------------------------------------------------------------------ commands
def cmd_analyze(args, settings, venue, product, input_fn) -> int:
    adapter = make_adapter(venue, product, settings, authenticated=False)
    meta = adapter.get_market_meta()
    print_meta(meta)
    meta.validate()
    analysis = analyze_market(adapter, meta, settings, datetime.now(timezone.utc))
    print_analysis(analysis)
    plan = build_plan(analysis, meta, gather_risk_inputs(args, settings, venue, input_fn))
    print_plan(plan, meta)
    print_intended_orders(plan, venue)
    print("\nAnalysis only: no orders were created.")
    return EXIT_OK


def _run_loop(step: Callable[[datetime], object], settings: Settings, once: bool, label: str) -> int:
    while True:
        now = datetime.now(timezone.utc)
        try:
            report = step(now)
        except KillSwitchTriggered as exc:
            print(f"\nKILL SWITCH: {exc}")
            return EXIT_KILLED
        except FatalRiskError as exc:
            print(f"\nHALTED: {exc}\nThe bot will not restart on its own. Review, then run --clear-halt.")
            return EXIT_HALTED
        print(f"[{now:%Y-%m-%d %H:%M:%S}Z] {label}")
        print_report(report)
        if report.status == "CLOSED":
            print("Run closed.")
            return EXIT_OK
        if once:
            return EXIT_OK
        try:
            time.sleep(settings.poll_seconds)
        except KeyboardInterrupt:
            print("\nStopped by user. Open orders REMAIN on the venue; use --status or --cancel-open.")
            return EXIT_OK


def cmd_paper(args, settings, venue, product, input_fn) -> int:
    adapter = make_adapter(venue, product, settings, authenticated=False)
    meta = load_meta(adapter)
    db = Database(settings.paper_database_path)
    now = datetime.now(timezone.utc)
    clock = {"now": now}
    active = db.active_run(venue.value, meta.symbol, Mode.PAPER.value)
    if active is not None:
        plan = db.run_plan(active["run_id"])
        inputs = gather_risk_inputs(args, settings, venue, input_fn)
        run_id = active["run_id"]
        print(f"Resuming paper run {run_id} (state reconciled; no duplicate orders will be created).")
    else:
        print_meta(meta)
        analysis = analyze_market(adapter, meta, settings, now)
        print_analysis(analysis)
        inputs = gather_risk_inputs(args, settings, venue, input_fn)
        plan = build_plan(analysis, meta, inputs, now)
        print_plan(plan, meta)
        print_intended_orders(plan, venue)
        if plan.refused:
            print("\nPlan refused; nothing to paper-trade.")
            return EXIT_REFUSED
        run_id = create_run(db, plan, Mode.PAPER, now)
    sim = make_sim(db, meta, settings, inputs, lambda: clock["now"])
    engine = TradingEngine(db=db, gateway=sim, meta=meta, settings=settings, mode=Mode.PAPER, run_id=run_id)
    print(f"\nPAPER MODE: orders are simulated and stored in {settings.paper_database_path}. "
          "No order endpoint is ever called.")

    def step(now):
        clock["now"] = now
        return paper_tick(adapter, sim, db, engine, settings, now)

    return _run_loop(step, settings, args.once, "paper step (SIMULATED)")


def check_live_gates(settings: Settings, venue: Venue) -> None:
    flag = "COINBASE_LIVE_TRADING" if venue == Venue.COINBASE else "HYPERLIQUID_LIVE_TRADING"
    if not settings.live_flag(venue.value):
        raise LiveTradingDisabled(f"{flag} is not true")
    if settings.dry_run:
        raise LiveTradingDisabled("DRY_RUN is true")
    if kill_switch_active(settings.stop_file):
        raise LiveTradingDisabled(f"kill switch file {settings.stop_file} exists")


def confirm(prompt: str, expected: str, input_fn: Callable[[str], str]) -> bool:
    try:
        return input_fn(prompt).strip() == expected
    except EOFError:
        return False


def cmd_live(args, settings, venue, product, input_fn) -> int:
    check_live_gates(settings, venue)
    verify_sdk(venue)
    adapter = make_adapter(venue, product, settings, authenticated=True)
    meta = load_meta(adapter)
    if meta.post_only:
        raise LiveTradingDisabled(f"{meta.symbol} is post-only; stop-limit orders would be rejected")
    db = Database(settings.database_path)
    halted = db.halt_reason(venue.value, Mode.LIVE.value)
    if halted:
        raise FatalRiskError(f"bot is halted: {halted}. Review, then run --clear-halt.")
    now = datetime.now(timezone.utc)
    print_meta(meta)

    live_equity = adapter.account_equity() if venue == Venue.HYPERLIQUID else None
    inputs = gather_risk_inputs(args, settings, venue, input_fn, live_equity=live_equity)
    active = db.active_run(venue.value, meta.symbol, Mode.LIVE.value)
    if active is not None:
        run_id = active["run_id"]
        plan = db.run_plan(run_id)
        print(f"\nAn active live run {run_id} exists; it will be reconciled and resumed, never duplicated.")
    else:
        run_id = None
        analysis = analyze_market(adapter, meta, settings, now)
        print_analysis(analysis)
        plan = build_plan(analysis, meta, inputs, now)
    print_plan(plan, meta)
    print_intended_orders(plan, venue)
    if plan.refused and active is None:
        print("\nPlan refused by risk rules; nothing will be submitted.")
        return EXIT_REFUSED

    available_quote = adapter.available_quote()
    needed = plan.capital_deployed * (1 + inputs.fee_pct / 100) / plan.leverage
    print(f"\n  available {meta.quote_asset}: {fmt(available_quote, 2)}   required for entries: {fmt(needed, 2)}")
    if active is None and available_quote < needed:
        raise LiveTradingDisabled("available balance does not cover the planned entries")

    if venue == Venue.HYPERLIQUID and settings.hyperliquid_leverage > 1:
        print(f"\n!!! Leverage {settings.hyperliquid_leverage}x: losses are multiplied and liquidation can "
              "happen before the stop executes.")
        if not confirm(f"Type {CONFIRM_LEVERAGE_TEXT} to accept leveraged risk: ", CONFIRM_LEVERAGE_TEXT, input_fn):
            print("Leverage not confirmed. Nothing submitted.")
            return EXIT_REFUSED
    print("\nLIVE TRADING submits real orders with real funds. Stop-limit orders may not fill.")
    if not confirm(f"Type {CONFIRM_TEXT} to enable live trading: ", CONFIRM_TEXT, input_fn):
        print("Confirmation not given. Nothing submitted; run --paper instead.")
        return EXIT_REFUSED

    if venue == Venue.HYPERLIQUID:
        adapter.prepare_live(settings.hyperliquid_leverage)
    if run_id is None:
        run_id = create_run(db, plan, Mode.LIVE, now)
    engine = TradingEngine(db=db, gateway=adapter, meta=meta, settings=settings, mode=Mode.LIVE, run_id=run_id)

    def step(now):
        snapshot = adapter.get_market_meta()
        last = snapshot.mark_price or snapshot.last_price
        if last is None:
            raise LiveTradingDisabled("no current price available")
        report = engine.step(last, now)
        if venue == Venue.HYPERLIQUID and report.position > 0:
            liq = adapter.exchange_liquidation_price()
            if liq is not None and liq >= plan.stop_limit:
                log.critical("exchange liquidation price %s is at/above the stop-limit %s", liq, plan.stop_limit)
                report.messages.append(f"WARNING: exchange liquidation price {liq} >= stop-limit {plan.stop_limit}")
        return report

    return _run_loop(step, settings, args.once, "live step")


def cmd_backtest(args, settings, venue, product, input_fn) -> int:
    adapter = make_adapter(venue, product, settings, authenticated=False)
    meta = load_meta(adapter)
    df = adapter.get_candles(settings.candle_interval, max(args.candles, 200), datetime.now(timezone.utc))
    inputs = gather_risk_inputs(args, settings, venue, input_fn)
    result = run_backtest(df, meta, settings, inputs, interval=settings.candle_interval)
    print(f"\n=== Walk-forward backtest (SIMULATED) {meta.symbol} {settings.candle_interval} x {result.candles} ===")
    print("  Past simulated results do not predict future results. Funding and liquidation are not simulated.")
    for r in result.runs:
        print(f"  {r['run_id']} {r['created_at'][:16]} {r['status']:<7} bought {fmt(r['bought'])} "
              f"realized {fmt(r['realized'], 2)} open {fmt(r['open_position'])}")
    print(f"  runs: {len(result.runs)}   total realized: {fmt(result.total_realized, 2)}   "
          f"open position: {fmt(result.open_position)} (unrealized {fmt(result.unrealized, 2)})")
    print(f"  max drawdown (equity, simulated): {fmt(result.max_drawdown, 2)}")
    if result.skipped_plans:
        print("  candles where no plan was allowed:")
        for reason, n in sorted(result.skipped_plans.items(), key=lambda kv: -kv[1]):
            print(f"    {n:>5} x {reason}")
    return EXIT_OK


def _print_db_state(db: Database, venue: Venue, product: str, mode: Mode) -> None:
    print(f"\n=== {mode.value.upper()} state ({db.path}) ===")
    halted = db.halt_reason(venue.value, mode.value)
    if halted:
        print(f"  HALTED: {halted}")
    runs = db.runs(venue.value, product, mode.value)
    if not runs:
        print("  no runs")
    for run in runs[-5:]:
        position, avg_cost = db.position(run["run_id"])
        print(f"  run {run['run_id']} {run['status']} created {run['created_at'][:19]} "
              f"position {fmt(position)} avg cost {fmt(avg_cost)} realized {fmt(db.realized_for_run(run['run_id']), 2)}")
        for o in db.orders_for_run(run["run_id"]):
            trig = f" trig {fmt(o.trigger_price)}" if o.trigger_price else ""
            print(f"    {o.leg:<4} {o.side.value:<4} {o.order_type.value:<10} {fmt(o.quantity):>14} @ {fmt(o.price)}"
                  f"{trig} filled {fmt(o.filled_quantity)} {o.status.value} id={o.exchange_order_id}"
                  + (f" err={o.error}" if o.error else ""))
    print(f"  realized today: {fmt(db.realized_today(venue.value, mode.value, datetime.now(timezone.utc)), 2)}")


def _has_credentials(settings: Settings, venue: Venue) -> bool:
    if venue == Venue.COINBASE:
        return bool(settings.coinbase_api_key and settings.coinbase_api_secret)
    return bool(settings.hyperliquid_private_key and settings.hyperliquid_account_address)


def cmd_status(args, settings, venue, product, input_fn) -> int:
    product = product.upper()
    for mode, path in ((Mode.LIVE, settings.database_path), (Mode.PAPER, settings.paper_database_path)):
        db = Database(path)
        _print_db_state(db, venue, product, mode)
        db.close()
    if _has_credentials(settings, venue):
        adapter = make_adapter(venue, product, settings, authenticated=True)
        print("\n=== Exchange (read-only) ===")
        for o in adapter.list_open_orders():
            print(f"  open {o.side.value if o.side else '?'} id={o.exchange_order_id} client={o.client_order_id} "
                  f"filled {fmt(o.filled_quantity)}")
        print(f"  position/base available: {fmt(adapter.available_position())}")
        print(f"  quote available: {fmt(adapter.available_quote(), 2)}")
    else:
        print("\n(no credentials configured: exchange state not queried)")
    if kill_switch_active(settings.stop_file):
        print(f"\nKILL SWITCH ACTIVE: {settings.stop_file} exists")
    return EXIT_OK


def cmd_cancel_open(args, settings, venue, product, input_fn) -> int:
    from simulator import SIM_SCHEMA

    product = product.upper()
    now = datetime.now(timezone.utc)
    paper_db = Database(settings.paper_database_path)
    paper_db.conn.executescript(SIM_SCHEMA)
    cur = paper_db.conn.execute(
        "UPDATE sim_orders SET status = 'CANCELLED' WHERE venue = ? AND product = ? AND status = 'OPEN'",
        (venue.value, product))
    paper_db.conn.execute(
        "UPDATE orders SET status = 'CANCELLED', updated_at = ? WHERE venue = ? AND product = ? AND mode = 'paper' "
        "AND status NOT IN ('FILLED', 'CANCELLED', 'EXPIRED', 'REJECTED')", (now.isoformat(), venue.value, product))
    paper_db.conn.commit()
    print(f"Paper: cancelled {cur.rowcount} simulated order(s).")
    if not _has_credentials(settings, venue):
        print("Live: no credentials configured; nothing to cancel.")
        return EXIT_OK
    adapter = make_adapter(venue, product, settings, authenticated=True)
    open_orders = adapter.list_open_orders()
    if not open_orders:
        print("Live: no open orders.")
        return EXIT_OK
    print(f"Live: {len(open_orders)} open order(s) on {product}, including any protective stops.")
    print("Cancelling a stop leaves the position UNPROTECTED.")
    if not args.yes and not confirm("Type CANCEL to cancel them all: ", "CANCEL", input_fn):
        print("Not confirmed; nothing cancelled.")
        return EXIT_REFUSED
    results = adapter.cancel_orders([o.exchange_order_id for o in open_orders])
    for oid, ok in results.items():
        print(f"  {oid}: {'cancelled' if ok else 'FAILED'}")
    db = Database(settings.database_path)
    active = db.active_run(venue.value, product, Mode.LIVE.value)
    if active is not None:
        TradingEngine(db=db, gateway=adapter, meta=load_meta(adapter), settings=settings, mode=Mode.LIVE,
                      run_id=active["run_id"]).reconcile(now)
    return EXIT_OK if all(results.values()) else EXIT_ERROR


def cmd_reset_paper(args, settings, venue, product, input_fn) -> int:
    from simulator import reset_paper_state

    db = Database(settings.paper_database_path)
    reset_paper_state(db, venue, product.upper())
    print(f"Paper state for {venue.value}:{product.upper()} deleted from {settings.paper_database_path}.")
    return EXIT_OK


def cmd_clear_halt(args, settings, venue, product, input_fn) -> int:
    for path, mode in ((settings.database_path, Mode.LIVE), (settings.paper_database_path, Mode.PAPER)):
        db = Database(path)
        reason = db.halt_reason(venue.value, mode.value)
        if reason:
            db.clear_halt(venue.value, mode.value)
            print(f"Cleared {mode.value} halt for {venue.value}: {reason}")
    return EXIT_OK


COMMANDS = {
    "analyze": cmd_analyze, "paper": cmd_paper, "backtest": cmd_backtest, "live": cmd_live,
    "status": cmd_status, "cancel_open": cmd_cancel_open, "reset_paper": cmd_reset_paper,
    "clear_halt": cmd_clear_halt,
}


def main(argv: Optional[list[str]] = None, input_fn: Callable[[str], str] = input,
         settings: Optional[Settings] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        settings = settings or load_settings(args.env_file)
    except (ConfigError, ValueError) as exc:
        setup_logging(args.log_level, None)
        print(f"Configuration error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    setup_logging(args.log_level, settings)
    if not args.venue or not args.product:
        parser.error("--venue and --product are required")
    venue = Venue(args.venue)
    command = next(name for name in COMMANDS if getattr(args, name))
    try:
        return COMMANDS[command](args, settings, venue, args.product, input_fn)
    except MarketUnavailable as exc:
        print(str(exc))
        return EXIT_UNAVAILABLE
    except LiveTradingDisabled as exc:
        print(f"Live trading refused: {exc}. No order was submitted.")
        return EXIT_REFUSED
    except (InvalidMetadata, InsufficientHistory) as exc:
        print(f"Refusing: {exc}")
        return EXIT_REFUSED
    except KillSwitchTriggered as exc:
        print(f"KILL SWITCH: {exc}")
        return EXIT_KILLED
    except FatalRiskError as exc:
        print(f"HALTED: {exc}")
        return EXIT_HALTED
    except (ConfigError, BotError) as exc:
        print(f"Error: {exc}")
        return EXIT_ERROR
    except requests.exceptions.RequestException as exc:
        print(f"Network/API error ({type(exc).__name__}); nothing was changed. Check connectivity and retry.")
        return EXIT_ERROR
