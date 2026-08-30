"""전략 작성용 공통 임포트 묶음.

새 전략은 `from strategies.base import Strategy, Bar, Signal, Side` 로 시작하면 된다.
'다른 분들의 매매법'은 규칙형(rule_based/)이든 카피형(copy/)이든
모두 Strategy를 상속해 같은 Signal을 내보낸다 → 봇 입장에선 구별되지 않는다.
"""
from core.events import Bar, Side, Signal
from core.interfaces import Strategy

__all__ = ["Strategy", "Bar", "Signal", "Side"]
