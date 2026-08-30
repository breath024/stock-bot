"""메인 실행 루프.

과거(백테스트)와 실시간(모의투자)이 공용으로 쓴다.
데이터피드와 브로커만 교체하면 동일 전략이 양쪽에서 동작한다.

핵심: 신호는 '이번 봉 종가' 기준으로 내고, 체결은 '다음 봉 시가'에 한다.
      → 미래 데이터를 미리 보는 룩어헤드(lookahead) 오류 방지.
"""
from __future__ import annotations

from core.events import Order, Side, Signal
from core.interfaces import Broker, DataFeed, Strategy
from portfolio.account import Account


class Engine:
    def __init__(self, feed: DataFeed, strategy: Strategy, broker: Broker, account: Account):
        self.feed = feed
        self.strategy = strategy
        self.broker = broker
        self.account = account
        self.equity_curve: list[tuple] = []
        self.fills: list = []

    def run(self) -> "Engine":
        for bar in self.feed.stream():
            self.account.update_price(bar.symbol, bar.close)

            # 1) 직전 봉에서 낸 주문을 이번 봉에 체결
            for fill in self.broker.execute_pending(bar):
                self.account.apply_fill(fill)
                self.fills.append(fill)

            # 2) 전략이 이번 봉 종가 기준으로 신호 생성
            for sig in self.strategy.on_bar(bar, self.account):
                qty = self._resolve_qty(sig, bar.close)
                if qty > 0:
                    self.broker.submit(Order(sig.symbol, sig.side, qty, bar.dt, sig.reason))

            # 3) 자산 곡선 기록
            self.equity_curve.append((bar.dt, self.account.equity()))
        return self

    def _resolve_qty(self, sig: Signal, ref_price: float) -> int:
        """Signal(수량/비중)을 실제 주문 수량으로 변환."""
        if sig.side == Side.SELL:
            held = self.account.position_qty(sig.symbol)
            if sig.qty is not None:
                return min(sig.qty, held)
            if sig.weight is not None:
                return int(held * sig.weight)
            return held  # 전량 매도

        # BUY
        if sig.qty is not None:
            return sig.qty
        if sig.weight is not None and ref_price > 0:
            budget = self.account.cash * sig.weight
            return int(budget // ref_price)
        return 0
