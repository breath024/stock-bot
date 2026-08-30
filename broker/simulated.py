"""모의 체결 엔진.

백테스트와 '자체 모의투자' 양쪽에서 공용으로 쓰는 핵심 부품.
한국 주식 현실을 반영한다: 매매수수료 + 거래세(매도) + 슬리피지.

기본값:
- fee_rate 0.00015 (0.015%)  : 증권사별로 다름. 실제 값으로 교체할 것.
- tax_rate 0.0018  (0.18%)   : 거래세+농특세, 매도 시에만. (※ 세율은 연도별로 바뀜)
- slippage 0.0005  (0.05%)   : 체결 미끄러짐 가정.
"""
from __future__ import annotations

from core.events import Bar, Fill, Order, Side
from core.interfaces import Broker


class SimulatedBroker(Broker):
    def __init__(self, fee_rate: float = 0.00015, tax_rate: float = 0.0018,
                 slippage: float = 0.0005):
        self.fee_rate = fee_rate
        self.tax_rate = tax_rate
        self.slippage = slippage
        self.pending: list[Order] = []

    def submit(self, order: Order) -> None:
        if order.qty > 0:
            self.pending.append(order)

    def execute_pending(self, bar: Bar) -> list[Fill]:
        fills: list[Fill] = []
        for order in self.pending:
            if order.symbol != bar.symbol:
                continue
            # 다음 봉 시가에 체결 (룩어헤드 방지) + 슬리피지
            base = bar.open
            slip = base * self.slippage
            price = base + slip if order.side == Side.BUY else base - slip
            fee = price * order.qty * self.fee_rate
            tax = price * order.qty * self.tax_rate if order.side == Side.SELL else 0.0
            fills.append(Fill(order.symbol, order.side, order.qty,
                              price, fee, tax, bar.dt, order.reason))
        # 체결된 종목 주문 제거
        self.pending = [o for o in self.pending if o.symbol != bar.symbol]
        return fills
