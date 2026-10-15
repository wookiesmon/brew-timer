"""Shared data types and exceptions.

Every price, quantity, notional, fee and P/L value is a ``Decimal``. Floats are
only used inside indicator maths (analysis.py) and at the Hyperliquid SDK
boundary, which takes floats; values are rounded with Decimal before they cross.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional, Protocol


# --------------------------------------------------------------------------- enums
class Venue(str, Enum):
    COINBASE = "coinbase"
    HYPERLIQUID = "hyperliquid"


class Mode(str, Enum):
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_LIMIT"


class OrderRole(str, Enum):
    ENTRY = "ENTRY"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP = "STOP"


class OrderStatus(str, Enum):
    PENDING_SUBMIT = "PENDING_SUBMIT"  # written before the API call (write-ahead)
    SUBMIT_UNKNOWN = "SUBMIT_UNKNOWN"  # API call raised; must be looked up before anything else
    OPEN = "OPEN"  # resting, possibly partially filled
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"

    @property
    def terminal(self) -> bool:
        return self in TERMINAL_STATUSES


TERMINAL_STATUSES = frozenset(
    {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.EXPIRED, OrderStatus.REJECTED}
)


# ---------------------------------------------------------------------- exceptions
class BotError(Exception):
    """Base class for all errors raised by this project."""


class MarketUnavailable(BotError):
    """The requested market is not listed, not spot/perp as required, or not tradable."""


class InvalidMetadata(BotError):
    """Exchange metadata (precision, minimums, status) is missing or invalid."""


class InsufficientHistory(BotError):
    """Not enough candles to compute the indicators."""


class RiskRejected(BotError):
    """A risk rule refused the plan or an order."""


class OrderRejected(BotError):
    """The exchange (or the simulator) rejected an order."""


class LiveTradingDisabled(BotError):
    """A live-trading precondition is not met. Nothing was submitted."""


class FatalRiskError(BotError):
    """A hard limit was breached. The bot halts and will not restart on its own."""


class KillSwitchTriggered(BotError):
    """The STOP file exists."""


# ---------------------------------------------------------------------- dataclasses
@dataclass(frozen=True)
class MarketMeta:
    venue: Venue
    symbol: str
    base_asset: str
    quote_asset: str
    product_type: str  # "SPOT" or "PERP"
    tradable: bool
    status_detail: str
    size_increment: Decimal
    min_size: Decimal
    min_notional: Decimal
    price_increment: Optional[Decimal] = None  # None => Hyperliquid significant-figure rule
    max_notional: Optional[Decimal] = None
    limit_only: bool = False
    cancel_only: bool = False
    post_only: bool = False
    auction_mode: bool = False
    sz_decimals: Optional[int] = None
    max_leverage: Optional[int] = None
    only_isolated: Optional[bool] = None
    last_price: Optional[Decimal] = None
    mark_price: Optional[Decimal] = None
    change_24h_pct: Optional[Decimal] = None
    funding_rate: Optional[Decimal] = None

    def validate(self) -> None:
        """Raise unless metadata is complete and the market accepts new orders."""
        if self.size_increment is None or self.size_increment <= 0:
            raise InvalidMetadata(f"{self.symbol}: invalid size increment {self.size_increment!r}")
        if self.min_size is None or self.min_size < 0:
            raise InvalidMetadata(f"{self.symbol}: invalid minimum size {self.min_size!r}")
        if self.min_notional is None or self.min_notional < 0:
            raise InvalidMetadata(f"{self.symbol}: invalid minimum notional {self.min_notional!r}")
        if self.price_increment is None:
            if self.sz_decimals is None or not (0 <= self.sz_decimals <= 6):
                raise InvalidMetadata(f"{self.symbol}: no price increment and no valid szDecimals")
        elif self.price_increment <= 0:
            raise InvalidMetadata(f"{self.symbol}: invalid price increment {self.price_increment!r}")
        if not self.tradable:
            raise MarketUnavailable(f"{self.symbol} is not tradable: {self.status_detail}")
        if self.cancel_only:
            raise MarketUnavailable(f"{self.symbol} is in cancel-only mode")
        if self.auction_mode:
            raise MarketUnavailable(f"{self.symbol} is in auction mode")


@dataclass(frozen=True)
class PlannedOrder:
    leg: str  # E1, E2, E3
    role: OrderRole
    side: Side
    order_type: OrderType
    price: Decimal
    quantity: Decimal
    trigger_price: Optional[Decimal] = None

    @property
    def notional(self) -> Decimal:
        return self.price * self.quantity


@dataclass
class TradePlan:
    venue: Venue
    symbol: str
    interval: str
    created_at: str
    current_price: Decimal
    atr: Decimal
    entries: list[PlannedOrder]
    weighted_avg_entry: Decimal
    stop_trigger: Decimal
    stop_limit: Decimal
    r_value: Decimal
    take_profits: list[Decimal]
    tp3_source: str
    total_quantity: Decimal
    capital_deployed: Decimal
    margin_required: Decimal
    leverage: int
    max_planned_loss_budget: Decimal
    planned_loss_at_trigger: Decimal
    estimated_fees: Decimal
    estimated_slippage: Decimal
    worst_case_loss: Decimal
    sizing_binding: str
    risk_based_quantity: Decimal
    allocation_based_quantity: Decimal
    liquidation_price: Optional[Decimal] = None
    refused: bool = False
    refusal_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        def conv(value):
            if isinstance(value, Decimal):
                return str(value)
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, list):
                return [conv(v) for v in value]
            if isinstance(value, dict):
                return {k: conv(v) for k, v in value.items()}
            return value

        return conv(asdict(self))

    @classmethod
    def from_dict(cls, data: dict) -> "TradePlan":
        def dec(value):
            return None if value is None else Decimal(value)

        entries = [
            PlannedOrder(
                leg=e["leg"],
                role=OrderRole(e["role"]),
                side=Side(e["side"]),
                order_type=OrderType(e["order_type"]),
                price=Decimal(e["price"]),
                quantity=Decimal(e["quantity"]),
                trigger_price=dec(e.get("trigger_price")),
            )
            for e in data["entries"]
        ]
        decimal_fields = (
            "current_price", "atr", "weighted_avg_entry", "stop_trigger", "stop_limit", "r_value",
            "total_quantity", "capital_deployed", "margin_required", "max_planned_loss_budget",
            "planned_loss_at_trigger", "estimated_fees", "estimated_slippage", "worst_case_loss",
            "risk_based_quantity", "allocation_based_quantity",
        )
        kwargs = dict(data)
        kwargs["venue"] = Venue(data["venue"])
        kwargs["entries"] = entries
        kwargs["take_profits"] = [Decimal(tp) for tp in data["take_profits"]]
        kwargs["liquidation_price"] = dec(data.get("liquidation_price"))
        for name in decimal_fields:
            kwargs[name] = Decimal(data[name])
        return cls(**kwargs)


@dataclass(frozen=True)
class ExchangeOrder:
    """Venue-neutral snapshot of one order as the exchange (or simulator) reports it."""

    client_order_id: Optional[str]
    exchange_order_id: str
    status: OrderStatus
    side: Optional[Side] = None
    quantity: Optional[Decimal] = None
    filled_quantity: Decimal = Decimal(0)
    avg_fill_price: Optional[Decimal] = None
    fees: Decimal = Decimal(0)
    raw_status: str = ""


@dataclass
class OrderRecord:
    """One row of the ``orders`` table."""

    id: int
    venue: str
    product: str
    mode: str
    run_id: str
    client_order_id: str
    exchange_order_id: Optional[str]
    leg: str
    role: OrderRole
    order_type: OrderType
    side: Side
    price: Decimal
    trigger_price: Optional[Decimal]
    quantity: Decimal
    filled_quantity: Decimal
    avg_fill_price: Optional[Decimal]
    fees: Decimal
    status: OrderStatus
    created_at: str
    updated_at: str
    error: Optional[str]

    @property
    def remaining(self) -> Decimal:
        return max(self.quantity - self.filled_quantity, Decimal(0))


class OrderGateway(Protocol):
    """What the execution engine needs from a venue (live adapter or simulator)."""

    venue: Venue
    # True when resting sell orders reserve the base balance (Coinbase spot holds), so a
    # stop and take-profits cannot both cover the full position at the same time.
    exits_share_balance: bool

    def place_limit_buy(self, client_order_id: str, quantity: Decimal, price: Decimal) -> str: ...

    def place_limit_sell(
        self, client_order_id: str, quantity: Decimal, price: Decimal, reduce_only: bool
    ) -> str: ...

    def place_stop_limit_sell(
        self, client_order_id: str, quantity: Decimal, trigger_price: Decimal,
        limit_price: Decimal, reduce_only: bool,
    ) -> str: ...

    def get_order(self, client_order_id: str, exchange_order_id: Optional[str]) -> Optional[ExchangeOrder]: ...

    def list_open_orders(self) -> list[ExchangeOrder]: ...

    def cancel_orders(self, exchange_order_ids: list[str]) -> dict[str, bool]: ...

    def available_position(self) -> Decimal: ...

    def available_quote(self) -> Decimal: ...
