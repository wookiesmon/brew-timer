"""SQLite persistence for runs, orders, fills, daily P/L and bot state.

Decimals are stored as TEXT so no precision is lost. Live and paper state live in
separate database files (see Settings.paper_database_path); every row also carries
its mode so a mix-up is detectable.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Optional, Union

from models import (
    OrderRecord,
    OrderRole,
    OrderStatus,
    OrderType,
    Side,
    TERMINAL_STATUSES,
    TradePlan,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id      TEXT PRIMARY KEY,
    venue       TEXT NOT NULL,
    product     TEXT NOT NULL,
    mode        TEXT NOT NULL,
    status      TEXT NOT NULL,           -- ACTIVE, CLOSED, KILLED, HALTED
    plan_json   TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS runs_active ON runs (venue, product, mode, status);

CREATE TABLE IF NOT EXISTS orders (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    venue             TEXT NOT NULL,
    product           TEXT NOT NULL,
    mode              TEXT NOT NULL,
    run_id            TEXT NOT NULL REFERENCES runs(run_id),
    client_order_id   TEXT NOT NULL,
    exchange_order_id TEXT,
    leg               TEXT NOT NULL,
    role              TEXT NOT NULL,
    order_type        TEXT NOT NULL,
    side              TEXT NOT NULL,
    price             TEXT NOT NULL,
    trigger_price     TEXT,
    quantity          TEXT NOT NULL,
    filled_quantity   TEXT NOT NULL DEFAULT '0',
    avg_fill_price    TEXT,
    fees              TEXT NOT NULL DEFAULT '0',
    status            TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    error             TEXT,
    UNIQUE (venue, mode, client_order_id)
);
CREATE INDEX IF NOT EXISTS orders_run ON orders (run_id, leg);

CREATE TABLE IF NOT EXISTS fills (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    venue            TEXT NOT NULL,
    product          TEXT NOT NULL,
    mode             TEXT NOT NULL,
    run_id           TEXT NOT NULL,
    client_order_id  TEXT NOT NULL,
    side             TEXT NOT NULL,
    quantity         TEXT NOT NULL,
    price            TEXT NOT NULL,
    fee              TEXT NOT NULL,
    realized_pnl     TEXT NOT NULL DEFAULT '0',
    simulated        INTEGER NOT NULL,
    ts               TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS fills_run ON fills (run_id);

CREATE TABLE IF NOT EXISTS daily_pnl (
    day        TEXT NOT NULL,
    venue      TEXT NOT NULL,
    mode       TEXT NOT NULL,
    realized   TEXT NOT NULL,
    PRIMARY KEY (day, venue, mode)
);

CREATE TABLE IF NOT EXISTS state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

RunStatus = str  # ACTIVE | CLOSED | KILLED | HALTED


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat()


def _dec(value: Optional[str]) -> Optional[Decimal]:
    return None if value is None else Decimal(value)


class Database:
    def __init__(self, path: Union[str, Path]):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        if self.path != ":memory:":
            self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ------------------------------------------------------------------ state
    def get_state(self, key: str) -> Optional[str]:
        row = self.conn.execute("SELECT value FROM state WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def set_state(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self.conn.commit()

    def delete_state(self, key: str) -> None:
        self.conn.execute("DELETE FROM state WHERE key = ?", (key,))
        self.conn.commit()

    @staticmethod
    def _halt_key(venue: str, mode: str) -> str:
        return f"halt:{venue}:{mode}"

    def set_halt(self, venue: str, mode: str, reason: str) -> None:
        self.set_state(self._halt_key(venue, mode), json.dumps({"reason": reason, "at": iso(utcnow())}))

    def halt_reason(self, venue: str, mode: str) -> Optional[str]:
        raw = self.get_state(self._halt_key(venue, mode))
        return json.loads(raw)["reason"] if raw else None

    def clear_halt(self, venue: str, mode: str) -> None:
        self.delete_state(self._halt_key(venue, mode))

    def set_cooldown(self, venue: str, mode: str, until: datetime) -> None:
        self.set_state(f"cooldown:{venue}:{mode}", iso(until))

    def cooldown_until(self, venue: str, mode: str) -> Optional[datetime]:
        raw = self.get_state(f"cooldown:{venue}:{mode}")
        return datetime.fromisoformat(raw) if raw else None

    # ------------------------------------------------------------------- runs
    def create_run(self, run_id: str, venue: str, product: str, mode: str, plan: TradePlan, now: datetime) -> None:
        if self.active_run(venue, product, mode) is not None:
            raise RuntimeError(f"an active {mode} run already exists for {venue}:{product}")
        self.conn.execute(
            "INSERT INTO runs (run_id, venue, product, mode, status, plan_json, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?)",
            (run_id, venue, product, mode, json.dumps(plan.to_dict()), iso(now), iso(now)),
        )
        self.conn.commit()

    def active_run(self, venue: str, product: str, mode: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM runs WHERE venue = ? AND product = ? AND mode = ? AND status = 'ACTIVE' "
            "ORDER BY created_at DESC LIMIT 1",
            (venue, product, mode),
        ).fetchone()

    def get_run(self, run_id: str) -> Optional[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()

    def run_plan(self, run_id: str) -> TradePlan:
        row = self.get_run(run_id)
        if row is None:
            raise KeyError(run_id)
        return TradePlan.from_dict(json.loads(row["plan_json"]))

    def set_run_status(self, run_id: str, status: RunStatus, now: datetime) -> None:
        self.conn.execute(
            "UPDATE runs SET status = ?, updated_at = ? WHERE run_id = ?", (status, iso(now), run_id)
        )
        self.conn.commit()

    def runs(self, venue: str, product: str, mode: str) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM runs WHERE venue = ? AND product = ? AND mode = ? ORDER BY created_at",
            (venue, product, mode),
        ).fetchall()

    # ----------------------------------------------------------------- orders
    def _row_to_order(self, row: sqlite3.Row) -> OrderRecord:
        return OrderRecord(
            id=row["id"],
            venue=row["venue"],
            product=row["product"],
            mode=row["mode"],
            run_id=row["run_id"],
            client_order_id=row["client_order_id"],
            exchange_order_id=row["exchange_order_id"],
            leg=row["leg"],
            role=OrderRole(row["role"]),
            order_type=OrderType(row["order_type"]),
            side=Side(row["side"]),
            price=Decimal(row["price"]),
            trigger_price=_dec(row["trigger_price"]),
            quantity=Decimal(row["quantity"]),
            filled_quantity=Decimal(row["filled_quantity"]),
            avg_fill_price=_dec(row["avg_fill_price"]),
            fees=Decimal(row["fees"]),
            status=OrderStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            error=row["error"],
        )

    def insert_order(
        self, *, venue: str, product: str, mode: str, run_id: str, client_order_id: str, leg: str,
        role: OrderRole, order_type: OrderType, side: Side, price: Decimal,
        trigger_price: Optional[Decimal], quantity: Decimal, now: datetime,
    ) -> OrderRecord:
        """Write-ahead insert. The UNIQUE constraint makes a duplicate client ID impossible."""
        cur = self.conn.execute(
            "INSERT INTO orders (venue, product, mode, run_id, client_order_id, leg, role, order_type, "
            "side, price, trigger_price, quantity, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                venue, product, mode, run_id, client_order_id, leg, role.value, order_type.value,
                side.value, str(price), None if trigger_price is None else str(trigger_price),
                str(quantity), OrderStatus.PENDING_SUBMIT.value, iso(now), iso(now),
            ),
        )
        self.conn.commit()
        return self.get_order(cur.lastrowid)

    def get_order(self, order_id: int) -> OrderRecord:
        row = self.conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if row is None:
            raise KeyError(order_id)
        return self._row_to_order(row)

    def update_order(self, order_id: int, now: datetime, **fields) -> OrderRecord:
        allowed = {"exchange_order_id", "filled_quantity", "avg_fill_price", "fees", "status", "error"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValueError(f"cannot update {unknown}")
        sets, values = [], []
        for key, value in fields.items():
            if isinstance(value, OrderStatus):
                value = value.value
            elif isinstance(value, Decimal):
                value = str(value)
            sets.append(f"{key} = ?")
            values.append(value)
        sets.append("updated_at = ?")
        values.append(iso(now))
        values.append(order_id)
        self.conn.execute(f"UPDATE orders SET {', '.join(sets)} WHERE id = ?", values)
        self.conn.commit()
        return self.get_order(order_id)

    def orders_for_run(self, run_id: str, *, leg_prefix: Optional[str] = None, open_only: bool = False) -> list[OrderRecord]:
        sql = "SELECT * FROM orders WHERE run_id = ?"
        params: list = [run_id]
        if leg_prefix:
            sql += " AND leg LIKE ?"
            params.append(f"{leg_prefix}%")
        if open_only:
            sql += f" AND status NOT IN ({','.join('?' * len(TERMINAL_STATUSES))})"
            params.extend(s.value for s in TERMINAL_STATUSES)
        sql += " ORDER BY id"
        return [self._row_to_order(r) for r in self.conn.execute(sql, params).fetchall()]

    def open_orders(self, venue: str, mode: str, product: Optional[str] = None) -> list[OrderRecord]:
        sql = f"SELECT * FROM orders WHERE venue = ? AND mode = ? AND status NOT IN ({','.join('?' * len(TERMINAL_STATUSES))})"
        params: list = [venue, mode, *(s.value for s in TERMINAL_STATUSES)]
        if product:
            sql += " AND product = ?"
            params.append(product)
        return [self._row_to_order(r) for r in self.conn.execute(sql + " ORDER BY id", params).fetchall()]

    def count_leg_versions(self, run_id: str, leg: str) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS n FROM orders WHERE run_id = ? AND leg = ?", (run_id, leg)
        ).fetchone()
        return int(row["n"])

    # ------------------------------------------------------------------ fills
    def record_fill(
        self, *, venue: str, product: str, mode: str, run_id: str, client_order_id: str, side: Side,
        quantity: Decimal, price: Decimal, fee: Decimal, simulated: bool, now: datetime,
    ) -> Decimal:
        """Store a fill; for sells compute realized P/L against the run's average cost."""
        realized = Decimal(0)
        if side == Side.SELL:
            _, avg_cost = self.position(run_id)
            realized = quantity * (price - avg_cost) - fee
        self.conn.execute(
            "INSERT INTO fills (venue, product, mode, run_id, client_order_id, side, quantity, price, fee, "
            "realized_pnl, simulated, ts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                venue, product, mode, run_id, client_order_id, side.value, str(quantity), str(price),
                str(fee), str(realized), int(simulated), iso(now),
            ),
        )
        if side == Side.SELL:
            day = now.astimezone(timezone.utc).date().isoformat()
            row = self.conn.execute(
                "SELECT realized FROM daily_pnl WHERE day = ? AND venue = ? AND mode = ?", (day, venue, mode)
            ).fetchone()
            total = (Decimal(row["realized"]) if row else Decimal(0)) + realized
            self.conn.execute(
                "INSERT INTO daily_pnl (day, venue, mode, realized) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(day, venue, mode) DO UPDATE SET realized = excluded.realized",
                (day, venue, mode, str(total)),
            )
        self.conn.commit()
        return realized

    def fills_for_run(self, run_id: str) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM fills WHERE run_id = ? ORDER BY id", (run_id,)).fetchall()

    def position(self, run_id: str) -> tuple[Decimal, Decimal]:
        """(open quantity, average cost per unit including buy fees) for one run."""
        bought = sold = cost = Decimal(0)
        for row in self.fills_for_run(run_id):
            qty = Decimal(row["quantity"])
            if row["side"] == Side.BUY.value:
                bought += qty
                cost += qty * Decimal(row["price"]) + Decimal(row["fee"])
            else:
                sold += qty
        avg_cost = cost / bought if bought > 0 else Decimal(0)
        return bought - sold, avg_cost

    def total_bought(self, run_id: str) -> Decimal:
        return sum(
            (Decimal(r["quantity"]) for r in self.fills_for_run(run_id) if r["side"] == Side.BUY.value),
            Decimal(0),
        )

    def realized_for_run(self, run_id: str) -> Decimal:
        return sum((Decimal(r["realized_pnl"]) for r in self.fills_for_run(run_id)), Decimal(0))

    def realized_today(self, venue: str, mode: str, now: datetime) -> Decimal:
        day = now.astimezone(timezone.utc).date().isoformat()
        row = self.conn.execute(
            "SELECT realized FROM daily_pnl WHERE day = ? AND venue = ? AND mode = ?", (day, venue, mode)
        ).fetchone()
        return Decimal(row["realized"]) if row else Decimal(0)

    # ------------------------------------------------------------------ reset
    def reset_product(self, venue: str, product: str, mode: str) -> None:
        run_ids = [r["run_id"] for r in self.runs(venue, product, mode)]
        for table in ("fills", "orders"):
            self.conn.executemany(f"DELETE FROM {table} WHERE run_id = ?", [(r,) for r in run_ids])
        self.conn.execute("DELETE FROM runs WHERE venue = ? AND product = ? AND mode = ?", (venue, product, mode))
        self.conn.execute("DELETE FROM daily_pnl WHERE venue = ? AND mode = ?", (venue, mode))
        for key in (self._halt_key(venue, mode), f"cooldown:{venue}:{mode}"):
            self.conn.execute("DELETE FROM state WHERE key = ?", (key,))
        self.conn.commit()
