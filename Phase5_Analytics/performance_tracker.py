"""
Performance Tracker
Calculate and track trading performance metrics
"""

from typing import Dict, List
import math
from datetime import datetime


class PerformanceTracker:
    """
    Track and calculate performance metrics
    """

    def __init__(self):
        """Initialize performance tracker"""
        self.trades = []
        self.equity_curve = []

    def calculate_metrics(self, trades: List[Dict], initial_capital: float) -> Dict:
        """
        Calculate comprehensive performance metrics

        Args:
            trades: List of trade dicts
            initial_capital: Starting capital

        Returns:
            Performance metrics dict
        """
        if not trades:
            return {'error': 'No trades to analyze'}

        # Separate wins and losses
        wins = [t['pnl'] for t in trades if t['pnl'] > 0]
        losses = [t['pnl'] for t in trades if t['pnl'] < 0]

        total_pnl = sum(t['pnl'] for t in trades)
        total_return = total_pnl / initial_capital

        win_rate = len(wins) / len(trades) if trades else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Sharpe Ratio (simplified)
        returns = [t['pnl'] / initial_capital for t in trades]
        avg_return = sum(returns) / len(returns) if returns else 0
        std_dev = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns)) if len(returns) > 1 else 0
        sharpe_ratio = (avg_return / std_dev * math.sqrt(252)) if std_dev > 0 else 0

        # Max Drawdown
        equity = initial_capital
        peak = initial_capital
        max_dd = 0

        for trade in trades:
            equity += trade['pnl']
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd

        return {
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd,
            'final_equity': initial_capital + total_pnl
        }

    def generate_report(self, metrics: Dict) -> str:
        """
        Generate human-readable performance report

        Args:
            metrics: Performance metrics dict

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("📊 PERFORMANCE REPORT")
        report.append("=" * 70)
        report.append("")

        report.append(f"Total Trades: {metrics['total_trades']}")
        report.append(f"Win Rate: {metrics['win_rate']:.1%}")
        report.append(f"Total P&L: ${metrics['total_pnl']:,.2f}")
        report.append(f"Total Return: {metrics['total_return']:.1%}")
        report.append("")

        report.append(f"Average Win: ${metrics['avg_win']:,.2f}")
        report.append(f"Average Loss: ${metrics['avg_loss']:,.2f}")
        report.append(f"Profit Factor: {metrics['profit_factor']:.2f}")
        report.append("")

        report.append(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        report.append(f"Max Drawdown: {metrics['max_drawdown']:.1%}")
        report.append("")

        report.append(f"Final Equity: ${metrics['final_equity']:,.2f}")
        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    tracker = PerformanceTracker()

    # Sample trades
    sample_trades = [
        {'pnl': 100, 'symbol': 'BTCUSDT'},
        {'pnl': -50, 'symbol': 'ETHUSDT'},
        {'pnl': 150, 'symbol': 'BTCUSDT'},
        {'pnl': 80, 'symbol': 'SOLUSDT'},
        {'pnl': -30, 'symbol': 'ETHUSDT'},
        {'pnl': 200, 'symbol': 'BTCUSDT'},
        {'pnl': -40, 'symbol': 'BNBUSDT'},
        {'pnl': 120, 'symbol': 'BTCUSDT'},
    ]

    metrics = tracker.calculate_metrics(sample_trades, initial_capital=10000)
    report = tracker.generate_report(metrics)

    print(report)
