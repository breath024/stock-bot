"""새 규칙형 전략 복붙용 템플릿.

이 파일을 복사해서 '다른 분의 매매법'을 옮겨 담으면 된다.
필요한 건 단 하나: on_bar에서 매매 조건을 판단해 Signal을 반환할 것.
"""
from strategies.base import Side, Signal, Strategy


class MyStrategy(Strategy):
    def __init__(self, symbol: str):
        self.symbol = symbol
        # 여기서 지표용 상태(이전 종가, 큐 등)를 초기화

    def on_bar(self, bar, account):
        if bar.symbol != self.symbol:
            return []

        signals = []
        # --- 여기에 매매 규칙 작성 ---
        # 예) if 조건: signals.append(Signal(self.symbol, Side.BUY, weight=0.5, reason="..."))
        # 예) if 조건: signals.append(Signal(self.symbol, Side.SELL, reason="전량매도"))
        return signals
