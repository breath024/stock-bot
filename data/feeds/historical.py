"""과거 데이터 피드 (백테스트용).

- CsvFeed:        실제 CSV 파일을 읽어 Bar로 변환
- SyntheticFeed:  KIS 키 없이 바로 돌려보기 위한 가짜 시세 (추세+노이즈)

CSV 컬럼: date,open,high,low,close,volume   (date = YYYY-MM-DD)
"""
from __future__ import annotations

import csv
import math
from datetime import datetime, timedelta

from core.events import Bar
from core.interfaces import DataFeed


class CsvFeed(DataFeed):
    def __init__(self, symbol: str, path: str):
        self.symbol = symbol
        self.path = path

    def stream(self):
        with open(self.path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                yield Bar(
                    self.symbol,
                    datetime.strptime(row["date"], "%Y-%m-%d"),
                    float(row["open"]), float(row["high"]),
                    float(row["low"]), float(row["close"]),
                    float(row.get("volume", 0) or 0),
                )


class _Lcg:
    """결정적 선형합동난수 — 외부 의존성 없이 재현 가능한 시세 생성용."""
    def __init__(self, seed: int):
        self.s = seed & 0x7FFFFFFF

    def next(self) -> float:
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF


class SyntheticFeed(DataFeed):
    def __init__(self, symbol: str = "TEST", days: int = 250,
                 start_price: float = 50000, seed: int = 42):
        self.symbol = symbol
        self.days = days
        self.start_price = start_price
        self.seed = seed

    def stream(self):
        rnd = _Lcg(self.seed)
        price = self.start_price
        dt = datetime(2024, 1, 1)
        for i in range(self.days):
            drift = math.sin(i / 20) * 0.004        # 완만한 추세 (사이클)
            shock = (rnd.next() - 0.5) * 0.03         # 노이즈
            open_p = price
            close_p = max(1000, price * (1 + drift + shock))
            high = max(open_p, close_p) * (1 + rnd.next() * 0.01)
            low = min(open_p, close_p) * (1 - rnd.next() * 0.01)
            yield Bar(self.symbol, dt, round(open_p), round(high),
                      round(low), round(close_p), 1_000_000)
            price = close_p
            dt += timedelta(days=1)
