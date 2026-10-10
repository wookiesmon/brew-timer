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
                                                  settings.hyperliquid_private_key, settings.coingecko_api_key)
                   if s is not None]
        handler.addFilter(RedactSecrets(secrets))
    handlers: list[logging.Handler] = [handler]
    if settings is not None and settings.log_file is not None:
        file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
        file_handler.setFormatter(handler.formatter)
        for f in handler.filters:
            file_handler.addFilter(f)
        handlers.append(file_handler)
    root = logging.getLogger()
    root.handlers[:] = handlers
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
    actions.add_argument("--check", action="store_true", help="pre-flight report (config, data, keys); never trades")
    actions.add_argument("--screen", action="store_true",
                         help="rank coins tradable on the venue by CoinGecko liquidity; never trades")
    actions.add_argument("--preview", action="store_true", help="Coinbase: validate planned orders without placing")
    p.add_argument("--equity", help="account equity in USD (default ACCOUNT_EQUITY_USD)")
    p.add_argument("--max-allocation", help="maximum USD to deploy (capped by MAX_ALLOCATION_PCT)")
    p.add_argument("--max-loss", help="maximum planned loss in USD (capped by MAX_PLANNED_LOSS_PCT)")
    p.add_argument("--risk-pct", help="optional risk percentage of equity (<= MAX_PLANNED_LOSS_PCT)")
    p.add_argument("--ask", action="store_true", help="prompt for equity, allocation and loss")
    p.add_argument("--once", action="store_true", help="paper/live: run a single step and exit")
    p.add_argument("--max-runs", type=int, default=1,
                   help="paper/live: trade up to N plans in this session (default 1)")
    p.add_argument("--candles", type=int, default=1000, help="backtest: number of candles to fetch")
    p.add_argument("--products", help="backtest: comma-separated products, e.g. BTC-USD,ETH-USD,SOL-USD")
    p.add_argument("--compare", action="store_true",
                   help="backtest: compare trend filters and exit rules, ranked by out-of-sample results")
    p.add_argument("--fee-pct", help="backtest: fee %% per order to assume, or a list like 1.2,0.6,0.045")
    p.add_argument("--limit", type=int, default=20, help="--screen: number of rows")
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


def paper_tick(adapter, sim, db: Database, session, settings: Settings, now: datetime):
    from execution import candle_row

    key = f"sim_cursor:{session.meta.venue.value}:{session.meta.symbol}"
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
    return session.step(last_price, now)


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
    coingecko_gate(settings, meta, plan)
    print_plan(plan, meta)
    print_intended_orders(plan, venue)
    print("\nAnalysis only: no orders were created.")
    return EXIT_OK


MAX_CONSECUTIVE_ERRORS = 10


def transient_errors() -> tuple:
    errors: list = [requests.exceptions.RequestException, InvalidMetadata, InsufficientHistory]
    try:
        from hyperliquid.utils.error import Error as HyperliquidError

        errors.append(HyperliquidError)
    except ImportError:  # pragma: no cover
        pass
    return tuple(errors)


def _run_loop(step: Callable[[datetime], object], settings: Settings, once: bool, label: str,
              sleep: Callable[[float], None] = time.sleep) -> int:
    """Poll until the session is done. Temporary API/network failures are logged and retried;
    orders already resting on the exchange (including the protective stop) keep working."""
    retryable = transient_errors()
    failures = 0
    while True:
        now = datetime.now(timezone.utc)
        try:
            report = step(now)
            failures = 0
        except KeyboardInterrupt:
            print("\nStopped by user. Open orders REMAIN on the venue; use --status or --cancel-open.")
            return EXIT_OK
        except KillSwitchTriggered as exc:
            print(f"\nKILL SWITCH: {exc}")
            return EXIT_KILLED
        except FatalRiskError as exc:
            print(f"\nHALTED: {exc}\nThe bot will not restart on its own. Review, then run --clear-halt.")
            return EXIT_HALTED
        except retryable as exc:
            failures += 1
            log.error("step failed (%s); attempt %d/%d", type(exc).__name__, failures, MAX_CONSECUTIVE_ERRORS)
            print(f"[{now:%Y-%m-%d %H:%M:%S}Z] {label}: temporary error {type(exc).__name__} "
                  f"({failures}/{MAX_CONSECUTIVE_ERRORS}); resting orders keep working")
            if once or failures >= MAX_CONSECUTIVE_ERRORS:
                print("Giving up. Open orders REMAIN on the venue; check --status and the exchange UI.")
                return EXIT_ERROR
        else:
            print(f"[{now:%Y-%m-%d %H:%M:%S}Z] {label}")
            print_report(report)
            if report.status == "DONE":
                print("Session complete.")
                return EXIT_OK
            if once:
                return EXIT_OK
        try:
            sleep(settings.poll_seconds)
        except KeyboardInterrupt:
            print("\nStopped by user. Open orders REMAIN on the venue; use --status or --cancel-open.")
            return EXIT_OK


def print_market_check(check) -> None:
    print("\n=== CoinGecko cross-check (data only) ===")
    print(f"  coin id               {check.coin_id}")
    print(f"  CoinGecko price       {fmt(check.reference_price)}   venue price {fmt(check.venue_price)}"
          + (f"   deviation {check.deviation_pct:.2f}%" if check.deviation_pct is not None else ""))
    print(f"  24h volume (all)      {fmt(check.total_volume_usd, 0)} USD   market cap {fmt(check.market_cap_usd, 0)} USD")
    if check.venue_volume_usd is not None:
        print(f"  24h volume (Coinbase) {fmt(check.venue_volume_usd, 0)} USD")
    for note in check.notes:
        print(f"  - {note}")
    for problem in check.problems:
        print(f"  ! {problem}")
    print("  result                " + ("OK" if check.ok else "REFUSE new plans"))


_COINGECKO_CLIENTS: dict[int, object] = {}


def coingecko_client(settings: Settings):
    """One client per settings object, so its response cache spans the whole session."""
    from coingecko import CoinGeckoClient

    if id(settings) not in _COINGECKO_CLIENTS:
        _COINGECKO_CLIENTS[id(settings)] = CoinGeckoClient(settings)
    return _COINGECKO_CLIENTS[id(settings)]


def coingecko_gate(settings: Settings, meta: MarketMeta, plan: Optional[TradePlan]):
    """When COINGECKO_ENABLED, refuse plans on thin or mispriced markets. Fails closed."""
    if not settings.coingecko_enabled:
        return None
    from coingecko import check_market

    check = check_market(coingecko_client(settings), meta, settings,
                         planned_notional=plan.capital_deployed if plan else None)
    print_market_check(check)
    if plan is not None and not check.ok:
        plan.refused = True
        plan.refusal_reasons.extend(f"CoinGecko: {p}" for p in check.problems)
    return check


def make_plan_factory(adapter, meta: MarketMeta, settings: Settings, inputs_fn: Callable[[], RiskInputs],
                      *, verbose: bool, balance_check: Optional[Callable[[TradePlan, RiskInputs], Optional[str]]] = None):
    """Fresh analysis -> plan for each new run. Returns None (with a printed reason) if refused."""

    def factory(now: datetime) -> Optional[TradePlan]:
        analysis = analyze_market(adapter, meta, settings, now)
        inputs = inputs_fn()
        plan = build_plan(analysis, meta, inputs, now)
        if not plan.refused:
            coingecko_gate(settings, adapter.get_market_meta(), plan)
        if verbose or not plan.refused:
            print_analysis(analysis)
            print_plan(plan, meta)
            print_intended_orders(plan, meta.venue)
        if not plan.refused and balance_check is not None:
            problem = balance_check(plan, inputs)
            if problem:
                plan.refused = True
                plan.refusal_reasons.append(problem)
        return plan

    return factory


def cmd_paper(args, settings, venue, product, input_fn) -> int:
    from execution import RunSession

    adapter = make_adapter(venue, product, settings, authenticated=False)
    meta = load_meta(adapter)
    db = Database(settings.paper_database_path)
    now = datetime.now(timezone.utc)
    clock = {"now": now}
    inputs = gather_risk_inputs(args, settings, venue, input_fn)
    factory = make_plan_factory(adapter, meta, settings, lambda: inputs, verbose=False)
    active = db.active_run(venue.value, meta.symbol, Mode.PAPER.value)
    if active is not None:
        run_id = active["run_id"]
        print(f"Resuming paper run {run_id} (state reconciled; no duplicate orders will be created).")
    else:
        print_meta(meta)
        plan = factory(now)
        if plan.refused:
            print("\nPlan refused:")
            for reason in plan.refusal_reasons:
                print(f"  - {reason}")
            if args.max_runs <= 1:
                return EXIT_REFUSED
            run_id = None
            print("Waiting for an allowed setup (--max-runs > 1).")
        else:
            run_id = create_run(db, plan, Mode.PAPER, now)
    sim = make_sim(db, meta, settings, inputs, lambda: clock["now"])
    session = RunSession(db=db, gateway=sim, meta=meta, settings=settings, mode=Mode.PAPER,
                         plan_factory=factory, run_id=run_id, max_runs=args.max_runs)
    print(f"\nPAPER MODE: orders are simulated and stored in {settings.paper_database_path}. "
          "No order endpoint is ever called.")

    def step(now):
        clock["now"] = now
        return paper_tick(adapter, sim, db, session, settings, now)

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


def preflight_credentials(adapter, venue: Venue) -> None:
    """Refuse keys that could move funds out of the account."""
    if venue == Venue.COINBASE:
        adapter.check_key_permissions()
    else:
        adapter.check_api_wallet()


def cmd_live(args, settings, venue, product, input_fn) -> int:
    from execution import RunSession

    check_live_gates(settings, venue)
    verify_sdk(venue)
    adapter = make_adapter(venue, product, settings, authenticated=True)
    preflight_credentials(adapter, venue)
    meta = load_meta(adapter)
    if meta.post_only:
        raise LiveTradingDisabled(f"{meta.symbol} is post-only; stop-limit orders would be rejected")
    db = Database(settings.database_path)
    halted = db.halt_reason(venue.value, Mode.LIVE.value)
    if halted:
        raise FatalRiskError(f"bot is halted: {halted}. Review, then run --clear-halt.")
    now = datetime.now(timezone.utc)
    print_meta(meta)

    base_inputs = gather_risk_inputs(args, settings, venue, input_fn)

    def current_inputs() -> RiskInputs:
        if venue == Venue.HYPERLIQUID:  # never size from more than the account actually holds
            equity = min(base_inputs.account_equity, adapter.account_equity())
            return risk_inputs_from_settings(
                settings, venue, equity=equity, max_allocation_usd=base_inputs.max_allocation_usd,
                max_planned_loss_usd=base_inputs.max_planned_loss_usd)
        return base_inputs

    def balance_check(plan: TradePlan, inputs: RiskInputs) -> Optional[str]:
        available = adapter.available_quote()
        needed = plan.capital_deployed * (1 + inputs.fee_pct / 100) / plan.leverage
        print(f"\n  available {meta.quote_asset}: {fmt(available, 2)}   required for entries: {fmt(needed, 2)}")
        return None if available >= needed else "available balance does not cover the planned entries"

    factory = make_plan_factory(adapter, meta, settings, current_inputs, verbose=False, balance_check=balance_check)
    active = db.active_run(venue.value, meta.symbol, Mode.LIVE.value)
    if active is not None:
        run_id = active["run_id"]
        plan = db.run_plan(run_id)
        print(f"\nAn active live run {run_id} exists; it will be reconciled and resumed, never duplicated.")
        print_plan(plan, meta)
        print_intended_orders(plan, venue)
    else:
        run_id = None
        plan = factory(now)
        if plan.refused:
            print("\nPlan refused; nothing will be submitted:")
            for reason in plan.refusal_reasons:
                print(f"  - {reason}")
            return EXIT_REFUSED

    if venue == Venue.HYPERLIQUID and settings.hyperliquid_leverage > 1:
        print(f"\n!!! Leverage {settings.hyperliquid_leverage}x: losses are multiplied and liquidation can "
              "happen before the stop executes.")
        if not confirm(f"Type {CONFIRM_LEVERAGE_TEXT} to accept leveraged risk: ", CONFIRM_LEVERAGE_TEXT, input_fn):
            print("Leverage not confirmed. Nothing submitted.")
            return EXIT_REFUSED
    print("\nLIVE TRADING submits real orders with real funds. Stop-limit orders may not fill.")
    if args.max_runs > 1:
        print(f"This session may start up to {args.max_runs} runs. Each new plan follows the same rules and "
              "limits and is submitted WITHOUT asking again. MAX_DAILY_LOSS_USD still halts everything.")
    if not confirm(f"Type {CONFIRM_TEXT} to enable live trading: ", CONFIRM_TEXT, input_fn):
        print("Confirmation not given. Nothing submitted; run --paper instead.")
        return EXIT_REFUSED

    if venue == Venue.HYPERLIQUID:
        adapter.prepare_live(settings.hyperliquid_leverage)
    if run_id is None:
        run_id = create_run(db, plan, Mode.LIVE, now)
    session = RunSession(db=db, gateway=adapter, meta=meta, settings=settings, mode=Mode.LIVE,
                         plan_factory=factory, run_id=run_id, max_runs=args.max_runs)

    def step(now):
        snapshot = adapter.get_market_meta()
        last = snapshot.mark_price or snapshot.last_price
        if last is None:
            raise InvalidMetadata("no current price available")
        report = session.step(last, now)
        if venue == Venue.HYPERLIQUID and report.position > 0 and session.plan is not None:
            liq = adapter.exchange_liquidation_price()
            if liq is not None and liq >= session.plan.stop_limit:
                log.critical("exchange liquidation price %s is at/above the stop-limit %s", liq, session.plan.stop_limit)
                report.messages.append(f"WARNING: exchange liquidation price {liq} >= stop-limit {session.plan.stop_limit}")
        return report

    return _run_loop(step, settings, args.once, "live step")


def cmd_preview(args, settings, venue, product, input_fn) -> int:
    """Validate the planned entries with Coinbase's order-preview endpoint. Never places orders."""
    if venue != Venue.COINBASE:
        print("Hyperliquid has no order preview. Rehearse with HYPERLIQUID_TESTNET=true and a testnet API wallet.")
        return EXIT_REFUSED
    verify_sdk(venue)
    adapter = make_adapter(venue, product, settings, authenticated=True)
    preflight_credentials(adapter, venue)
    meta = load_meta(adapter)
    now = datetime.now(timezone.utc)
    analysis = analyze_market(adapter, meta, settings, now)
    plan = build_plan(analysis, meta, gather_risk_inputs(args, settings, venue, input_fn), now)
    coingecko_gate(settings, meta, plan)
    print_plan(plan, meta)
    if plan.refused:
        print("\nPlan refused; previewing anyway so you can see what Coinbase would say.")
    print("\n=== Coinbase order preview (nothing is placed) ===")
    ok = True
    for entry in plan.entries:
        if entry.quantity <= 0:
            continue
        result = adapter.preview_limit_buy(entry.quantity, entry.price)
        status = "OK" if not result["errors"] else "REJECTED"
        ok = ok and not result["errors"]
        print(f"  {entry.leg} BUY {fmt(entry.quantity)} @ {fmt(entry.price)}: {status} "
              f"total {result['order_total']} fees {result['commission_total']}")
        for err in result["errors"]:
            print(f"    error: {err}")
        for warning in result["warnings"]:
            print(f"    warning: {warning}")
    print("  Exits are sells of coins you will only hold after fills, so they cannot be previewed now.")
    return EXIT_OK if ok else EXIT_REFUSED


def cmd_screen(args, settings, venue, product, input_fn) -> int:
    """Rank coins tradable on the venue by liquidity using CoinGecko. Never trades."""
    from coingecko import CoinGeckoClient, screen

    adapter = make_adapter(venue, product or ("BTC-USD" if venue == Venue.COINBASE else "BTC"), settings,
                           authenticated=False)
    symbols = adapter.list_tradable_symbols()
    print(f"{len(symbols)} {'USD spot products' if venue == Venue.COINBASE else 'active perps'} on {venue.value}; "
          "ranking by CoinGecko 24h volume...")
    rows = screen(CoinGeckoClient(settings), symbols, settings, limit=args.limit, venue=venue,
                  progress=lambda sym: log.debug("fetching venue volume for %s", sym))
    if not rows:
        print("No tradable coin passed COINGECKO_MIN_VOLUME_USD.")
        return EXIT_OK
    venue_col = "Coinbase vol" if venue == Venue.COINBASE else ""
    print(f"\n  {'#':>2} {'product':<12}{'price':>14}{'24h %':>9}{'24h vol (all)':>17}{'mkt cap':>17}  {venue_col}")
    for i, r in enumerate(rows, 1):
        change = f"{r.change_24h_pct:+.1f}" if r.change_24h_pct is not None else "n/a"
        venue_vol = fmt(r.venue_volume_usd, 0) if r.venue_volume_usd is not None else ""
        flag = "  (symbol shared by several coins; pin with COINGECKO_COIN_IDS)" if r.ambiguous else ""
        print(f"  {i:>2} {r.venue_symbol:<12}{fmt(r.price):>14}{change:>9}{fmt(r.total_volume_usd, 0):>17}"
              f"{fmt(r.market_cap_usd, 0):>17}  {venue_vol}{flag}")
    print("\nA liquidity screen, not a recommendation. Run --analyze on a product before paper trading it.")
    return EXIT_OK


def cmd_check(args, settings, venue, product, input_fn) -> int:
    """Pre-flight report: configuration, SDK, market data, credentials, live gates. Never trades."""
    results: list[tuple[str, str, str]] = []

    def check(name: str, fn: Callable[[], str]) -> None:
        try:
            results.append(("PASS", name, fn() or ""))
        except Exception as exc:  # noqa: BLE001 - the report shows every failure
            results.append(("FAIL", name, f"{type(exc).__name__}: {exc}"[:200]))

    def skip(name: str, why: str) -> None:
        results.append(("SKIP", name, why))

    check("installed SDK has every method used", lambda: verify_sdk(venue) or "")
    public = make_adapter(venue, product, settings, authenticated=False)
    meta_box: dict = {}

    def market() -> str:
        meta_box["meta"] = load_meta(public)
        m = meta_box["meta"]
        return f"{m.symbol} {m.product_type} tradable, last {fmt(m.last_price)}"

    check("market listed and tradable", market)
    if "meta" in meta_box:
        check("candle history", lambda: f"{len(public.get_candles(settings.candle_interval, TARGET_CANDLES))} "
                                        f"closed {settings.candle_interval} candles")
    if settings.coingecko_enabled and "meta" in meta_box:
        def gecko() -> str:
            from coingecko import CoinGeckoClient, check_market

            result = check_market(CoinGeckoClient(settings), meta_box["meta"], settings)
            if not result.ok:
                raise RuntimeError("; ".join(result.problems))
            dev = f", deviation {result.deviation_pct:.2f}%" if result.deviation_pct is not None else ""
            return f"{result.coin_id}: volume {fmt(result.total_volume_usd, 0)} USD{dev}"

        check("CoinGecko cross-check (liquidity, price sanity)", gecko)
    elif not settings.coingecko_enabled:
        skip("CoinGecko cross-check", "COINGECKO_ENABLED=false")
    if _has_credentials(settings, venue):
        auth = make_adapter(venue, product, settings, authenticated=True)
        if venue == Venue.COINBASE:
            def perms() -> str:
                auth.check_key_permissions()
                p = auth.key_permissions()
                return f"view={p.get('can_view')} trade={p.get('can_trade')} transfer={p.get('can_transfer')}"

            check("API key is trade-only (no transfer)", perms)
        else:
            check("API wallet (cannot withdraw) is used", lambda: auth.check_api_wallet() or
                  f"signer {auth.signer_address()[:8]}... trades for {settings.hyperliquid_account_address[:8]}...")
            check("account equity", lambda: f"{fmt(auth.account_equity(), 2)} USDC")
        if "meta" in meta_box:
            check("available balance", lambda: f"quote {fmt(auth.available_quote(), 2)}, "
                                               f"base/position {fmt(auth.available_position())}")
    else:
        skip("credentials", "not configured (only needed for --live, --preview and --status)")
    flag = "COINBASE_LIVE_TRADING" if venue == Venue.COINBASE else "HYPERLIQUID_LIVE_TRADING"
    results.append(("INFO", flag, str(settings.live_flag(venue.value)).lower()))
    results.append(("INFO", "DRY_RUN", str(settings.dry_run).lower()))
    results.append(("INFO", "kill switch", "ACTIVE" if kill_switch_active(settings.stop_file) else "not present"))
    db = Database(settings.database_path)
    results.append(("INFO", "live halt", db.halt_reason(venue.value, Mode.LIVE.value) or "none"))
    db.close()
    results.append(("INFO", "risk limits",
                    f"equity {settings.account_equity_usd}, alloc {settings.max_allocation_pct}%, "
                    f"loss/trade {settings.max_planned_loss_pct}%, daily loss {settings.max_daily_loss_usd}, "
                    f"max notional {settings.max_position_notional_usd}, leverage {settings.hyperliquid_leverage}x"))
    print(f"\n=== Pre-flight check: {venue.value} {product.upper()} ===")
    for status, name, detail in results:
        print(f"  [{status}] {name}" + (f": {detail}" if detail else ""))
    failed = any(status == "FAIL" for status, _, _ in results)
    print("\nResult: " + ("problems found (see FAIL lines)." if failed else "no blocking problems found."))
    return EXIT_ERROR if failed else EXIT_OK


COMPARE_GRID = (  # (trend filter, breakeven after TP1, trailing stop in ATR)
    ("off", False, Decimal(0)),
    ("ema", False, Decimal(0)),
    ("ema200", False, Decimal(0)),
    ("off", True, Decimal(2)),
    ("ema", True, Decimal(2)),
    ("ema200", True, Decimal(2)),
)


def _signed(value: Optional[Decimal], places: int = 2) -> str:
    return "n/a" if value is None else f"{value:+.{places}f}"


def _pf(stats) -> str:
    if stats.profit_factor is not None:
        return f"{stats.profit_factor:.2f}"
    return "inf" if stats.wins else "n/a"


def config_label(trend: str, breakeven: bool, trail: Decimal) -> str:
    exits = "fixed TPs" if not breakeven and not trail else (
        ("breakeven" if breakeven else "") + ("+" if breakeven and trail else "") + (f"trail {trail}ATR" if trail else ""))
    return f"trend={trend:<6} exits={exits}"


def print_backtest_report(r, interval: str, label: str = "") -> None:
    s = r.stats
    print(f"\n=== Walk-forward backtest (SIMULATED) {r.symbol} {interval} x {r.candles} candles {label}===")
    print(f"  trades            {s.trades} (wins {s.wins}, losses {s.losses})   win rate "
          f"{'n/a' if s.win_rate is None else f'{s.win_rate:.1f}%'}   profit factor {_pf(s)}")
    print(f"  avg trade         {_signed(s.expectancy)}   avg win {_signed(s.avg_win)}   avg loss {_signed(s.avg_loss)}"
          f"   fees paid {fmt(s.fees, 2)}")
    print(f"  net P/L           {_signed(s.net_pnl)} ({r.return_pct:+.2f}% of equity incl. open position)   "
          f"max drawdown {fmt(r.max_drawdown, 2)} ({r.max_drawdown_pct:.2f}%)   time in market {r.exposure_pct:.0f}%")
    for name, part in (("in-sample (70%)", r.in_sample), ("out-of-sample (30%)", r.out_of_sample)):
        print(f"  {name:<21}{part.trades} trades, net {_signed(part.net_pnl)}, profit factor {_pf(part)}")
    print(f"  buy & hold        {_signed(r.buy_hold_pnl)} holding the same max allocation "
          f"(asset {r.asset_change_pct:+.1f}% over the period)")
    if r.open_position > 0:
        print(f"  open at end       {fmt(r.open_position)} units, P/L so far {_signed(r.unrealized)} (not counted as a trade)")
    if not s.enough_trades:
        print(f"  ! only {s.trades} closed trades: too few to tell skill from luck (want 30+)")
    if r.skipped_plans:
        print("  candles where no plan was allowed:")
        for reason, n in sorted(r.skipped_plans.items(), key=lambda kv: -kv[1])[:5]:
            print(f"    {n:>5} x {reason}")


def _fee_list(raw: Optional[str]) -> list[Optional[Decimal]]:
    if not raw:
        return [None]
    out = []
    for part in raw.split(","):
        value = _decimal_arg(part.strip(), "--fee-pct")
        out.append(value)
    return out


def cmd_backtest(args, settings, venue, product, input_fn) -> int:
    import dataclasses

    from metrics import MIN_MEANINGFUL_TRADES, merge

    products = [p.strip() for p in (args.products or product or "").split(",") if p.strip()]
    if not products:
        raise ConfigError("give --product or --products")
    base_inputs = gather_risk_inputs(args, settings, venue, input_fn)
    data = []
    for name in products:
        try:
            adapter = make_adapter(venue, name, settings, authenticated=False)
            meta = load_meta(adapter)
            df = adapter.get_candles(settings.candle_interval, max(args.candles, 200), datetime.now(timezone.utc))
        except (MarketUnavailable, InvalidMetadata, InsufficientHistory) as exc:
            print(f"Skipping {name}: {exc}")
            continue
        data.append((meta, df))
    if not data:
        return EXIT_UNAVAILABLE

    configs = COMPARE_GRID if args.compare else (
        (settings.trend_filter, settings.breakeven_after_tp1, settings.trail_atr_multiple),)
    rows = []
    for fee in _fee_list(args.fee_pct):
        for trend, breakeven, trail in configs:
            run_settings = settings.model_copy(update={
                "trend_filter": trend, "breakeven_after_tp1": breakeven, "trail_atr_multiple": trail,
                **({"coinbase_fee_pct": fee, "hyperliquid_fee_pct": fee} if fee is not None else {}),
            })
            inputs = dataclasses.replace(base_inputs, trend_filter=trend,
                                         fee_pct=fee if fee is not None else base_inputs.fee_pct)
            label = config_label(trend, breakeven, trail) + f" fee={inputs.fee_pct}%"
            if args.compare:
                print(f"  running {label} ...", flush=True)
            results = [run_backtest(df, meta, run_settings, inputs, interval=settings.candle_interval)
                       for meta, df in data]
            if not args.compare:
                for r in results:
                    print_backtest_report(r, settings.candle_interval, f"[{label}] ")
            rows.append((label, results))

    print("\nPast simulated results do not predict future results. Funding and liquidation are not simulated.")
    if not args.compare and len(data) == 1:
        return EXIT_OK

    print(f"\n=== {'Comparison' if args.compare else 'Summary'} across {', '.join(m.symbol for m, _ in data)} "
          f"({settings.candle_interval}, SIMULATED) ===")
    print("  Choose rules by the OUT-OF-SAMPLE columns (data the rules were not picked on), and only")
    print(f"  trust rows with {MIN_MEANINGFUL_TRADES}+ trades. Compare net P/L with buy & hold.")
    header = (f"  {'rules':<56}{'trades':>7}{'win%':>7}{'PF':>6}{'avg':>9}{'net':>10}"
              f"{'OOS tr':>8}{'OOS PF':>8}{'OOS net':>10}{'maxDD%':>8}{'B&H':>10}")
    print(header)
    summary = []
    for label, results in rows:
        allstats = merge(r.stats for r in results)
        oos = merge(r.out_of_sample for r in results)
        dd = max(r.max_drawdown_pct for r in results)
        bh = sum((r.buy_hold_pnl for r in results), Decimal(0))
        summary.append((oos.net_pnl, label, allstats, oos, dd, bh))
    for _, label, st, oos, dd, bh in sorted(summary, key=lambda x: x[0], reverse=True):
        flag = "" if st.enough_trades else "  (few trades)"
        win = "n/a" if st.win_rate is None else f"{st.win_rate:.0f}"
        print(f"  {label:<56}{st.trades:>7}{win:>7}{_pf(st):>6}{_signed(st.expectancy):>9}{_signed(st.net_pnl):>10}"
              f"{oos.trades:>8}{_pf(oos):>8}{_signed(oos.net_pnl):>10}{dd:>8.1f}{_signed(bh):>10}{flag}")
    print("\n  PF = profit factor (gains / losses after fees; above 1.0 is profitable). avg = net P/L per trade.")
    print("  To adopt a row, set TREND_FILTER, BREAKEVEN_AFTER_TP1 and TRAIL_ATR_MULTIPLE in .env, then paper-trade it.")
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
    "clear_halt": cmd_clear_halt, "check": cmd_check, "preview": cmd_preview, "screen": cmd_screen,
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
    if not args.venue or (not args.product and not args.screen and not (args.backtest and args.products)):
        parser.error("--venue and --product are required")
    if args.max_runs < 1:
        parser.error("--max-runs must be at least 1")
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
