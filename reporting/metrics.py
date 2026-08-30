"""성과 지표 계산.

총수익률, MDD(최대낙폭), 샤프지수, 체결 통계 등.
"""
from __future__ import annotations

import math


def compute(equity_curve: list[tuple], initial_cash: float, fills: list) -> dict:
    if not equity_curve:
        return {}

    equities = [e for _, e in equity_curve]
    final = equities[-1]
    total_return = final / initial_cash - 1

    # MDD (최대 낙폭)
    peak = -float("inf")
    mdd = 0.0
    for e in equities:
        peak = max(peak, e)
        if peak > 0:
            mdd = min(mdd, e / peak - 1)

    # 일간 수익률 → 샤프 (연 250 거래일 가정, 무위험수익률 0)
    rets = [equities[i] / equities[i - 1] - 1
            for i in range(1, len(equities)) if equities[i - 1] > 0]
    if len(rets) > 1:
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
        std = math.sqrt(var)
        sharpe = (mean / std) * math.sqrt(250) if std > 0 else 0.0
    else:
        sharpe = 0.0

    sells = [f for f in fills if f.side.value == "SELL"]
    return {
        "최종자산": f"{round(final):,}원",
        "총수익률": f"{total_return * 100:.2f}%",
        "MDD": f"{mdd * 100:.2f}%",
        "샤프지수": round(sharpe, 2),
        "체결건수": len(fills),
        "매도건수": len(sells),
    }
