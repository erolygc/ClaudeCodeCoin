"""
Strategy Optimizer
Find best parameters for trading strategies
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
from itertools import product

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from Phase2_AlphaEngine.backtesting.backtester import Backtester
from Phase2_AlphaEngine.backtesting.strategy import RSI_Strategy, MACD_Strategy, BollingerBands_Strategy


class StrategyOptimizer:
    """
    Optimize strategy parameters using grid search
    """

    def __init__(self, db_path: str = None):
        """Initialize optimizer"""
        self.db_path = db_path
        self.results = []

    def optimize_rsi(
        self,
        symbol: str,
        exchange: str = "binance",
        rsi_buy_range: List[int] = [20, 25, 30, 35],
        rsi_sell_range: List[int] = [65, 70, 75, 80],
        initial_capital: float = 10000
    ) -> Dict:
        """
        Optimize RSI strategy parameters

        Args:
            symbol: Trading symbol
            exchange: Exchange name
            rsi_buy_range: List of RSI buy thresholds to test
            rsi_sell_range: List of RSI sell thresholds to test
            initial_capital: Starting capital

        Returns:
            Best parameters and results
        """
        print("=" * 70)
        print("🔍 RSI Strategy Optimization")
        print("=" * 70)
        print(f"Symbol: {symbol}")
        print(f"Exchange: {exchange}")
        print(f"Testing {len(rsi_buy_range)} x {len(rsi_sell_range)} = {len(rsi_buy_range) * len(rsi_sell_range)} combinations")
        print()

        backtester = Backtester(db_path=self.db_path, initial_capital=initial_capital)
        results = []

        total_tests = len(rsi_buy_range) * len(rsi_sell_range)
        current_test = 0

        for buy in rsi_buy_range:
            for sell in rsi_sell_range:
                if buy >= sell:
                    continue  # Invalid combination

                current_test += 1
                print(f"[{current_test}/{total_tests}] Testing RSI({buy}, {sell})...", end=" ")

                strategy = RSI_Strategy(rsi_buy=buy, rsi_sell=sell)

                try:
                    backtest_result = backtester.run(
                        strategy=strategy,
                        symbol=symbol,
                        exchange=exchange
                    )

                    if 'error' not in backtest_result:
                        results.append({
                            'rsi_buy': buy,
                            'rsi_sell': sell,
                            'total_return': backtest_result['total_return'],
                            'sharpe_ratio': backtest_result['sharpe_ratio'],
                            'win_rate': backtest_result['win_rate'],
                            'max_drawdown': backtest_result['max_drawdown'],
                            'profit_factor': backtest_result['profit_factor'],
                            'total_trades': backtest_result['total_trades']
                        })
                        print(f"✅ Return: {backtest_result['total_return']:.2%}, Sharpe: {backtest_result['sharpe_ratio']:.2f}")
                    else:
                        print(f"❌ {backtest_result['error']}")

                except Exception as e:
                    print(f"❌ Error: {e}")

        if not results:
            return {'error': 'No valid results'}

        # Sort by Sharpe ratio
        results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)

        best = results[0]

        print()
        print("=" * 70)
        print("🏆 OPTIMIZATION RESULTS")
        print("=" * 70)
        print()
        print(f"Best Parameters: RSI({best['rsi_buy']}, {best['rsi_sell']})")
        print(f"Total Return: {best['total_return']:.2%}")
        print(f"Sharpe Ratio: {best['sharpe_ratio']:.2f}")
        print(f"Win Rate: {best['win_rate']:.1%}")
        print(f"Max Drawdown: {best['max_drawdown']:.1%}")
        print(f"Profit Factor: {best['profit_factor']:.2f}")
        print(f"Total Trades: {best['total_trades']}")
        print()

        # Top 5
        print("📊 Top 5 Combinations:")
        print("-" * 70)
        print(f"{'Params':<12} {'Return':<12} {'Sharpe':<10} {'Win Rate':<12} {'Max DD':<10}")
        print("-" * 70)

        for i, r in enumerate(results[:5], 1):
            print(f"{i}. RSI({r['rsi_buy']},{r['rsi_sell']})  {r['total_return']:>10.2%}  {r['sharpe_ratio']:>8.2f}  {r['win_rate']:>10.1%}  {r['max_drawdown']:>8.1%}")

        print()
        print("=" * 70)

        return {
            'best_params': {'rsi_buy': best['rsi_buy'], 'rsi_sell': best['rsi_sell']},
            'best_results': best,
            'all_results': results
        }

    def compare_strategies(
        self,
        symbol: str,
        exchange: str = "binance",
        initial_capital: float = 10000
    ) -> Dict:
        """
        Compare different strategy types

        Args:
            symbol: Trading symbol
            exchange: Exchange name
            initial_capital: Starting capital

        Returns:
            Comparison results
        """
        print("=" * 70)
        print("🔍 Strategy Comparison")
        print("=" * 70)
        print(f"Symbol: {symbol}")
        print(f"Exchange: {exchange}")
        print()

        backtester = Backtester(db_path=self.db_path, initial_capital=initial_capital)

        strategies = [
            RSI_Strategy(rsi_buy=30, rsi_sell=70),
            MACD_Strategy(),
            BollingerBands_Strategy()
        ]

        results = []

        for strategy in strategies:
            print(f"Testing {strategy.name}...", end=" ")

            try:
                backtest_result = backtester.run(
                    strategy=strategy,
                    symbol=symbol,
                    exchange=exchange
                )

                if 'error' not in backtest_result:
                    results.append({
                        'strategy': strategy.name,
                        'total_return': backtest_result['total_return'],
                        'sharpe_ratio': backtest_result['sharpe_ratio'],
                        'win_rate': backtest_result['win_rate'],
                        'max_drawdown': backtest_result['max_drawdown'],
                        'profit_factor': backtest_result['profit_factor'],
                        'total_trades': backtest_result['total_trades']
                    })
                    print(f"✅ Return: {backtest_result['total_return']:.2%}, Sharpe: {backtest_result['sharpe_ratio']:.2f}")
                else:
                    print(f"❌ {backtest_result['error']}")

            except Exception as e:
                print(f"❌ Error: {e}")

        if not results:
            return {'error': 'No valid results'}

        # Sort by Sharpe ratio
        results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)

        print()
        print("=" * 70)
        print("📊 STRATEGY RANKING")
        print("=" * 70)
        print()
        print(f"{'Rank':<6} {'Strategy':<25} {'Return':<12} {'Sharpe':<10} {'Win Rate':<12} {'Max DD':<10}")
        print("-" * 70)

        for i, r in enumerate(results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{medal:<6} {r['strategy']:<25} {r['total_return']:>10.2%}  {r['sharpe_ratio']:>8.2f}  {r['win_rate']:>10.1%}  {r['max_drawdown']:>8.1%}")

        print()
        print(f"🏆 Winner: {results[0]['strategy']} (Sharpe: {results[0]['sharpe_ratio']:.2f})")
        print()
        print("=" * 70)

        return {
            'best_strategy': results[0]['strategy'],
            'results': results
        }


if __name__ == "__main__":
    # Find database
    db_path = project_root / "data_output" / "binance_data.db"

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print("Please run data collectors first!")
        exit(1)

    optimizer = StrategyOptimizer(db_path=str(db_path))

    print("\n" + "=" * 70)
    print("🎯 ClaudeCodeCoin - Strategy Optimizer")
    print("=" * 70)
    print()

    # Test 1: Optimize RSI
    print("📊 Test 1: RSI Parameter Optimization")
    print()

    rsi_results = optimizer.optimize_rsi(
        symbol='BTCUSDT',
        exchange='binance',
        rsi_buy_range=[25, 30, 35],
        rsi_sell_range=[65, 70, 75]
    )

    print()
    input("Press Enter to continue to strategy comparison...")
    print()

    # Test 2: Compare strategies
    print("📊 Test 2: Strategy Comparison")
    print()

    comparison = optimizer.compare_strategies(
        symbol='BTCUSDT',
        exchange='binance'
    )

    print()
    print("✅ Optimization Complete!")
