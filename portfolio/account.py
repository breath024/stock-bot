"""계좌·포트폴리오 상태.

현금, 보유 종목, 평단가, 평가자산을 관리한다.
백테스트와 모의투자가 동일하게 사용한다.
"""
from __future__ import annotations

from dataclasses import dataclass

from core.events import Fill, Side


@dataclass
class Position:
    qty: int = 0
    avg_price: float = 0.0


class Account:
    def __init__(self, initial_cash: float):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: dict[str, Position] = {}
        self.last_prices: dict[str, float] = {}

    def update_price(self, symbol: str, price: float) -> None:
        self.last_prices[symbol] = price

    def apply_fill(self, fill: Fill) -> None:
        pos = self.positions.setdefault(fill.symbol, Position())
        if fill.side == Side.BUY:
            cost = fill.price * fill.qty + fill.fee
            self.cash -= cost
            new_qty = pos.qty + fill.qty
            if new_qty > 0:
                pos.avg_price = (pos.avg_price * pos.qty + fill.price * fill.qty) / new_qty
            pos.qty = new_qty
        else:  # SELL
            self.cash += fill.price * fill.qty - fill.fee - fill.tax
            pos.qty -= fill.qty
            if pos.qty <= 0:
                pos.qty = 0
                pos.avg_price = 0.0

    def position_qty(self, symbol: str) -> int:
        p = self.positions.get(symbol)
        return p.qty if p else 0

    def equity(self) -> float:
        """현금 + 보유종목 평가액."""
        mv = sum(
            self.last_prices.get(sym, p.avg_price) * p.qty
            for sym, p in self.positions.items()
        )
        return self.cash + mv
