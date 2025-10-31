"""
Data Quality Validator
Checks data quality and detects anomalies in collected market data
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class DataQualityValidator:
    """
    Validates data quality and detects anomalies
    """

    def __init__(self, db_path: str = "data_output/binance_data.db"):
        """
        Initialize validator

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)

    def check_missing_candles(
        self,
        symbol: str,
        exchange: str = "binance",
        interval_minutes: int = 1
    ) -> List[Tuple[int, int]]:
        """
        Check for missing candles (gaps in data)

        Args:
            symbol: Trading symbol
            exchange: Exchange name
            interval_minutes: Candle interval in minutes

        Returns:
            List of (expected_timestamp, gap_duration_minutes) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp
            FROM klines
            WHERE symbol = ? AND exchange = ?
            ORDER BY timestamp ASC
        """, (symbol, exchange))

        timestamps = [row[0] for row in cursor.fetchall()]
        conn.close()

        if len(timestamps) < 2:
            return []

        gaps = []
        interval_ms = interval_minutes * 60 * 1000

        for i in range(1, len(timestamps)):
            expected = timestamps[i-1] + interval_ms
            actual = timestamps[i]
            diff = actual - expected

            if diff > interval_ms:
                # Gap detected
                gap_minutes = diff // (60 * 1000)
                gaps.append((expected, gap_minutes))

        return gaps

    def check_price_anomalies(
        self,
        symbol: str,
        exchange: str = "binance",
        threshold_percent: float = 10.0
    ) -> List[Dict[str, any]]:
        """
        Check for unusual price movements (potential data errors)

        Args:
            symbol: Trading symbol
            exchange: Exchange name
            threshold_percent: Percentage change threshold

        Returns:
            List of anomalies with details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, datetime, open, high, low, close
            FROM klines
            WHERE symbol = ? AND exchange = ?
            ORDER BY timestamp ASC
        """, (symbol, exchange))

        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 2:
            return []

        anomalies = []

        for i in range(1, len(rows)):
            prev_close = rows[i-1][5]
            curr_open = rows[i][2]
            curr_high = rows[i][3]
            curr_low = rows[i][4]
            curr_close = rows[i][5]

            # Check for huge gaps between candles
            gap_percent = abs((curr_open - prev_close) / prev_close * 100)
            if gap_percent > threshold_percent:
                anomalies.append({
                    'type': 'price_gap',
                    'timestamp': rows[i][0],
                    'datetime': rows[i][1],
                    'prev_close': prev_close,
                    'curr_open': curr_open,
                    'gap_percent': gap_percent
                })

            # Check for impossible OHLC relationships
            if curr_low > curr_high:
                anomalies.append({
                    'type': 'invalid_ohlc',
                    'timestamp': rows[i][0],
                    'datetime': rows[i][1],
                    'error': 'low > high',
                    'high': curr_high,
                    'low': curr_low
                })

            if curr_close > curr_high or curr_close < curr_low:
                anomalies.append({
                    'type': 'invalid_ohlc',
                    'timestamp': rows[i][0],
                    'datetime': rows[i][1],
                    'error': 'close outside high/low range',
                    'high': curr_high,
                    'low': curr_low,
                    'close': curr_close
                })

            if curr_open > curr_high or curr_open < curr_low:
                anomalies.append({
                    'type': 'invalid_ohlc',
                    'timestamp': rows[i][0],
                    'datetime': rows[i][1],
                    'error': 'open outside high/low range',
                    'high': curr_high,
                    'low': curr_low,
                    'open': curr_open
                })

        return anomalies

    def check_volume_anomalies(
        self,
        symbol: str,
        exchange: str = "binance",
        threshold_multiplier: float = 10.0
    ) -> List[Dict[str, any]]:
        """
        Check for unusual volume spikes

        Args:
            symbol: Trading symbol
            exchange: Exchange name
            threshold_multiplier: How many times average volume

        Returns:
            List of volume anomalies
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, datetime, volume
            FROM klines
            WHERE symbol = ? AND exchange = ?
            ORDER BY timestamp ASC
        """, (symbol, exchange))

        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 10:
            return []

        volumes = [row[2] for row in rows]
        avg_volume = sum(volumes) / len(volumes)

        anomalies = []

        for row in rows:
            timestamp, dt, volume = row

            if volume > avg_volume * threshold_multiplier:
                anomalies.append({
                    'type': 'volume_spike',
                    'timestamp': timestamp,
                    'datetime': dt,
                    'volume': volume,
                    'avg_volume': avg_volume,
                    'multiplier': volume / avg_volume if avg_volume > 0 else 0
                })

            if volume == 0:
                anomalies.append({
                    'type': 'zero_volume',
                    'timestamp': timestamp,
                    'datetime': dt
                })

        return anomalies

    def check_duplicate_candles(
        self,
        symbol: str,
        exchange: str = "binance"
    ) -> List[int]:
        """
        Check for duplicate candles (same timestamp)

        Args:
            symbol: Trading symbol
            exchange: Exchange name

        Returns:
            List of duplicate timestamps
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, COUNT(*) as count
            FROM klines
            WHERE symbol = ? AND exchange = ?
            GROUP BY timestamp
            HAVING count > 1
        """, (symbol, exchange))

        duplicates = [row[0] for row in cursor.fetchall()]
        conn.close()

        return duplicates

    def validate_symbol(
        self,
        symbol: str,
        exchange: str = "binance"
    ) -> Dict[str, any]:
        """
        Run all validation checks for a symbol

        Args:
            symbol: Trading symbol
            exchange: Exchange name

        Returns:
            Dict with validation results
        """
        print(f"🔍 Validating {symbol} on {exchange}...")

        results = {
            'symbol': symbol,
            'exchange': exchange,
            'timestamp': datetime.utcnow().isoformat(),
            'missing_candles': [],
            'price_anomalies': [],
            'volume_anomalies': [],
            'duplicate_timestamps': [],
            'total_candles': 0,
            'is_valid': True
        }

        # Get total candle count
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM klines
            WHERE symbol = ? AND exchange = ?
        """, (symbol, exchange))
        results['total_candles'] = cursor.fetchone()[0]
        conn.close()

        # Check for missing candles
        missing = self.check_missing_candles(symbol, exchange)
        results['missing_candles'] = missing
        if missing:
            print(f"  ⚠️  Found {len(missing)} gaps in data")
            results['is_valid'] = False

        # Check for price anomalies
        price_anom = self.check_price_anomalies(symbol, exchange)
        results['price_anomalies'] = price_anom
        if price_anom:
            print(f"  ⚠️  Found {len(price_anom)} price anomalies")
            results['is_valid'] = False

        # Check for volume anomalies
        volume_anom = self.check_volume_anomalies(symbol, exchange)
        results['volume_anomalies'] = volume_anom
        if volume_anom:
            print(f"  ⚠️  Found {len(volume_anom)} volume anomalies")

        # Check for duplicates
        dupes = self.check_duplicate_candles(symbol, exchange)
        results['duplicate_timestamps'] = dupes
        if dupes:
            print(f"  ⚠️  Found {len(dupes)} duplicate timestamps")
            results['is_valid'] = False

        if results['is_valid']:
            print(f"  ✅ Data quality OK ({results['total_candles']} candles)")

        return results

    def validate_all_symbols(self) -> List[Dict[str, any]]:
        """
        Validate all symbols in database

        Returns:
            List of validation results for each symbol
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT symbol, exchange
            FROM klines
        """)

        symbols = cursor.fetchall()
        conn.close()

        results = []

        print("=" * 70)
        print("🔍 Data Quality Validation")
        print("=" * 70)
        print()

        for symbol, exchange in symbols:
            result = self.validate_symbol(symbol, exchange)
            results.append(result)
            print()

        return results

    def generate_report(self, results: List[Dict[str, any]]) -> str:
        """
        Generate human-readable validation report

        Args:
            results: List of validation results

        Returns:
            Report string
        """
        report = []
        report.append("=" * 70)
        report.append("📊 DATA QUALITY REPORT")
        report.append("=" * 70)
        report.append("")

        total_symbols = len(results)
        valid_symbols = sum(1 for r in results if r['is_valid'])
        total_candles = sum(r['total_candles'] for r in results)

        report.append(f"Total Symbols: {total_symbols}")
        report.append(f"Valid Symbols: {valid_symbols} ({valid_symbols/total_symbols*100:.1f}%)")
        report.append(f"Total Candles: {total_candles:,}")
        report.append("")

        # Summary by symbol
        report.append("SYMBOL SUMMARY:")
        report.append("-" * 70)

        for result in results:
            status = "✅" if result['is_valid'] else "⚠️"
            report.append(
                f"{status} {result['exchange']}:{result['symbol']} - "
                f"{result['total_candles']} candles"
            )

            if result['missing_candles']:
                report.append(f"   ⚠️  {len(result['missing_candles'])} gaps")

            if result['price_anomalies']:
                report.append(f"   ⚠️  {len(result['price_anomalies'])} price anomalies")

            if result['duplicate_timestamps']:
                report.append(f"   ⚠️  {len(result['duplicate_timestamps'])} duplicates")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    validator = DataQualityValidator()
    results = validator.validate_all_symbols()

    print()
    report = validator.generate_report(results)
    print(report)
