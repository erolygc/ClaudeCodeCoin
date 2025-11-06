"""
ClaudeCodeCoin - Comprehensive System Test
Tests every component end-to-end with detailed diagnostics
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_result(success, message):
    """Print test result"""
    status = "[✓]" if success else "[✗]"
    print(f"{status} {message}")
    return success

# ============================================================================
# STEP 1: DATABASE & DATA COLLECTION
# ============================================================================

def test_database():
    print_header("STEP 1: DATABASE & DATA COLLECTION")

    all_ok = True

    try:
        db_path = "data_output/binance_data.db"
        conn = sqlite3.connect(db_path)

        # Total records
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM klines")
        total = cursor.fetchone()[0]
        all_ok &= print_result(total > 0, f"Database has {total:,} total records")

        # Recent data (last 10 minutes)
        ten_mins_ago = (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT COUNT(*) FROM klines WHERE datetime >= ?", (ten_mins_ago,))
        recent = cursor.fetchone()[0]
        all_ok &= print_result(recent > 100, f"Recent data (10 min): {recent:,} records")

        # Gate.io symbols
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM klines WHERE exchange='gate.io'")
        symbols = cursor.fetchone()[0]
        all_ok &= print_result(symbols > 100, f"Gate.io symbols: {symbols}")

        # Sample data quality
        cursor.execute("""
            SELECT symbol, COUNT(*) as cnt, MIN(datetime), MAX(datetime)
            FROM klines
            WHERE exchange='gate.io'
            GROUP BY symbol
            ORDER BY cnt DESC
            LIMIT 3
        """)

        print("\n  Sample Coin Data Quality:")
        for row in cursor.fetchall():
            symbol, cnt, min_dt, max_dt = row
            print(f"    {symbol}: {cnt} bars | {min_dt} → {max_dt}")

        conn.close()

    except Exception as e:
        all_ok &= print_result(False, f"Database error: {e}")

    return all_ok

# ============================================================================
# STEP 2: INDICATOR CALCULATIONS
# ============================================================================

def test_indicators():
    print_header("STEP 2: PUMP DETECTION - INDICATOR CALCULATIONS")

    all_ok = True

    try:
        sys.path.insert(0, "Phase6_PumpDetection")
        from pump_detection_engine import PumpDetectionEngine

        engine = PumpDetectionEngine()

        # Get sample data
        conn = sqlite3.connect("data_output/binance_data.db")
        query = """
            SELECT timestamp, datetime, open, high, low, close, volume
            FROM klines
            WHERE symbol = '1m_BTC_USDT' AND exchange = 'gate.io'
            ORDER BY timestamp DESC
            LIMIT 120
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        all_ok &= print_result(len(df) >= 20, f"Sample data: {len(df)} bars for BTC_USDT")

        if len(df) >= 20:
            # Sort and calculate indicators
            df = df.sort_values('timestamp').reset_index(drop=True)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = engine._calculate_indicators(df)

            latest = df.iloc[-1]

            # Check volume_ratio
            volume_ratio = latest.get('volume_ratio', None)
            is_valid = volume_ratio is not None and not pd.isna(volume_ratio)
            all_ok &= print_result(is_valid, f"volume_ratio: {volume_ratio:.2f}" if is_valid else "volume_ratio: INVALID")

            # Check volatility_ratio
            volatility_ratio = latest.get('volatility_ratio', None)
            is_valid = volatility_ratio is not None and not pd.isna(volatility_ratio)
            all_ok &= print_result(is_valid, f"volatility_ratio: {volatility_ratio:.2f}" if is_valid else "volatility_ratio: INVALID")

            # Check RSI
            rsi = latest.get('rsi', None)
            is_valid = rsi is not None and not pd.isna(rsi) and 0 <= rsi <= 100
            all_ok &= print_result(is_valid, f"RSI: {rsi:.1f}" if is_valid else "RSI: INVALID")

            # Check price changes
            price_change_5 = latest.get('price_change_5', None)
            is_valid = price_change_5 is not None and not pd.isna(price_change_5)
            all_ok &= print_result(is_valid, f"Price change (5 bars): {price_change_5:.2f}%" if is_valid else "Price change: INVALID")

            print("\n  Indicator Summary (BTC_USDT last bar):")
            print(f"    Volume: {latest['volume']:.2f}")
            print(f"    Volume MA(20): {latest.get('volume_ma_20', 0):.2f}")
            print(f"    Volume Ratio: {volume_ratio:.2f}" if not pd.isna(volume_ratio) else "    Volume Ratio: NaN")
            print(f"    Price: ${latest['close']:.2f}")
            print(f"    RSI: {rsi:.1f}" if not pd.isna(rsi) else "    RSI: NaN")

    except Exception as e:
        all_ok &= print_result(False, f"Indicator calculation error: {e}")
        import traceback
        traceback.print_exc()

    return all_ok

# ============================================================================
# STEP 3: SIGNAL GENERATION
# ============================================================================

def test_signal_generation():
    print_header("STEP 3: SIGNAL GENERATION")

    all_ok = True

    try:
        sys.path.insert(0, "Phase6_PumpDetection")
        from pump_detection_engine import PumpDetectionEngine

        engine = PumpDetectionEngine()

        # Test on multiple symbols
        test_symbols = ['1m_BTC_USDT', '1m_ETH_USDT', '1m_SOL_USDT']

        for symbol in test_symbols:
            signals = engine.analyze_symbol(symbol, exchange="gate.io")

            print(f"\n  {symbol}:")
            if signals:
                for sig in signals:
                    print(f"    [{sig.signal_type.value}] Confidence: {sig.confidence:.1f}%")
                    print(f"      Volume Change: {sig.volume_change_pct:.1f}%")
                    print(f"      Price Change: {sig.price_change_pct:.1f}%")

                    # Validate signal data
                    has_valid_confidence = 0 <= sig.confidence <= 100
                    has_volume = sig.volume_change_pct >= 0

                    all_ok &= print_result(has_valid_confidence, f"      Valid confidence: {sig.confidence:.1f}%")
                    all_ok &= print_result(has_volume, f"      Volume data exists: {sig.volume_change_pct:.1f}%")
            else:
                print(f"    No signals (market calm)")

    except Exception as e:
        all_ok &= print_result(False, f"Signal generation error: {e}")
        import traceback
        traceback.print_exc()

    return all_ok

# ============================================================================
# STEP 4: JSON SERIALIZATION
# ============================================================================

def test_json_serialization():
    print_header("STEP 4: JSON ALERT SERIALIZATION")

    all_ok = True

    try:
        # Check if alerts directory exists
        alerts_dir = Path("pump_alerts")
        all_ok &= print_result(alerts_dir.exists(), f"Alerts directory exists: {alerts_dir}")

        if alerts_dir.exists():
            # Find today's alert file
            today = datetime.now().strftime("%Y%m%d")
            alert_file = alerts_dir / f"pump_alerts_{today}.json"

            if alert_file.exists():
                all_ok &= print_result(True, f"Today's alert file exists: {alert_file.name}")

                # Load and validate JSON
                with open(alert_file, 'r', encoding='utf-8') as f:
                    alerts = json.load(f)

                all_ok &= print_result(len(alerts) > 0, f"Alert count: {len(alerts)}")

                if alerts:
                    # Check first alert structure
                    first = alerts[0]
                    required_fields = ['symbol', 'confidence', 'volume_change_pct',
                                     'price_change_pct', 'signal_type', 'timestamp']

                    print("\n  First Alert Structure:")
                    for field in required_fields:
                        has_field = field in first
                        value = first.get(field, 'MISSING')
                        all_ok &= print_result(has_field, f"    {field}: {value}")

                    # Check volume distribution
                    volume_counts = {'zero': 0, 'nonzero': 0}
                    for alert in alerts:
                        vol = alert.get('volume_change_pct', 0)
                        if vol == 0:
                            volume_counts['zero'] += 1
                        else:
                            volume_counts['nonzero'] += 1

                    print(f"\n  Volume Distribution:")
                    print(f"    Alerts with volume=0: {volume_counts['zero']}")
                    print(f"    Alerts with volume>0: {volume_counts['nonzero']}")

                    # This is expected! price_surge can have 0% volume if no volume spike

            else:
                all_ok &= print_result(False, "No alert file found - run pump scanner first")

    except Exception as e:
        all_ok &= print_result(False, f"JSON serialization error: {e}")
        import traceback
        traceback.print_exc()

    return all_ok

# ============================================================================
# STEP 5: PAPER TRADING INTEGRATION
# ============================================================================

def test_paper_trading():
    print_header("STEP 5: PAPER TRADING INTEGRATION")

    all_ok = True

    try:
        sys.path.insert(0, "Phase7_PaperTrading")
        from paper_trading_engine import PaperTradingEngine
        import config

        print(f"\n  Configuration:")
        print(f"    MIN_CONFIDENCE: {config.MIN_CONFIDENCE_TO_TRADE}%")
        print(f"    MIN_VOLUME_SPIKE: {config.MIN_VOLUME_SPIKE}%")
        print(f"    MAX_POSITIONS: {config.MAX_OPEN_POSITIONS}")

        # Create engine
        engine = PaperTradingEngine()
        all_ok &= print_result(True, "Paper trading engine created")

        # Load alerts
        alerts = engine.load_recent_alerts()
        all_ok &= print_result(len(alerts) > 0, f"Loaded {len(alerts)} recent alerts")

        if alerts:
            # Analyze why positions aren't opening
            print(f"\n  Alert Analysis:")

            passed_count = 0
            failed_count = 0
            failure_reasons = {}

            for alert in alerts[:10]:  # Check first 10
                symbol = alert['symbol']
                confidence = alert.get('confidence', 0)
                volume = alert.get('volume_change_pct', 0)

                # Check filters
                reasons = []

                if confidence < config.MIN_CONFIDENCE_TO_TRADE:
                    reasons.append(f"Low confidence ({confidence:.1f}% < {config.MIN_CONFIDENCE_TO_TRADE}%)")

                if volume < config.MIN_VOLUME_SPIKE:
                    reasons.append(f"Low volume ({volume:.1f}% < {config.MIN_VOLUME_SPIKE}%)")

                if reasons:
                    failed_count += 1
                    reason_str = ", ".join(reasons)
                    print(f"    [X] {symbol}: {reason_str}")

                    for r in reasons:
                        failure_reasons[r] = failure_reasons.get(r, 0) + 1
                else:
                    passed_count += 1
                    print(f"    [✓] {symbol}: PASSED (C={confidence:.1f}%, V={volume:.1f}%)")

            print(f"\n  Summary:")
            print(f"    Alerts passing filters: {passed_count}")
            print(f"    Alerts failing filters: {failed_count}")

            if failure_reasons:
                print(f"\n  Failure Breakdown:")
                for reason, count in sorted(failure_reasons.items(), key=lambda x: -x[1]):
                    print(f"    {reason}: {count} alerts")

    except Exception as e:
        all_ok &= print_result(False, f"Paper trading integration error: {e}")
        import traceback
        traceback.print_exc()

    return all_ok

# ============================================================================
# STEP 6: FINAL REPORT
# ============================================================================

def generate_report(results):
    print_header("COMPREHENSIVE TEST REPORT")

    all_passed = all(results.values())

    print("\n  Test Results:")
    for step, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"    [{status}] {step}")

    print("\n" + "="*80)
    if all_passed:
        print("  ✓ ALL SYSTEMS OPERATIONAL")
        print("="*80)
        print("\n  System is ready for production use!")
    else:
        print("  ✗ SOME ISSUES DETECTED")
        print("="*80)
        print("\n  Review failed steps above and fix issues.")

    return all_passed

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*80)
    print("  CLAUDECODECOIN - COMPREHENSIVE SYSTEM TEST")
    print("="*80)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    results = {}

    # Run all tests
    results['Database & Data Collection'] = test_database()
    results['Indicator Calculations'] = test_indicators()
    results['Signal Generation'] = test_signal_generation()
    results['JSON Serialization'] = test_json_serialization()
    results['Paper Trading Integration'] = test_paper_trading()

    # Generate report
    all_passed = generate_report(results)

    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
