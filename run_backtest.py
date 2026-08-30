"""백테스트 진입점.

KIS API 키 없이 바로 실행 가능 (합성 데이터 사용).
    실행:  python run_backtest.py

나중에 실제 데이터로 바꾸려면 SyntheticFeed 대신 CsvFeed를 쓰면 된다.
"""
from broker.simulated import SimulatedBroker
from core.engine import Engine
from data.feeds.historical import SyntheticFeed
from portfolio.account import Account
from reporting import metrics, trade_log
from strategies.rule_based.golden_cross import GoldenCross

SYMBOL = "TEST"
INITIAL_CASH = 10_000_000


def main():
    feed = SyntheticFeed(symbol=SYMBOL, days=250)
    strategy = GoldenCross(symbol=SYMBOL, short=5, long=20, weight=0.95)
    broker = SimulatedBroker(fee_rate=0.00015, tax_rate=0.0018, slippage=0.0005)
    account = Account(INITIAL_CASH)

    engine = Engine(feed, strategy, broker, account).run()

    result = metrics.compute(engine.equity_curve, INITIAL_CASH, engine.fills)
    trade_log.save(engine.fills, "backtest_trades.csv")

    print("\n=== 백테스트 결과 (골든크로스 / 합성데이터 250일) ===")
    print(f"  초기자본: {INITIAL_CASH:,}원")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print(f"\n  매매내역 저장 → backtest_trades.csv")


if __name__ == "__main__":
    main()
