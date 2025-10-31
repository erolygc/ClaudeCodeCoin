"""
Feedback Loop
Learn from performance and adapt strategies
"""

from typing import Dict, List
from datetime import datetime


class FeedbackLoop:
    """
    Analyze performance and provide feedback for system improvement
    """

    def __init__(self):
        """Initialize feedback loop"""
        self.min_sharpe = 2.0
        self.min_win_rate = 0.60
        self.max_drawdown = 0.15

    def analyze_strategy_performance(
        self,
        strategy_results: List[Dict]
    ) -> Dict:
        """
        Analyze individual strategy performance

        Args:
            strategy_results: List of strategy performance dicts

        Returns:
            Analysis with recommendations
        """
        if not strategy_results:
            return {'status': 'no_data'}

        # Sort by Sharpe ratio
        sorted_strategies = sorted(
            strategy_results,
            key=lambda x: x.get('sharpe_ratio', 0),
            reverse=True
        )

        best_strategies = sorted_strategies[:3]
        worst_strategies = sorted_strategies[-3:]

        # Identify strategies to disable
        disable_list = [
            s for s in strategy_results
            if s.get('sharpe_ratio', 0) < self.min_sharpe / 2
            or s.get('max_drawdown', 1) > self.max_drawdown * 1.5
        ]

        return {
            'total_strategies': len(strategy_results),
            'best_strategies': best_strategies,
            'worst_strategies': worst_strategies,
            'disable_recommendations': disable_list,
            'timestamp': datetime.utcnow().isoformat()
        }

    def adjust_allocations(
        self,
        strategy_results: List[Dict]
    ) -> Dict[str, float]:
        """
        Adjust capital allocation based on performance

        Args:
            strategy_results: Strategy performance data

        Returns:
            Dict mapping strategy_id to allocation percentage
        """
        allocations = {}

        # Calculate total Sharpe
        total_sharpe = sum(
            max(0, s.get('sharpe_ratio', 0))
            for s in strategy_results
        )

        if total_sharpe == 0:
            # Equal allocation
            alloc = 1.0 / len(strategy_results)
            return {s['strategy_id']: alloc for s in strategy_results}

        # Allocate based on Sharpe ratio
        for strategy in strategy_results:
            sharpe = max(0, strategy.get('sharpe_ratio', 0))
            allocations[strategy['strategy_id']] = sharpe / total_sharpe

        return allocations

    def generate_feedback_report(self, analysis: Dict) -> str:
        """Generate feedback report"""
        report = []
        report.append("=" * 70)
        report.append("🔄 FEEDBACK LOOP REPORT")
        report.append("=" * 70)
        report.append("")

        report.append(f"Total Strategies: {analysis['total_strategies']}")
        report.append("")

        report.append("🏆 BEST PERFORMING STRATEGIES:")
        for s in analysis['best_strategies']:
            report.append(f"  {s['strategy_id']}: Sharpe {s.get('sharpe_ratio', 0):.2f}")

        report.append("")
        report.append("⚠️  WORST PERFORMING STRATEGIES:")
        for s in analysis['worst_strategies']:
            report.append(f"  {s['strategy_id']}: Sharpe {s.get('sharpe_ratio', 0):.2f}")

        if analysis['disable_recommendations']:
            report.append("")
            report.append("🛑 DISABLE RECOMMENDATIONS:")
            for s in analysis['disable_recommendations']:
                report.append(f"  {s['strategy_id']}")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    feedback = FeedbackLoop()

    # Sample strategy results
    strategies = [
        {'strategy_id': 'RSI_MACD', 'sharpe_ratio': 2.8, 'max_drawdown': 0.10},
        {'strategy_id': 'BB_Mean_Rev', 'sharpe_ratio': 1.2, 'max_drawdown': 0.18},
        {'strategy_id': 'Momentum', 'sharpe_ratio': 3.2, 'max_drawdown': 0.08},
        {'strategy_id': 'Trend_Follow', 'sharpe_ratio': 0.8, 'max_drawdown': 0.25},
    ]

    analysis = feedback.analyze_strategy_performance(strategies)
    report = feedback.generate_feedback_report(analysis)
    print(report)

    print()
    allocations = feedback.adjust_allocations(strategies)
    print("💰 RECOMMENDED ALLOCATIONS:")
    for strategy_id, alloc in allocations.items():
        print(f"  {strategy_id}: {alloc:.1%}")
