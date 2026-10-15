"""Paper-trading exchange simulator.

Implements the same OrderGateway interface as the live adapters, so the execution
engine runs identical code in paper, backtest and live modes. Nothing in this file
can reach an exchange.

Fill model (deliberately conservative; every fill is labelled SIMULATED):
- An order can only fill on candles that open at or after the order was placed.
- Limit buy at P fills only if the candle low trades strictly below P, at min(P, open).
- Limit sell at P fills only if the candle high trades strictly above P, at max(P, open).
- Stop-limit sell (trigger T, limit L) triggers when low <= T. If the candle opens at
  or below L (a gap through the limit) it does NOT fill and rests as a limit at L,
  which is exactly the non-execution risk of real stop-limit orders. Otherwise it
  fills at L (the worst price the limit allows).
- Fill size per candle is capped at SIM_VOLUME_PARTICIPATION_PCT of candle volume,
  which produces partial fills in thin markets.
- Coinbase spot: resting sells hold base balance and buys hold quote balance.
- Hyperliquid perps: exits are reduce-only and are clipped to the open position.
- Funding payments and liquidation are NOT simulated.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Callable, Optional

from database import Database, iso
from models import ExchangeOrder, OrderRejected, OrderStatus, Side, Venue
from risk import floor_to_increment

SIM_SCHEMA = """
CREATE TABLE IF NOT EXISTS sim_orders (
    oid             INTEGER PRIMARY KEY AUTOINCREMENT,
    venue           TEXT NOT NULL,
    product         TEXT NOT NULL,
    client_order_id TEXT NOT NULL,
    side            TEXT NOT NULL,
    order_type      TEXT NOT NULL,
    price           TEXT NOT NULL,
    trigger_price   TEXT,
    quantity        TEXT NOT NULL,
    filled          TEXT NOT NULL DEFAULT '0',
    filled_notional TEXT NOT NULL DEFAULT '0',
    fees            TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL,
    triggered       INTEGER NOT NULL DEFAULT 0,
    reduce_only     INTEGER NOT NULL DEFAULT 0,
    created_ts      TEXT NOT NULL,
    UNIQUE (venue, product, client_order_id)
);
CREATE TABLE IF NOT EXISTS sim_accounts (
    venue   TEXT NOT NULL,
    product TEXT NOT NULL,
    quote   TEXT NOT NULL,
    base    TEXT NOT NULL,
    PRIMARY KEY (venue, product)
);
CREATE TABLE IF NOT EXISTS sim_ledger (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    venue    TEXT NOT NULL,
    product  TEXT NOT NULL,
    oid      INTEGER NOT NULL,
    side     TEXT NOT NULL,
    quantity TEXT NOT NULL,
    price    TEXT NOT NULL,
    fee      TEXT NOT NULL,
    ts       TEXT NOT NULL
);
"""

OPEN = OrderStatus.OPEN.value


class SimulatedExchange:
    def __init__(
        self, db: Database, venue: Venue, product: str, *, starting_quote: Decimal, fee_pct: Decimal,
        participation_pct: Decimal, size_increment: Decimal, clock: Callable[[], datetime], leverage: int = 1,
    ):
        self.db = db
        self.venue = venue
        self.product = product
        self.fee = fee_pct / 100
        self.participation = participation_pct / 100
        self.size_increment = size_increment
        self.clock = clock
        self.leverage = max(int(leverage), 1)
        self.exits_share_balance = venue == Venue.COINBASE
        db.conn.executescript(SIM_SCHEMA)
        db.conn.execute(
            "INSERT OR IGNORE INTO sim_accounts (venue, product, quote, base) VALUES (?, ?, ?, '0')",
            (venue.value, product, str(starting_quote)),
        )
        db.conn.commit()

    # ------------------------------------------------------------- accounts
    def balances(self) -> tuple[Decimal, Decimal]:
        row = self.db.conn.execute(
            "SELECT quote, base FROM sim_accounts WHERE venue = ? AND product = ?", (self.venue.value, self.product)
        ).fetchone()
        return Decimal(row["quote"]), Decimal(row["base"])

    def _set_balances(self, quote: Decimal, base: Decimal) -> None:
        self.db.conn.execute(
            "UPDATE sim_accounts SET quote = ?, base = ? WHERE venue = ? AND product = ?",
            (str(quote), str(base), self.venue.value, self.product),
        )

    def _open_rows(self):
        return self.db.conn.execute(
            "SELECT * FROM sim_orders WHERE venue = ? AND product = ? AND status = ? ORDER BY oid",
            (self.venue.value, self.product, OPEN),
        ).fetchall()

    def _held(self) -> tuple[Decimal, Decimal]:
        held_quote = held_base = Decimal(0)
        for row in self._open_rows():
            remaining = Decimal(row["quantity"]) - Decimal(row["filled"])
            if row["side"] == Side.BUY.value:
                held_quote += remaining * Decimal(row["price"]) * (1 + self.fee) / self.leverage
            elif not row["reduce_only"]:
                held_base += remaining
        return held_quote, held_base

    def available_quote(self) -> Decimal:
        quote, _ = self.balances()
        return quote - self._held()[0]

    def available_position(self) -> Decimal:
        _, base = self.balances()
        if self.exits_share_balance:
            return base - self._held()[1]
        return base

    # --------------------------------------------------------------- orders
    def _insert(self, client_order_id: str, side: Side, order_type: str, quantity: Decimal, price: Decimal,
                trigger: Optional[Decimal], reduce_only: bool) -> str:
        if quantity <= 0 or price <= 0:
            raise OrderRejected("simulated order needs positive quantity and price")
        try:
            cur = self.db.conn.execute(
                "INSERT INTO sim_orders (venue, product, client_order_id, side, order_type, price, trigger_price, "
                "quantity, status, reduce_only, created_ts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.venue.value, self.product, client_order_id, side.value, order_type, str(price),
                    None if trigger is None else str(trigger), str(quantity), OPEN, int(reduce_only),
                    iso(self.clock()),
                ),
            )
        except Exception as exc:  # sqlite3.IntegrityError on duplicate client ID
            raise OrderRejected(f"duplicate client order id {client_order_id}") from exc
        self.db.conn.commit()
        return f"SIM-{cur.lastrowid}"

    def place_limit_buy(self, client_order_id: str, quantity: Decimal, price: Decimal) -> str:
        required = quantity * price * (1 + self.fee) / self.leverage
        if required > self.available_quote():
            raise OrderRejected(f"insufficient simulated quote balance for {required:.2f}")
        return self._insert(client_order_id, Side.BUY, "LIMIT", quantity, price, None, False)

    def _check_sell(self, quantity: Decimal, reduce_only: bool) -> None:
        if self.exits_share_balance:
            if quantity > self.available_position():
                raise OrderRejected("insufficient simulated base balance (spot sells are bounded by balance)")
        else:
            if not reduce_only:
                raise OrderRejected("simulated perp exits must be reduce-only")
            if quantity > self.balances()[1]:
                raise OrderRejected("reduce-only order larger than the open position")

    def place_limit_sell(self, client_order_id: str, quantity: Decimal, price: Decimal, reduce_only: bool) -> str:
        self._check_sell(quantity, reduce_only)
        return self._insert(client_order_id, Side.SELL, "LIMIT", quantity, price, None, reduce_only)

    def place_stop_limit_sell(self, client_order_id: str, quantity: Decimal, trigger_price: Decimal,
                              limit_price: Decimal, reduce_only: bool) -> str:
        if limit_price > trigger_price:
            raise OrderRejected("stop-limit sell limit must not be above the trigger")
        self._check_sell(quantity, reduce_only)
        return self._insert(client_order_id, Side.SELL, "STOP_LIMIT", quantity, limit_price, trigger_price, reduce_only)

    def _to_exchange_order(self, row) -> ExchangeOrder:
        filled = Decimal(row["filled"])
        avg = Decimal(row["filled_notional"]) / filled if filled > 0 else None
        return ExchangeOrder(
            client_order_id=row["client_order_id"],
            exchange_order_id=f"SIM-{row['oid']}",
            status=OrderStatus(row["status"]),
            side=Side(row["side"]),
            quantity=Decimal(row["quantity"]),
            filled_quantity=filled,
            avg_fill_price=avg,
            fees=Decimal(row["fees"]),
            raw_status=("TRIGGERED" if row["triggered"] and row["status"] == OPEN else row["status"]),
        )

    def get_order(self, client_order_id: str, exchange_order_id: Optional[str]) -> Optional[ExchangeOrder]:
        if exchange_order_id:
            row = self.db.conn.execute(
                "SELECT * FROM sim_orders WHERE oid = ?", (int(exchange_order_id.removeprefix("SIM-")),)
            ).fetchone()
        else:
            row = self.db.conn.execute(
                "SELECT * FROM sim_orders WHERE venue = ? AND product = ? AND client_order_id = ?",
                (self.venue.value, self.product, client_order_id),
            ).fetchone()
        return self._to_exchange_order(row) if row else None

    def list_open_orders(self) -> list[ExchangeOrder]:
        return [self._to_exchange_order(r) for r in self._open_rows()]

    def cancel_orders(self, exchange_order_ids: list[str]) -> dict[str, bool]:
        result = {}
        for oid in exchange_order_ids:
            cur = self.db.conn.execute(
                "UPDATE sim_orders SET status = ? WHERE oid = ? AND status = ?",
                (OrderStatus.CANCELLED.value, int(oid.removeprefix("SIM-")), OPEN),
            )
            result[oid] = cur.rowcount == 1
        self.db.conn.commit()
        return result

    # ------------------------------------------------------------ matching
    def process_candle(self, candle: dict) -> list[dict]:
        """Match open orders against one closed candle.

        ``candle`` has keys time (datetime of candle open), open, high, low, close,
        volume, all Decimal except time. Returns the simulated fills.
        """
        ts: datetime = candle["time"]
        o, h, l = candle["open"], candle["high"], candle["low"]
        budget = candle["volume"] * self.participation
        fills = []
        for row in self._open_rows():
            if datetime.fromisoformat(row["created_ts"]) > ts:
                continue  # placed after this candle opened: no look-ahead fills
            side = Side(row["side"])
            price = Decimal(row["price"])
            fill_px: Optional[Decimal] = None
            if row["order_type"] == "LIMIT":
                if side == Side.BUY and l < price:
                    fill_px = min(price, o)
                elif side == Side.SELL and h > price:
                    fill_px = max(price, o)
            else:  # STOP_LIMIT sell
                trigger = Decimal(row["trigger_price"])
                if not row["triggered"]:
                    if l <= trigger:
                        self.db.conn.execute("UPDATE sim_orders SET triggered = 1 WHERE oid = ?", (row["oid"],))
                        if o > price:
                            fill_px = price
                        # else: gapped through the limit -> stays unfilled (real stop-limit risk)
                elif h > price:
                    fill_px = max(price, o)
            if fill_px is None:
                continue

            remaining = Decimal(row["quantity"]) - Decimal(row["filled"])
            quantity = min(remaining, budget)
            quote, base = self.balances()
            if side == Side.SELL:
                if row["reduce_only"] and base <= 0:
                    self.db.conn.execute(
                        "UPDATE sim_orders SET status = ? WHERE oid = ?", (OrderStatus.CANCELLED.value, row["oid"])
                    )
                    continue
                quantity = min(quantity, base)
            quantity = floor_to_increment(quantity, self.size_increment) if quantity < remaining else quantity
            if quantity <= 0:
                continue
            fee = quantity * fill_px * self.fee
            if side == Side.BUY:
                quote -= quantity * fill_px + fee
                base += quantity
            else:
                quote += quantity * fill_px - fee
                base -= quantity
            self._set_balances(quote, base)
            filled = Decimal(row["filled"]) + quantity
            status = OrderStatus.FILLED.value if filled >= Decimal(row["quantity"]) else OPEN
            self.db.conn.execute(
                "UPDATE sim_orders SET filled = ?, filled_notional = ?, fees = ?, status = ? WHERE oid = ?",
                (
                    str(filled), str(Decimal(row["filled_notional"]) + quantity * fill_px),
                    str(Decimal(row["fees"]) + fee), status, row["oid"],
                ),
            )
            self.db.conn.execute(
                "INSERT INTO sim_ledger (venue, product, oid, side, quantity, price, fee, ts) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (self.venue.value, self.product, row["oid"], side.value, str(quantity), str(fill_px), str(fee), iso(ts)),
            )
            budget -= quantity
            fills.append({"oid": row["oid"], "client_order_id": row["client_order_id"], "side": side.value,
                          "quantity": quantity, "price": fill_px, "fee": fee, "time": ts, "simulated": True})
        self.db.conn.commit()
        return fills

    def ledger(self) -> list:
        return self.db.conn.execute(
            "SELECT * FROM sim_ledger WHERE venue = ? AND product = ? ORDER BY id", (self.venue.value, self.product)
        ).fetchall()


def reset_paper_state(db: Database, venue: Venue, product: str) -> None:
    """Delete all paper runs, orders, fills and simulator balances for one market."""
    db.conn.executescript(SIM_SCHEMA)
    for table in ("sim_orders", "sim_ledger", "sim_accounts"):
        db.conn.execute(f"DELETE FROM {table} WHERE venue = ? AND product = ?", (venue.value, product))
    db.conn.execute("DELETE FROM state WHERE key = ?", (f"sim_cursor:{venue.value}:{product}",))
    db.conn.commit()
    db.reset_product(venue.value, product, "paper")
