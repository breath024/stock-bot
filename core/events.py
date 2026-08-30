"""시스템 전체가 주고받는 기본 데이터 타입.

전략·브로커·계좌가 모두 이 타입들로만 소통한다.
한국 주식이든 미국 주식이든 여기 구조는 안 바뀐다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Bar:
    """하나의 봉(일봉/분봉). 데이터피드가 흘려보내는 단위."""
    symbol: str
    dt: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Signal:
    """전략이 내는 '매매 의도'. 수량 또는 비중으로 표현.

    - qty: 정확한 주식 수
    - weight: 현금(매수)·보유량(매도) 대비 비중 0~1 (qty 없을 때 사용)
    - 둘 다 없고 SELL이면 전량 매도로 해석
    """
    symbol: str
    side: Side
    qty: int | None = None
    weight: float | None = None
    reason: str = ""


@dataclass
class Order:
    """브로커에 접수되는 실제 주문."""
    symbol: str
    side: Side
    qty: int
    created_dt: datetime
    reason: str = ""


@dataclass
class Fill:
    """체결 결과. 수수료·세금까지 확정된 상태."""
    symbol: str
    side: Side
    qty: int
    price: float
    fee: float
    tax: float
    dt: datetime
    reason: str = ""
