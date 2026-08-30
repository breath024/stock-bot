"""규칙형 전략 예시 — 이동평균 골든/데드크로스.

단기 이평선이 장기 이평선을 위로 뚫으면(골든크로스) 매수,
아래로 뚫으면(데드크로스) 전량 매도.

이게 '다른 분 매매법 = 파일 하나'의 표준 형태다.
다른 분의 규칙을 여기 on_bar 안에 옮겨 담으면 새 전략이 된다.
"""
from collections import deque

from strategies.base import Side, Signal, Strategy


class GoldenCross(Strategy):
    def __init__(self, symbol: str, short: int = 5, long: int = 20, weight: float = 0.95):
        self.symbol = symbol
        self.short = short
        self.long = long
        self.weight = weight
        self.closes: deque = deque(maxlen=long)
        self.prev_state: str | None = None  # "above" / "below"

    def on_bar(self, bar, account):
        if bar.symbol != self.symbol:
            return []
        self.closes.append(bar.close)
        if len(self.closes) < self.long:
            return []  # 데이터 부족 — 아직 판단 안 함

        closes = list(self.closes)
        ma_s = sum(closes[-self.short:]) / self.short
        ma_l = sum(closes) / self.long
        state = "above" if ma_s > ma_l else "below"

        signals = []
        crossed_up = self.prev_state == "below" and state == "above"
        crossed_down = self.prev_state == "above" and state == "below"

        if crossed_up and account.position_qty(self.symbol) == 0:
            signals.append(Signal(self.symbol, Side.BUY, weight=self.weight,
                                  reason=f"골든크로스 MA{self.short}>MA{self.long}"))
        elif crossed_down and account.position_qty(self.symbol) > 0:
            signals.append(Signal(self.symbol, Side.SELL,
                                  reason=f"데드크로스 MA{self.short}<MA{self.long}"))

        self.prev_state = state
        return signals
