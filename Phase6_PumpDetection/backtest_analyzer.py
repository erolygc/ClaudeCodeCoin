"""
ClaudeCodeCoin - Backtest Analyzer
Analyzes historical trades to calculate signal win rates and optimize parameters
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BacktestAnalyzer:
    """Analyze historical performance and calculate optimal parameters"""

    def __init__(self, trades_db: str = "data_output/paper_trading.db",
                 alerts_dir: str = "pump_alerts"):
        self.trades_db = trades_db
        self.alerts_dir = Path(alerts_dir)

    def analyze_signal_performance(self, days_back: int = 7) -> dict:
        """Analyze win rates by signal type"""
        try:
            conn = sqlite3.connect(self.trades_db)

            # Get closed positions from last N days
            cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            query = """
                SELECT symbol, entry_time, exit_time, entry_price, exit_price,
                       pnl, pnl_percent, confidence
                FROM positions
                WHERE status = 'CLOSED'
                  AND DATE(entry_time) >= ?
            """

            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
            conn.close()

            if df.empty:
                logger.warning("No closed trades found in the specified period")
                return {}

            # Load pump alerts to match trades with signal types
            signal_performance = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0})

            for _, trade in df.iterrows():
                symbol = trade['symbol']
                entry_time = pd.to_datetime(trade['entry_time'])

                # Find corresponding alert
                signal_type = self._find_signal_type_for_trade(symbol, entry_time)

                if signal_type:
                    signal_performance[signal_type]['total'] += 1
                    if trade['pnl'] > 0:
                        signal_performance[signal_type]['wins'] += 1
                    else:
                        signal_performance[signal_type]['losses'] += 1

            # Calculate win rates
            results = {}
            for signal_type, stats in signal_performance.items():
                win_rate = stats['wins'] / stats['total'] if stats['total'] > 0 else 0
                results[signal_type] = {
                    'win_rate': win_rate,
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'total': stats['total'],
                    'confidence_multiplier': max(0.5, min(1.5, win_rate / 0.5))  # Scale 0.5-1.5
                }

            return results

        except Exception as e:
            logger.error(f"Error analyzing signal performance: {e}")
            return {}

    def _find_signal_type_for_trade(self, symbol: str, entry_time: datetime) -> str:
        """Find the signal type that triggered this trade"""
        try:
            # Look in alert files around the entry time
            date_str = entry_time.strftime('%Y%m%d')
            alert_file = self.alerts_dir / f"pump_alerts_{date_str}.json"

            if not alert_file.exists():
                return 'unknown'

            with open(alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                alerts = data if isinstance(data, list) else data.get('alerts', [])

            # Find alert within 10 minutes of entry time
            for alert in alerts:
                if alert['symbol'] == symbol:
                    alert_time = pd.to_datetime(alert['timestamp'])
                    time_diff = abs((alert_time - entry_time).total_seconds())

                    if time_diff < 600:  # Within 10 minutes
                        return alert.get('signal_type', 'unknown')

            return 'unknown'

        except Exception as e:
            logger.warning(f"Could not find signal type for {symbol}: {e}")
            return 'unknown'

    def analyze_hourly_performance(self, days_back: int = 7) -> dict:
        """Analyze win rates by hour of day"""
        try:
            conn = sqlite3.connect(self.trades_db)

            cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            query = """
                SELECT entry_time, pnl
                FROM positions
                WHERE status = 'CLOSED'
                  AND DATE(entry_time) >= ?
            """

            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
            conn.close()

            if df.empty:
                return {}

            df['entry_time'] = pd.to_datetime(df['entry_time'])
            df['hour'] = df['entry_time'].dt.hour
            df['win'] = df['pnl'] > 0

            # Group by hour ranges
            hourly_stats = {}
            hour_ranges = [
                ('00-04', range(0, 4)),
                ('04-08', range(4, 8)),
                ('08-12', range(8, 12)),
                ('12-16', range(12, 16)),
                ('16-20', range(16, 20)),
                ('20-24', range(20, 24))
            ]

            for range_name, hours in hour_ranges:
                mask = df['hour'].isin(hours)
                range_df = df[mask]

                if len(range_df) > 0:
                    win_rate = range_df['win'].sum() / len(range_df)
                    hourly_stats[range_name] = {
                        'win_rate': win_rate,
                        'total_trades': len(range_df),
                        'multiplier': max(0.7, min(1.2, win_rate / 0.5))  # Scale 0.7-1.2
                    }

            return hourly_stats

        except Exception as e:
            logger.error(f"Error analyzing hourly performance: {e}")
            return {}

    def analyze_coin_performance(self, min_trades: int = 3) -> dict:
        """Analyze performance by coin"""
        try:
            conn = sqlite3.connect(self.trades_db)

            query = """
                SELECT symbol,
                       COUNT(*) as total_trades,
                       SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losses,
                       AVG(pnl_percent) as avg_pnl_pct,
                       SUM(pnl) as total_pnl
                FROM positions
                WHERE status = 'CLOSED'
                GROUP BY symbol
                HAVING total_trades >= ?
                ORDER BY win_rate DESC
            """

            df = pd.read_sql_query(query, conn, params=(min_trades,))
            conn.close()

            if df.empty:
                return {}

            df['win_rate'] = df['wins'] / df['total_trades']

            results = {}
            for _, row in df.iterrows():
                results[row['symbol']] = {
                    'win_rate': row['win_rate'],
                    'total_trades': row['total_trades'],
                    'wins': row['wins'],
                    'losses': row['losses'],
                    'avg_pnl_pct': row['avg_pnl_pct'],
                    'total_pnl': row['total_pnl'],
                    'recommendation': 'whitelist' if row['win_rate'] > 0.7 else 'blacklist' if row['win_rate'] < 0.3 else 'neutral'
                }

            return results

        except Exception as e:
            logger.error(f"Error analyzing coin performance: {e}")
            return {}

    def generate_report(self, days_back: int = 7) -> str:
        """Generate comprehensive backtest report"""
        logger.info(f"Generating backtest report for last {days_back} days...")

        report = []
        report.append("=" * 80)
        report.append("CLAUDECODECOIN - BACKTEST ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Analysis Period: Last {days_back} days")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Signal Type Performance
        report.append("\n1. SIGNAL TYPE PERFORMANCE")
        report.append("-" * 80)
        signal_perf = self.analyze_signal_performance(days_back)

        if signal_perf:
            for signal_type, stats in sorted(signal_perf.items(), key=lambda x: x[1]['win_rate'], reverse=True):
                report.append(f"\n{signal_type.upper()}:")
                report.append(f"  Win Rate: {stats['win_rate']:.1%} ({stats['wins']}W / {stats['losses']}L)")
                report.append(f"  Total Trades: {stats['total']}")
                report.append(f"  Recommended Multiplier: {stats['confidence_multiplier']:.2f}x")
        else:
            report.append("  No data available")

        # Hourly Performance
        report.append("\n\n2. HOURLY PERFORMANCE")
        report.append("-" * 80)
        hourly_perf = self.analyze_hourly_performance(days_back)

        if hourly_perf:
            for time_range, stats in sorted(hourly_perf.items()):
                report.append(f"\n{time_range}:")
                report.append(f"  Win Rate: {stats['win_rate']:.1%} ({stats['total_trades']} trades)")
                report.append(f"  Recommended Multiplier: {stats['multiplier']:.2f}x")
        else:
            report.append("  No data available")

        # Coin Performance
        report.append("\n\n3. TOP/BOTTOM PERFORMING COINS")
        report.append("-" * 80)
        coin_perf = self.analyze_coin_performance()

        if coin_perf:
            # Top performers
            report.append("\nTOP 10 PERFORMERS:")
            top_coins = sorted(coin_perf.items(), key=lambda x: x[1]['win_rate'], reverse=True)[:10]
            for symbol, stats in top_coins:
                report.append(f"  {symbol}: {stats['win_rate']:.1%} WR, "
                            f"${stats['total_pnl']:.2f} P&L ({stats['total_trades']} trades)")

            # Bottom performers (potential blacklist)
            report.append("\nBOTTOM 10 PERFORMERS (Consider Blacklist):")
            bottom_coins = sorted(coin_perf.items(), key=lambda x: x[1]['win_rate'])[:10]
            for symbol, stats in bottom_coins:
                if stats['win_rate'] < 0.3:
                    report.append(f"  {symbol}: {stats['win_rate']:.1%} WR, "
                                f"${stats['total_pnl']:.2f} P&L ({stats['total_trades']} trades) ⚠️ BLACKLIST")
        else:
            report.append("  No data available")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def export_optimized_parameters(self, output_file: str = "optimized_params.json"):
        """Export optimized parameters based on backtest"""
        logger.info("Calculating optimized parameters...")

        signal_perf = self.analyze_signal_performance(7)
        hourly_perf = self.analyze_hourly_performance(7)

        params = {
            'signal_win_rates': {
                signal_type: stats['confidence_multiplier']
                for signal_type, stats in signal_perf.items()
            },
            'hourly_performance': {
                time_range: stats['multiplier']
                for time_range, stats in hourly_perf.items()
            },
            'generated_at': datetime.now().isoformat(),
            'analysis_period_days': 7
        }

        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(params, f, indent=2)

        logger.info(f"Optimized parameters exported to {output_path}")
        return params


def main():
    """Run backtest analysis"""
    analyzer = BacktestAnalyzer(
        trades_db="../data_output/paper_trading.db",
        alerts_dir="../pump_alerts"
    )

    # Generate report
    report = analyzer.generate_report(days_back=7)
    print(report)

    # Export optimized parameters
    params = analyzer.export_optimized_parameters("optimized_params.json")

    print("\n" + "=" * 80)
    print("OPTIMIZED PARAMETERS:")
    print("=" * 80)
    print(json.dumps(params, indent=2))


if __name__ == "__main__":
    main()
