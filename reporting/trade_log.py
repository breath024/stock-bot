"""매매내역 CSV 저장. (엑셀에서 한글 깨짐 방지 위해 utf-8-sig)"""
from __future__ import annotations

import csv


def save(fills: list, path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["일시", "종목", "방향", "수량", "가격", "수수료", "세금", "사유"])
        for x in fills:
            w.writerow([
                x.dt.strftime("%Y-%m-%d"), x.symbol, x.side.value,
                x.qty, round(x.price), round(x.fee), round(x.tax), x.reason,
            ])
