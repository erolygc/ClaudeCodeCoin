"""
Manual Backtesting Test Script
Test backtesting with explicit database path
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Phase2_AlphaEngine.backtesting.backtester import Backtester
from Phase2_AlphaEngine.backtesting.strategy import RSI_Strategy, MACD_Strategy, BollingerBands_Strategy

def main():
    print("=" * 70)
    print("🎯 ClaudeCodeCoin - Backtesting Engine Test")
    print("=" * 70)
    print()

    # Find database
    db_path = project_root / "data_output" / "binance_data.db"

    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print()
        print("Please ensure you have collected data first:")
        print("  1. Run: .\\START_COLLECTOR.bat")
        print("  2. Wait for at least 100+ candles")
        print("  3. Run this test again")
        return

    print(f"✅ Found database: {db_path}")
    print(f"   Size: {db_path.stat().st_size / 1024:.2f} KB")
    print()

    # Initialize backtester with explicit path
    backtester = Backtester(
        db_path=str(db_path),
        initial_capital=10000,
        commission=0.001,
        slippage=0.0005
    )

    # Test strategies
    strategies = [
        RSI_Strategy(rsi_buy=30, rsi_sell=70),
        MACD_Strategy(),
        BollingerBands_Strategy()
    ]

    results_list = []

    for strategy in strategies:
        print("=" * 70)
        print(f"🔄 Testing: {strategy.name}")
        print("=" * 70)
        print()

        try:
            results = backtester.run(
                strategy=strategy,
                symbol='BTCUSDT',
                exchange='binance'
            )

            if 'error' in results:
                print(f"❌ Error: {results['error']}")
            else:
                results_list.append({
                    'strategy': strategy.name,
                    'results': results
                })

                print()
                print(f"📊 RESULTS - {strategy.name}")
                print("-" * 70)
                print(f"Total Return: {results['total_return']:.2%}")
                print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
                print(f"Win Rate: {results['win_rate']:.1%}")
                print(f"Max Drawdown: {results['max_drawdown']:.1%}")
                print(f"Profit Factor: {results['profit_factor']:.2f}")

        except Exception as e:
            print(f"❌ Error running strategy: {e}")
            import traceback
            traceback.print_exc()

        print()

    # Summary
    if results_list:
        print("=" * 70)
        print("📊 STRATEGY COMPARISON")
        print("=" * 70)
        print()
        print(f"{'Strategy':<25} {'Return':<12} {'Sharpe':<10} {'Win Rate':<12} {'Max DD':<10}")
        print("-" * 70)

        for item in sorted(results_list, key=lambda x: x['results']['sharpe_ratio'], reverse=True):
            r = item['results']
            print(f"{item['strategy']:<25} {r['total_return']:>10.2%}  {r['sharpe_ratio']:>8.2f}  {r['win_rate']:>10.1%}  {r['max_drawdown']:>8.1%}")

        print()
        print(f"🏆 Best Strategy: {results_list[0]['strategy']} (Sharpe: {results_list[0]['results']['sharpe_ratio']:.2f})")
        print()

    print("=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
