from decimal import Decimal

import pytest
from pydantic import ValidationError

from analysis import Zone
from conftest import NOW, cb_meta, fake_analysis, hl_meta, make_settings
from models import InvalidMetadata, Venue
from risk import (
    approx_isolated_long_liquidation,
    build_plan,
    daily_loss_breached,
    floor_to_increment,
    hl_floor_price,
    risk_inputs_from_settings,
    stop_levels,
    worst_case_unit_loss,
)


# ------------------------------------------------------------------ rounding
@pytest.mark.parametrize("value,inc,expected", [
    ("1.23456", "0.01", "1.23"),
    ("1.239", "0.01", "1.23"),           # never rounds up
    ("0.000123456", "0.00000001", "0.00012345"),
    ("17", "5", "15"),
    ("0.5", "1", "0"),
])
def test_floor_to_increment(value, inc, expected):
    assert floor_to_increment(Decimal(value), Decimal(inc)) == Decimal(expected)


def test_floor_rejects_invalid_increment():
    with pytest.raises(InvalidMetadata):
        floor_to_increment(Decimal("1"), Decimal("0"))


@pytest.mark.parametrize("price,sz_decimals,expected", [
    ("1234.567", 2, "1234.5"),        # 5 significant figures
    ("0.123456789", 0, "0.12345"),    # 5 sig figs inside the 6-decimal cap
    ("0.0123456", 4, "0.01"),         # capped at 6 - szDecimals = 2 decimals
    ("123456.7", 1, "123456"),        # integers are always valid
])
def test_hyperliquid_price_rounding(price, sz_decimals, expected):
    assert hl_floor_price(Decimal(price), sz_decimals) == Decimal(expected)


def test_invalid_precision_metadata_is_rejected():
    with pytest.raises(InvalidMetadata):
        cb_meta(size_increment=Decimal("0")).validate()
    with pytest.raises(InvalidMetadata):
        hl_meta(sz_decimals=None).validate()


# ---------------------------------------------------------------- stop rules
def test_stop_limit_buffer_uses_larger_of_pct_and_atr():
    trigger, limit, buffer = stop_levels(Decimal("97"), Decimal("2"), Decimal("0.25"))
    assert trigger == Decimal("96")
    assert buffer == Decimal("0.5")             # 0.25 ATR (0.5) > 0.25% of 96 (0.24)
    assert limit == Decimal("95.5")
    trigger, limit, buffer = stop_levels(Decimal("10000"), Decimal("2"), Decimal("0.25"))
    assert buffer == trigger * Decimal("0.0025")  # percentage dominates for large prices


def test_plan_levels_and_take_profits():
    settings = make_settings_tmp()
    inputs = risk_inputs_from_settings(settings, Venue.COINBASE)
    plan = build_plan(fake_analysis(), cb_meta(), inputs, NOW)
    assert not plan.refused, plan.refusal_reasons
    assert [e.price for e in plan.entries] == [Decimal("99"), Decimal("98"), Decimal("97")]
    assert plan.stop_trigger == Decimal("96") and plan.stop_limit == Decimal("95.5")
    assert plan.stop_limit < plan.stop_trigger
    tp1, tp2, tp3 = plan.take_profits
    assert tp1 == floor_to_increment(plan.weighted_avg_entry + plan.r_value, Decimal("0.0001"))
    assert tp2 == floor_to_increment(plan.weighted_avg_entry + 2 * plan.r_value, Decimal("0.0001"))
    assert tp3 >= tp2
    assert "3R" in plan.tp3_source


def test_tp3_uses_nearest_resistance_above_tp2():
    settings = make_settings_tmp()
    inputs = risk_inputs_from_settings(settings, Venue.COINBASE)
    zones = [Zone(101, 101, 2, "swing_high"), Zone(110, 110, 3, "swing_high")]
    plan = build_plan(fake_analysis(resistances=zones), cb_meta(), inputs, NOW)
    assert plan.take_profits[2] == Decimal("110")  # 101 is below TP2, so it is skipped


# ------------------------------------------------------------------- sizing
def test_allocation_cap_binds_and_split_is_40_35_25():
    settings = make_settings_tmp()
    plan = build_plan(fake_analysis(), cb_meta(), risk_inputs_from_settings(settings, Venue.COINBASE), NOW)
    assert plan.sizing_binding == "allocation"
    assert plan.capital_deployed <= Decimal("200")
    q = [e.quantity for e in plan.entries]
    assert q == [Decimal("0.81"), Decimal("0.71"), Decimal("0.51")]


def test_risk_based_sizing_keeps_worst_case_within_budget():
    # Big allocation, small loss budget: risk must bind.
    settings = make_settings_tmp(max_allocation_pct=Decimal("100"), max_position_notional_usd=Decimal("100000"))
    inputs = risk_inputs_from_settings(settings, Venue.COINBASE)
    plan = build_plan(fake_analysis(), cb_meta(), inputs, NOW)
    assert plan.sizing_binding == "risk"
    assert plan.worst_case_loss <= inputs.max_planned_loss_usd == Decimal("20")
    # Conservative: never larger than the textbook max_loss / (avg - stop_trigger).
    assert plan.total_quantity <= inputs.max_planned_loss_usd / (plan.weighted_avg_entry - plan.stop_trigger)
    unit = worst_case_unit_loss(plan.weighted_avg_entry, plan.stop_limit, inputs.fee_pct, inputs.slippage_pct)
    assert unit > plan.weighted_avg_entry - plan.stop_trigger


def test_risk_pct_cannot_exceed_configured_maximum():
    settings = make_settings_tmp()
    with pytest.raises(Exception):
        risk_inputs_from_settings(settings, Venue.COINBASE, risk_pct=Decimal("5"))
    inputs = risk_inputs_from_settings(settings, Venue.COINBASE, risk_pct=Decimal("0.5"))
    assert inputs.max_planned_loss_usd == Decimal("10")


def test_minimum_order_size_failure_refuses_plan():
    settings = make_settings_tmp()
    meta = cb_meta(min_notional=Decimal("100"))  # each staged entry is < $100
    plan = build_plan(fake_analysis(), meta, risk_inputs_from_settings(settings, Venue.COINBASE), NOW)
    assert plan.refused
    assert any("below the exchange minimum" in r for r in plan.refusal_reasons)


def test_extended_market_refuses_plan():
    settings = make_settings_tmp()
    plan = build_plan(fake_analysis(extended=True), cb_meta(), risk_inputs_from_settings(settings, Venue.COINBASE), NOW)
    assert plan.refused
    assert "Market is extended; no automatic market entry will be created." in plan.refusal_reasons


def test_atr_too_large_refuses_plan():
    settings = make_settings_tmp()
    plan = build_plan(fake_analysis(price=1.0, atr=0.9), cb_meta(), risk_inputs_from_settings(settings, Venue.COINBASE), NOW)
    assert plan.refused


# --------------------------------------------------------------- hyperliquid
def test_liquidation_at_1x_is_zero():
    assert approx_isolated_long_liquidation(Decimal("100"), 1, 50) == 0


def test_liquidation_risk_rejects_plan():
    settings = make_settings_tmp(hyperliquid_leverage=10, hyperliquid_allow_leverage_above_1=True)
    inputs = risk_inputs_from_settings(settings, Venue.HYPERLIQUID)
    plan = build_plan(fake_analysis(atr=8.0), hl_meta(max_leverage=10), inputs, NOW)
    assert plan.refused
    assert any("liquidation" in r for r in plan.refusal_reasons)


def test_one_x_hyperliquid_plan_is_accepted():
    settings = make_settings_tmp()
    plan = build_plan(fake_analysis(), hl_meta(), risk_inputs_from_settings(settings, Venue.HYPERLIQUID), NOW)
    assert not plan.refused, plan.refusal_reasons
    assert plan.leverage == 1 and plan.margin_required == plan.capital_deployed
    assert plan.liquidation_price == 0


def test_leverage_above_market_maximum_is_refused():
    settings = make_settings_tmp(hyperliquid_leverage=5, hyperliquid_allow_leverage_above_1=True)
    plan = build_plan(fake_analysis(), hl_meta(max_leverage=3), risk_inputs_from_settings(settings, Venue.HYPERLIQUID), NOW)
    assert plan.refused


def test_leverage_above_1_rejected_unless_explicitly_enabled(tmp_path):
    with pytest.raises(ValidationError):
        make_settings(tmp_path, hyperliquid_leverage=2)
    assert make_settings(tmp_path, hyperliquid_leverage=2, hyperliquid_allow_leverage_above_1=True)


def test_isolated_margin_is_enforced(tmp_path):
    with pytest.raises(ValidationError):
        make_settings(tmp_path, hyperliquid_isolated=False)


def test_daily_loss_rule():
    assert daily_loss_breached(Decimal("-30"), Decimal("-20"), Decimal("50"))
    assert not daily_loss_breached(Decimal("-30"), Decimal("+100"), Decimal("50"))  # gains never offset


# ------------------------------------------------------------------ helpers
def make_settings_tmp(**over):
    import tempfile
    from pathlib import Path

    return make_settings(Path(tempfile.mkdtemp()), **over)
