"""Precision rounding, position sizing, plan construction and hard risk limits.

All calculations use Decimal. Every output is a rule-based scenario, not a forecast.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import ROUND_FLOOR, Decimal
from pathlib import Path
from typing import Optional

from analysis import MarketAnalysis
from config import Settings
from models import (
    InvalidMetadata,
    KillSwitchTriggered,
    MarketMeta,
    OrderRole,
    OrderType,
    PlannedOrder,
    RiskRejected,
    Side,
    TradePlan,
    Venue,
)

ENTRY_ATR_OFFSETS = (Decimal("0.5"), Decimal("1.0"), Decimal("1.5"))
ENTRY_WEIGHTS = (Decimal("0.40"), Decimal("0.35"), Decimal("0.25"))
TP_WEIGHTS = (Decimal("0.40"), Decimal("0.35"), Decimal("0.25"))
STOP_ATR_BELOW_LOWEST_ENTRY = Decimal("0.5")
STOP_BUFFER_ATR = Decimal("0.25")
HL_PRICE_SIG_FIGS = 5
HL_PERP_MAX_PRICE_DECIMALS = 6

STOP_LIMIT_WARNING = (
    "A stop-limit order is NOT a guaranteed exit: if price gaps or falls through the limit "
    "price, or liquidity disappears, the order can remain unfilled while losses grow."
)
SCENARIO_LABEL = (
    "Automated rule-based scenario from historical candles. Not a forecast, not financial "
    "advice, and not a statement that this trade suits you."
)


# ------------------------------------------------------------------- rounding
def floor_to_increment(value: Decimal, increment: Decimal) -> Decimal:
    """Round ``value`` down to a multiple of ``increment`` (never up)."""
    if increment is None or increment <= 0:
        raise InvalidMetadata(f"invalid increment {increment!r}")
    units = (value / increment).to_integral_value(rounding=ROUND_FLOOR)
    return units * increment


def hl_floor_price(price: Decimal, sz_decimals: int) -> Decimal:
    """Hyperliquid perp price rule: at most 5 significant figures and at most
    (6 - szDecimals) decimals; integer prices are always valid. Rounds down."""
    if price <= 0:
        raise InvalidMetadata(f"price must be positive, got {price}")
    max_decimals = HL_PERP_MAX_PRICE_DECIMALS - sz_decimals
    sig_decimals = HL_PRICE_SIG_FIGS - 1 - price.adjusted()
    decimals = max(0, min(max_decimals, sig_decimals))
    return price.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_FLOOR)


def round_price(meta: MarketMeta, price: Decimal) -> Decimal:
    if meta.price_increment is not None:
        return floor_to_increment(price, meta.price_increment)
    if meta.sz_decimals is None:
        raise InvalidMetadata(f"{meta.symbol}: no price precision available")
    return hl_floor_price(price, meta.sz_decimals)


def round_size(meta: MarketMeta, quantity: Decimal) -> Decimal:
    return floor_to_increment(quantity, meta.size_increment)


def meets_minimums(meta: MarketMeta, quantity: Decimal, price: Decimal) -> bool:
    return quantity > 0 and quantity >= meta.min_size and quantity * price >= meta.min_notional


# --------------------------------------------------------------- risk inputs
@dataclass(frozen=True)
class RiskInputs:
    account_equity: Decimal
    max_allocation_usd: Decimal
    max_planned_loss_usd: Decimal
    max_position_notional_usd: Decimal
    fee_pct: Decimal
    slippage_pct: Decimal
    stop_buffer_pct: Decimal
    leverage: int = 1


def risk_inputs_from_settings(
    settings: Settings, venue: Venue, *, equity: Optional[Decimal] = None,
    max_allocation_usd: Optional[Decimal] = None, max_planned_loss_usd: Optional[Decimal] = None,
    risk_pct: Optional[Decimal] = None,
) -> RiskInputs:
    equity = equity if equity is not None else settings.account_equity_usd
    if equity <= 0:
        raise RiskRejected("account equity must be positive")
    allocation_cap = equity * settings.max_allocation_pct / 100
    allocation = min(max_allocation_usd, allocation_cap) if max_allocation_usd is not None else allocation_cap
    loss_cap = equity * settings.max_planned_loss_pct / 100
    if risk_pct is not None:
        if not (Decimal(0) < risk_pct <= settings.max_planned_loss_pct):
            raise RiskRejected(
                f"risk percentage must be in (0, {settings.max_planned_loss_pct}] (MAX_PLANNED_LOSS_PCT)"
            )
        loss_cap = equity * risk_pct / 100
    loss = min(max_planned_loss_usd, loss_cap) if max_planned_loss_usd is not None else loss_cap
    if allocation <= 0 or loss <= 0:
        raise RiskRejected("maximum allocation and maximum planned loss must be positive")
    return RiskInputs(
        account_equity=equity,
        max_allocation_usd=allocation,
        max_planned_loss_usd=loss,
        max_position_notional_usd=settings.max_position_notional_usd,
        fee_pct=settings.fee_pct(venue.value),
        slippage_pct=settings.slippage_pct,
        stop_buffer_pct=settings.stop_buffer_pct,
        leverage=settings.hyperliquid_leverage if venue == Venue.HYPERLIQUID else 1,
    )


# ------------------------------------------------------------- core formulas
def staged_entries(price: Decimal, atr: Decimal) -> list[Decimal]:
    return [price - k * atr for k in ENTRY_ATR_OFFSETS]


def weighted_average(prices: list[Decimal], weights: list[Decimal]) -> Decimal:
    total = sum(weights, Decimal(0))
    if total <= 0:
        raise ValueError("weights must sum to a positive number")
    return sum((p * w for p, w in zip(prices, weights)), Decimal(0)) / total


def stop_levels(lowest_entry: Decimal, atr: Decimal, stop_buffer_pct: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """(stop trigger, stop-limit price, buffer). Buffer = max(pct of trigger, 0.25 ATR)."""
    trigger = lowest_entry - STOP_ATR_BELOW_LOWEST_ENTRY * atr
    buffer = max(trigger * stop_buffer_pct / 100, STOP_BUFFER_ATR * atr)
    return trigger, trigger - buffer, buffer


def worst_case_unit_loss(avg_entry: Decimal, stop_limit: Decimal, fee_pct: Decimal, slippage_pct: Decimal) -> Decimal:
    """Loss per unit if the stop-limit fills at its limit, after fees on both legs and slippage."""
    fee = fee_pct / 100
    return (avg_entry - stop_limit) + avg_entry * fee + stop_limit * fee + stop_limit * slippage_pct / 100


def approx_isolated_long_liquidation(avg_entry: Decimal, leverage: int, max_leverage: int) -> Decimal:
    """Conservative approximation, NOT the exchange's figure.

    Isolated long: equity at liquidation equals maintenance margin, with the
    maintenance rate taken as 1 / (2 * max leverage). At 1x this is 0 (no liquidation
    before the asset reaches zero). The live engine prefers the exchange-reported
    liquidationPx once a position exists.
    """
    if leverage < 1 or max_leverage < 1:
        raise ValueError("leverage must be >= 1")
    maintenance = Decimal(1) / (2 * max_leverage)
    liq = avg_entry * (1 - Decimal(1) / leverage) / (1 - maintenance)
    return max(liq, Decimal(0))


def split_quantity(total: Decimal, weights: tuple[Decimal, ...], meta: MarketMeta) -> list[Decimal]:
    """Split ``total`` by weights, flooring each part; the last part takes the remainder."""
    parts = [round_size(meta, total * w) for w in weights[:-1]]
    parts.append(round_size(meta, total - sum(parts, Decimal(0))))
    return parts


# ------------------------------------------------------------------ the plan
def build_plan(analysis: MarketAnalysis, meta: MarketMeta, inputs: RiskInputs, now: Optional[datetime] = None) -> TradePlan:
    """Build a staged long plan. Never raises for risk reasons: returns ``refused=True``
    with reasons so the operator can see the levels that were rejected."""
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    warnings: list[str] = [STOP_LIMIT_WARNING]
    price = Decimal(str(analysis.last_close))
    atr_value = Decimal(str(analysis.atr))

    if analysis.extended:
        reasons.append("Market is extended; no automatic market entry will be created.")
    if analysis.illiquid:
        reasons.append("Market looks illiquid; no entry plan will be created.")
    if atr_value <= 0:
        reasons.append("ATR is zero; risk cannot be calculated.")
    if meta.venue == Venue.COINBASE and meta.product_type != "SPOT":
        reasons.append("Coinbase module is spot-only.")
    if meta.venue == Venue.HYPERLIQUID:
        if inputs.leverage < 1:
            reasons.append("Leverage must be at least 1.")
        if meta.max_leverage is None:
            reasons.append("Maximum leverage unavailable; risk cannot be calculated.")
        elif inputs.leverage > meta.max_leverage:
            reasons.append(f"Leverage {inputs.leverage}x exceeds the market maximum {meta.max_leverage}x.")

    raw_entries = staged_entries(price, atr_value)
    if any(e <= 0 for e in raw_entries):
        reasons.append("ATR is too large relative to price; staged entries would be at or below zero.")
        raw_entries = [max(e, Decimal(0)) for e in raw_entries]
    try:
        entry_prices = [round_price(meta, e) if e > 0 else Decimal(0) for e in raw_entries]
    except InvalidMetadata as exc:
        reasons.append(str(exc))
        entry_prices = raw_entries
    if any(e >= price for e in entry_prices):
        reasons.append("An entry is not below the current price after rounding.")

    trigger_raw, limit_raw, _ = stop_levels(min(entry_prices), atr_value, inputs.stop_buffer_pct)
    if limit_raw <= 0:
        reasons.append("Stop-limit price would be at or below zero.")
        stop_trigger, stop_limit = max(trigger_raw, Decimal(0)), Decimal(0)
    else:
        stop_trigger, stop_limit = round_price(meta, trigger_raw), round_price(meta, limit_raw)
        if stop_limit >= stop_trigger:
            # Price precision can collapse the buffer; keep the limit strictly below.
            step = meta.price_increment or Decimal(1).scaleb(-(HL_PERP_MAX_PRICE_DECIMALS - (meta.sz_decimals or 0)))
            stop_limit = round_price(meta, stop_trigger - step) if stop_trigger - step > 0 else Decimal(0)
            if stop_limit <= 0:
                reasons.append("Price precision leaves no room for a stop-limit buffer.")

    planned_avg = weighted_average(entry_prices, list(ENTRY_WEIGHTS))
    r_value = planned_avg - stop_trigger
    if r_value <= 0:
        reasons.append("Average entry is not above the stop trigger.")

    unit_loss = worst_case_unit_loss(planned_avg, stop_limit, inputs.fee_pct, inputs.slippage_pct)
    allocation_cap = min(inputs.max_allocation_usd, inputs.max_position_notional_usd)
    # Risk sizing uses the worst-case unit loss (stop-limit fill + fees + slippage), which is
    # never smaller than (average entry - stop trigger); this keeps the worst case within budget.
    risk_qty = inputs.max_planned_loss_usd / unit_loss if unit_loss > 0 else Decimal(0)
    alloc_qty = allocation_cap / planned_avg if planned_avg > 0 else Decimal(0)
    target_qty = min(risk_qty, alloc_qty)
    binding = "risk" if risk_qty <= alloc_qty else "allocation"

    quantities = split_quantity(target_qty, ENTRY_WEIGHTS, meta) if target_qty > 0 else [Decimal(0)] * 3
    for leg, qty, entry_price in zip(("E1", "E2", "E3"), quantities, entry_prices):
        if not meets_minimums(meta, qty, entry_price):
            reasons.append(
                f"{leg} size {qty} at {entry_price} is below the exchange minimum "
                f"(min size {meta.min_size}, min notional {meta.min_notional})."
            )
    if meta.max_notional is not None:
        for leg, qty, entry_price in zip(("E1", "E2", "E3"), quantities, entry_prices):
            if qty * entry_price > meta.max_notional:
                reasons.append(f"{leg} notional exceeds the exchange maximum {meta.max_notional}.")

    total_qty = sum(quantities, Decimal(0))
    capital = sum((q * p for q, p in zip(quantities, entry_prices)), Decimal(0))
    avg_entry = capital / total_qty if total_qty > 0 else planned_avg
    r_value = avg_entry - stop_trigger

    fee = inputs.fee_pct / 100
    est_fees = capital * fee + total_qty * stop_limit * fee
    est_slippage = total_qty * stop_limit * inputs.slippage_pct / 100
    loss_at_trigger = total_qty * (avg_entry - stop_trigger)
    worst_case = total_qty * worst_case_unit_loss(avg_entry, stop_limit, inputs.fee_pct, inputs.slippage_pct)
    if worst_case > inputs.max_planned_loss_usd:
        reasons.append(f"Worst-case loss {worst_case:.2f} exceeds the planned-loss budget {inputs.max_planned_loss_usd:.2f}.")

    tp1_raw = avg_entry + r_value
    tp2_raw = avg_entry + 2 * r_value
    tp3_raw, tp3_source = avg_entry + 3 * r_value, "no resistance above TP2: using 3R"
    for zone in analysis.resistances:
        level = Decimal(str(zone.mid))
        if level > tp2_raw:
            tp3_raw, tp3_source = level, f"nearest resistance zone ({zone.source}, {zone.touches} touch(es))"
            break
    take_profits = [round_price(meta, tp) for tp in (tp1_raw, tp2_raw, tp3_raw)] if r_value > 0 else []
    if take_profits and take_profits[2] < take_profits[1]:
        take_profits[2] = take_profits[1]

    leverage = inputs.leverage
    margin = capital / leverage
    liquidation = None
    if meta.venue == Venue.HYPERLIQUID and meta.max_leverage:
        liquidation = approx_isolated_long_liquidation(avg_entry, leverage, meta.max_leverage)
        if liquidation > 0 and liquidation >= stop_limit:
            reasons.append(
                f"Estimated liquidation price {liquidation:.6f} is at or above the stop-limit price; "
                "the position could be liquidated before the stop can act."
            )
        warnings.append(
            "Perpetuals: liquidation, funding payments and mark-price triggers apply. Margin "
            f"{margin:.2f} controls notional exposure {capital:.2f}."
        )
    if analysis.flags:
        warnings.extend(f for f in analysis.flags if f not in reasons)

    entries = [
        PlannedOrder(leg=leg, role=OrderRole.ENTRY, side=Side.BUY, order_type=OrderType.LIMIT, price=p, quantity=q)
        for leg, p, q in zip(("E1", "E2", "E3"), entry_prices, quantities)
    ]
    # De-duplicate reasons while keeping order.
    reasons = list(dict.fromkeys(reasons))
    return TradePlan(
        venue=meta.venue,
        symbol=meta.symbol,
        interval=analysis.interval,
        created_at=now.isoformat(),
        current_price=price,
        atr=atr_value,
        entries=entries,
        weighted_avg_entry=avg_entry,
        stop_trigger=stop_trigger,
        stop_limit=stop_limit,
        r_value=r_value,
        take_profits=take_profits,
        tp3_source=tp3_source,
        total_quantity=total_qty,
        capital_deployed=capital,
        margin_required=margin,
        leverage=leverage,
        max_planned_loss_budget=inputs.max_planned_loss_usd,
        planned_loss_at_trigger=loss_at_trigger,
        estimated_fees=est_fees,
        estimated_slippage=est_slippage,
        worst_case_loss=worst_case,
        sizing_binding=binding,
        risk_based_quantity=risk_qty,
        allocation_based_quantity=alloc_qty,
        liquidation_price=liquidation,
        refused=bool(reasons),
        refusal_reasons=reasons,
        warnings=warnings,
    )


# --------------------------------------------------------------- hard limits
def kill_switch_active(stop_file: Path) -> bool:
    return Path(stop_file).exists()


def ensure_no_kill_switch(stop_file: Path) -> None:
    if kill_switch_active(stop_file):
        raise KillSwitchTriggered(f"kill switch file {stop_file} exists")


def daily_loss_breached(realized_today: Decimal, unrealized: Decimal, max_daily_loss: Decimal) -> bool:
    return realized_today + min(unrealized, Decimal(0)) <= -max_daily_loss


def check_order_capacity(open_order_count: int, new_orders: int, max_open_orders: int) -> None:
    if open_order_count + new_orders > max_open_orders:
        raise RiskRejected(
            f"placing {new_orders} order(s) would exceed MAX_OPEN_ORDERS={max_open_orders} "
            f"({open_order_count} already open)"
        )


def check_position_notional(quantity: Decimal, price: Decimal, max_notional: Decimal) -> None:
    if quantity * price > max_notional:
        raise RiskRejected(f"position notional {quantity * price:.2f} exceeds MAX_POSITION_NOTIONAL_USD={max_notional}")
