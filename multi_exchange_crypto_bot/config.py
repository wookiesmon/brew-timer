"""Settings loaded from environment variables (optionally via a .env file).

Secrets are held in pydantic ``SecretStr`` so they never appear in reprs or logs.
"""
from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Mapping, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, SecretStr, ValidationError, model_validator

SUPPORTED_INTERVALS = ("1m", "5m", "15m", "30m", "1h", "2h", "1d")
TREND_FILTERS = ("off", "ema", "ema200")

_TRUE = {"true", "1", "yes", "on"}
_FALSE = {"false", "0", "no", "off", ""}


class ConfigError(ValueError):
    """Raised when an environment variable is missing or malformed."""


def _get(env: Mapping[str, str], name: str) -> Optional[str]:
    raw = env.get(name)
    return raw.strip() if raw is not None else None


def _bool(env: Mapping[str, str], name: str, default: bool) -> bool:
    raw = _get(env, name)
    if raw is None:
        return default
    value = raw.lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise ConfigError(f"{name} must be true or false, got {raw!r}")


def _decimal(env: Mapping[str, str], name: str, default: str) -> Decimal:
    raw = _get(env, name) or default
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from exc
    if not value.is_finite():
        raise ConfigError(f"{name} must be finite, got {raw!r}")
    return value


def _int(env: Mapping[str, str], name: str, default: int) -> int:
    raw = _get(env, name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from exc


def _secret(env: Mapping[str, str], name: str) -> Optional[SecretStr]:
    raw = _get(env, name)
    if not raw:
        return None
    # .env files usually store PEM keys on one line with literal "\n" escapes.
    return SecretStr(raw.replace("\\n", "\n"))


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    coinbase_api_key: Optional[SecretStr] = None
    coinbase_api_secret: Optional[SecretStr] = None
    hyperliquid_private_key: Optional[SecretStr] = None
    hyperliquid_account_address: Optional[str] = None
    hyperliquid_testnet: bool = False

    coinbase_live_trading: bool = False
    hyperliquid_live_trading: bool = False
    dry_run: bool = True

    account_equity_usd: Decimal = Decimal("2000")
    max_allocation_pct: Decimal = Decimal("10")
    max_planned_loss_pct: Decimal = Decimal("1")
    max_daily_loss_usd: Decimal = Decimal("50")
    max_position_notional_usd: Decimal = Decimal("200")
    max_open_orders: int = 8
    hyperliquid_leverage: int = 1
    hyperliquid_isolated: bool = True
    hyperliquid_allow_leverage_above_1: bool = False
    stop_buffer_pct: Decimal = Decimal("0.25")

    coinbase_fee_pct: Decimal = Decimal("1.2")
    hyperliquid_fee_pct: Decimal = Decimal("0.05")
    slippage_pct: Decimal = Decimal("0.5")

    candle_interval: str = "1h"
    poll_seconds: int = 30
    entry_ttl_hours: int = 48
    max_retries: int = 4
    api_timeout_seconds: int = 15
    api_error_cooldown_seconds: int = 120
    sim_volume_participation_pct: Decimal = Decimal("20")
    database_path: Path = Path("trading_bot.sqlite3")
    stop_file: Path = Path("STOP")
    log_file: Optional[Path] = None

    trend_filter: str = "off"  # off | ema | ema200
    breakeven_after_tp1: bool = False
    trail_atr_multiple: Decimal = Decimal("0")  # 0 = no trailing stop

    coingecko_enabled: bool = False
    coingecko_api_key: Optional[SecretStr] = None
    coingecko_plan: str = "demo"
    coingecko_min_volume_usd: Decimal = Decimal("1000000")
    coingecko_min_venue_volume_usd: Decimal = Decimal("250000")
    coingecko_max_price_deviation_pct: Decimal = Decimal("2")
    coingecko_max_volume_share_pct: Decimal = Decimal("1")
    coingecko_coin_ids: str = ""
    coingecko_coinbase_exchange_id: str = "gdax"

    @model_validator(mode="after")
    def _validate(self) -> "Settings":
        if self.account_equity_usd <= 0:
            raise ConfigError("ACCOUNT_EQUITY_USD must be positive")
        for name in ("max_allocation_pct", "max_planned_loss_pct"):
            value = getattr(self, name)
            if not (Decimal(0) < value <= Decimal(100)):
                raise ConfigError(f"{name.upper()} must be in (0, 100]")
        for name in ("max_daily_loss_usd", "max_position_notional_usd"):
            if getattr(self, name) <= 0:
                raise ConfigError(f"{name.upper()} must be positive")
        for name in ("stop_buffer_pct", "coinbase_fee_pct", "hyperliquid_fee_pct", "slippage_pct"):
            if getattr(self, name) < 0:
                raise ConfigError(f"{name.upper()} must not be negative")
        if not (Decimal(0) < self.sim_volume_participation_pct <= Decimal(100)):
            raise ConfigError("SIM_VOLUME_PARTICIPATION_PCT must be in (0, 100]")
        if self.max_open_orders < 1:
            raise ConfigError("MAX_OPEN_ORDERS must be at least 1")
        if self.poll_seconds < 5:
            raise ConfigError("POLL_SECONDS must be at least 5")
        if self.max_retries < 0 or self.api_timeout_seconds <= 0:
            raise ConfigError("MAX_RETRIES must be >= 0 and API_TIMEOUT_SECONDS > 0")
        if self.candle_interval not in SUPPORTED_INTERVALS:
            raise ConfigError(f"CANDLE_INTERVAL must be one of {', '.join(SUPPORTED_INTERVALS)}")
        if self.trend_filter not in TREND_FILTERS:
            raise ConfigError(f"TREND_FILTER must be one of {', '.join(TREND_FILTERS)}")
        if self.trail_atr_multiple < 0:
            raise ConfigError("TRAIL_ATR_MULTIPLE must not be negative")
        if self.coingecko_plan not in ("demo", "pro"):
            raise ConfigError("COINGECKO_PLAN must be demo or pro")
        for name in ("coingecko_min_volume_usd", "coingecko_min_venue_volume_usd"):
            if getattr(self, name) < 0:
                raise ConfigError(f"{name.upper()} must not be negative")
        for name in ("coingecko_max_price_deviation_pct", "coingecko_max_volume_share_pct"):
            if getattr(self, name) <= 0:
                raise ConfigError(f"{name.upper()} must be positive")
        if not self.hyperliquid_isolated:
            raise ConfigError("HYPERLIQUID_ISOLATED must be true: cross margin is never used by this bot")
        if self.hyperliquid_leverage < 1:
            raise ConfigError("HYPERLIQUID_LEVERAGE must be at least 1")
        if self.hyperliquid_leverage > 1 and not self.hyperliquid_allow_leverage_above_1:
            raise ConfigError(
                "HYPERLIQUID_LEVERAGE above 1 requires HYPERLIQUID_ALLOW_LEVERAGE_ABOVE_1=true "
                "and an interactive risk confirmation"
            )
        return self

    @property
    def paper_database_path(self) -> Path:
        """Paper state lives in its own file so it can never mix with live state."""
        path = self.database_path
        return path.with_name(f"{path.stem}.paper{path.suffix or '.sqlite3'}")

    def fee_pct(self, venue: str) -> Decimal:
        return self.coinbase_fee_pct if venue == "coinbase" else self.hyperliquid_fee_pct

    def live_flag(self, venue: str) -> bool:
        return self.coinbase_live_trading if venue == "coinbase" else self.hyperliquid_live_trading


def load_settings(env_file: Optional[str] = ".env", env: Optional[Mapping[str, str]] = None) -> Settings:
    """Build Settings from ``env`` (defaults to os.environ after loading ``env_file``)."""
    if env is None:
        if env_file and Path(env_file).exists():
            load_dotenv(env_file, override=False)
        env = os.environ
    try:
        return _build(env)
    except ValidationError as exc:  # report the rule, never the (possibly secret) input values
        raise ConfigError("; ".join(err["msg"].removeprefix("Value error, ") for err in exc.errors())) from None


def _build(env: Mapping[str, str]) -> Settings:
    return Settings(
        coinbase_api_key=_secret(env, "COINBASE_API_KEY"),
        coinbase_api_secret=_secret(env, "COINBASE_API_SECRET"),
        hyperliquid_private_key=_secret(env, "HYPERLIQUID_PRIVATE_KEY"),
        hyperliquid_account_address=_get(env, "HYPERLIQUID_ACCOUNT_ADDRESS") or None,
        hyperliquid_testnet=_bool(env, "HYPERLIQUID_TESTNET", False),
        coinbase_live_trading=_bool(env, "COINBASE_LIVE_TRADING", False),
        hyperliquid_live_trading=_bool(env, "HYPERLIQUID_LIVE_TRADING", False),
        dry_run=_bool(env, "DRY_RUN", True),
        account_equity_usd=_decimal(env, "ACCOUNT_EQUITY_USD", "2000"),
        max_allocation_pct=_decimal(env, "MAX_ALLOCATION_PCT", "10"),
        max_planned_loss_pct=_decimal(env, "MAX_PLANNED_LOSS_PCT", "1"),
        max_daily_loss_usd=_decimal(env, "MAX_DAILY_LOSS_USD", "50"),
        max_position_notional_usd=_decimal(env, "MAX_POSITION_NOTIONAL_USD", "200"),
        max_open_orders=_int(env, "MAX_OPEN_ORDERS", 8),
        hyperliquid_leverage=_int(env, "HYPERLIQUID_LEVERAGE", 1),
        hyperliquid_isolated=_bool(env, "HYPERLIQUID_ISOLATED", True),
        hyperliquid_allow_leverage_above_1=_bool(env, "HYPERLIQUID_ALLOW_LEVERAGE_ABOVE_1", False),
        stop_buffer_pct=_decimal(env, "STOP_BUFFER_PCT", "0.25"),
        coinbase_fee_pct=_decimal(env, "COINBASE_FEE_PCT", "1.2"),
        hyperliquid_fee_pct=_decimal(env, "HYPERLIQUID_FEE_PCT", "0.05"),
        slippage_pct=_decimal(env, "SLIPPAGE_PCT", "0.5"),
        candle_interval=_get(env, "CANDLE_INTERVAL") or "1h",
        poll_seconds=_int(env, "POLL_SECONDS", 30),
        entry_ttl_hours=_int(env, "ENTRY_TTL_HOURS", 48),
        max_retries=_int(env, "MAX_RETRIES", 4),
        api_timeout_seconds=_int(env, "API_TIMEOUT_SECONDS", 15),
        api_error_cooldown_seconds=_int(env, "API_ERROR_COOLDOWN_SECONDS", 120),
        sim_volume_participation_pct=_decimal(env, "SIM_VOLUME_PARTICIPATION_PCT", "20"),
        database_path=Path(_get(env, "DATABASE_PATH") or "trading_bot.sqlite3"),
        log_file=Path(_get(env, "LOG_FILE")) if _get(env, "LOG_FILE") else None,
        trend_filter=(_get(env, "TREND_FILTER") or "off").lower(),
        breakeven_after_tp1=_bool(env, "BREAKEVEN_AFTER_TP1", False),
        trail_atr_multiple=_decimal(env, "TRAIL_ATR_MULTIPLE", "0"),
        coingecko_enabled=_bool(env, "COINGECKO_ENABLED", False),
        coingecko_api_key=_secret(env, "COINGECKO_API_KEY"),
        coingecko_plan=(_get(env, "COINGECKO_PLAN") or "demo").lower(),
        coingecko_min_volume_usd=_decimal(env, "COINGECKO_MIN_VOLUME_USD", "1000000"),
        coingecko_min_venue_volume_usd=_decimal(env, "COINGECKO_MIN_VENUE_VOLUME_USD", "250000"),
        coingecko_max_price_deviation_pct=_decimal(env, "COINGECKO_MAX_PRICE_DEVIATION_PCT", "2"),
        coingecko_max_volume_share_pct=_decimal(env, "COINGECKO_MAX_VOLUME_SHARE_PCT", "1"),
        coingecko_coin_ids=_get(env, "COINGECKO_COIN_IDS") or "",
        coingecko_coinbase_exchange_id=_get(env, "COINGECKO_COINBASE_EXCHANGE_ID") or "gdax",
    )
