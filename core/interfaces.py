"""핵심 추상 인터페이스(ABC).

모든 구현체는 이 3개 인터페이스에 맞춰 끼워진다.
- DataFeed:  과거 CSV든 실시간 웹소켓이든 Bar를 흘려보낸다
- Strategy:  Bar를 보고 Signal을 낸다 (규칙형/카피형 공통)
- Broker:    Order를 받아 Fill을 만든다 (모의 체결/실거래 공통)

이 분리 덕분에 같은 전략이 백테스트와 실시간 모의투자에서 그대로 돈다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from core.events import Bar, Fill, Order, Signal


class DataFeed(ABC):
    @abstractmethod
    def stream(self) -> Iterator[Bar]:
        """시간 순서대로 Bar를 하나씩 내보낸다."""
        ...


class Strategy(ABC):
    @abstractmethod
    def on_bar(self, bar: Bar, account) -> list[Signal]:
        """새 봉이 들어올 때마다 호출. 매매 의도를 0개 이상 반환."""
        ...


class Broker(ABC):
    @abstractmethod
    def submit(self, order: Order) -> None:
        """주문 접수 (즉시 체결되지 않고 대기열에 들어감)."""
        ...

    @abstractmethod
    def execute_pending(self, bar: Bar) -> list[Fill]:
        """대기 주문을 이번 봉에 체결시키고 Fill 목록을 반환."""
        ...
