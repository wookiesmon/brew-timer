"""Backtest statistics: is there an edge after fees, and does it survive unseen data?"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Optional

MIN_MEANINGFUL_TRADES = 30


@dataclass(frozen=True)
class TradeStats:
    trades: int
    wins: int
    losses: int
    net_pnl: Decimal
    gross_profit: Decimal
    gross_loss: Decimal  # positive number
    fees: Decimal

    @property
    def win_rate(self) -> Optional[Decimal]:
        return Decimal(self.wins) / self.trades * 100 if self.trades else None

    @property
    def profit_factor(self) -> Optional[Decimal]:
        """Gross profit / gross loss. Above 1 means winners outweigh losers after fees."""
        if self.gross_loss == 0:
            return None
        return self.gross_profit / self.gross_loss

    @property
    def expectancy(self) -> Optional[Decimal]:
        """Average net P/L per trade, after fees."""
        return self.net_pnl / self.trades if self.trades else None

    @property
    def avg_win(self) -> Optional[Decimal]:
        return self.gross_profit / self.wins if self.wins else None

    @property
    def avg_loss(self) -> Optional[Decimal]:
        return -self.gross_loss / self.losses if self.losses else None

    @property
    def enough_trades(self) -> bool:
        return self.trades >= MIN_MEANINGFUL_TRADES


def trade_stats(pnls: Iterable[Decimal], fees: Iterable[Decimal] = ()) -> TradeStats:
    pnls = list(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    return TradeStats(
        trades=len(pnls),
        wins=len(wins),
        losses=len(losses),
        net_pnl=sum(pnls, Decimal(0)),
        gross_profit=sum(wins, Decimal(0)),
        gross_loss=-sum(losses, Decimal(0)),
        fees=sum(fees, Decimal(0)),
    )


def max_drawdown(curve: Iterable[Decimal]) -> tuple[Decimal, Decimal]:
    """(largest peak-to-trough drop, same as % of that peak)."""
    peak = None
    worst, worst_pct = Decimal(0), Decimal(0)
    for value in curve:
        peak = value if peak is None or value > peak else peak
        drop = peak - value
        if drop > worst:
            worst = drop
            worst_pct = drop / peak * 100 if peak > 0 else Decimal(0)
    return worst, worst_pct


def merge(stats: Iterable[TradeStats]) -> TradeStats:
    stats = list(stats)
    return TradeStats(
        trades=sum(s.trades for s in stats), wins=sum(s.wins for s in stats), losses=sum(s.losses for s in stats),
        net_pnl=sum((s.net_pnl for s in stats), Decimal(0)),
        gross_profit=sum((s.gross_profit for s in stats), Decimal(0)),
        gross_loss=sum((s.gross_loss for s in stats), Decimal(0)),
        fees=sum((s.fees for s in stats), Decimal(0)),
    )
