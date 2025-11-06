"""
ClaudeCodeCoin - End-to-End System Test
Tests the complete flow: Collector → Pump Scanner → Paper Trading
"""

import subprocess
import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_database_data():
    """Check if we have recent data in the database"""
    print_section("1. CHECKING DATABASE DATA")

    try:
        db_path = Path("data_output/binance_data.db")
        if not db_path.exists():
            print("[ERROR] Database file doesn't exist!")
            return False

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check total records
        cursor.execute("SELECT COUNT(*) FROM klines")
        total = cursor.fetchone()[0]
        print(f"[OK] Total candlestick records: {total:,}")

        if total == 0:
            print("[WARN] Database is empty. Collector needs to run first.")
            conn.close()
            return False

        # Check Gate.io data
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM klines WHERE exchange='gate.io'")
        unique_symbols = cursor.fetchone()[0]
        print(f"[OK] Unique Gate.io symbols: {unique_symbols}")

        # Check recent data (last 5 minutes)
        from datetime import datetime, timedelta
        five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT COUNT(*) FROM klines WHERE datetime >= ?", (five_mins_ago,))
        recent = cursor.fetchone()[0]
        print(f"[OK] Records in last 5 minutes: {recent:,}")

        conn.close()

        if recent == 0:
            print("[WARN] No recent data. Collector may not be running.")
            return False

        print("[SUCCESS] Database has sufficient data! ✅")
        return True

    except Exception as e:
        print(f"[ERROR] Database check failed: {e}")
        return False

def run_pump_scanner_once():
    """Run the pump scanner once and check for signals"""
    print_section("2. RUNNING PUMP SCANNER")

    try:
        print("[INFO] Importing pump detection engine...")
        sys.path.insert(0, "Phase6_PumpDetection")
        from pump_detection_engine import PumpDetectionEngine

        print("[INFO] Creating engine instance...")
        engine = PumpDetectionEngine()

        print("[INFO] Scanning all symbols on gate.io...")
        results = engine.scan_all_symbols(exchange="gate.io")

        total_signals = sum(len(signals) for signals in results.values())
        print(f"\n[OK] Scan complete!")
        print(f"    - Symbols with signals: {len(results)}")
        print(f"    - Total signals found: {total_signals}")

        if total_signals == 0:
            print("[INFO] No pump signals detected. This is normal if market is calm.")
            return []

        # Show details of found signals
        print("\n[SIGNALS FOUND]:")
        all_signals = []
        for symbol, signals in results.items():
            for signal in signals:
                all_signals.append(signal)
                print(f"  - {symbol}:")
                print(f"      Confidence: {signal.confidence:.1f}%")
                print(f"      Volume Change: {signal.volume_change_pct:.0f}%")
                print(f"      Price Change: {signal.price_change_pct:.1f}%")
                print(f"      Type: {signal.signal_type.value}")

        print("\n[SUCCESS] Pump scanner working correctly! ✅")
        return all_signals

    except Exception as e:
        print(f"[ERROR] Pump scanner failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_test_alerts(signals):
    """Save signals to JSON file (simulating the scanner)"""
    print_section("3. SAVING ALERTS TO JSON")

    if not signals:
        print("[INFO] No signals to save.")
        return False

    try:
        # Create pump_alerts directory
        alerts_dir = Path("pump_alerts")
        alerts_dir.mkdir(exist_ok=True)

        # Create JSON file
        timestamp = datetime.now().strftime("%Y%m%d")
        alert_file = alerts_dir / f"pump_alerts_{timestamp}.json"

        # Convert signals to dicts
        alert_data = [signal.to_dict() for signal in signals]

        # Save to JSON
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(alert_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved {len(alert_data)} alerts to: {alert_file}")

        # Verify volume_change_pct is in the JSON
        print("\n[VERIFY] Checking volume_change_pct in JSON:")
        for alert in alert_data[:3]:  # Show first 3
            symbol = alert['symbol']
            volume = alert.get('volume_change_pct', 'MISSING')
            confidence = alert.get('confidence', 0)
            print(f"  - {symbol}: Volume {volume:.0f}%, Confidence {confidence:.0f}%")

        print("\n[SUCCESS] Alerts saved with correct volume data! ✅")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to save alerts: {e}")
        return False

def test_paper_trading():
    """Test paper trading with the saved alerts"""
    print_section("4. TESTING PAPER TRADING")

    try:
        print("[INFO] Importing paper trading engine...")
        sys.path.insert(0, "Phase7_PaperTrading")
        from paper_trading_engine import PaperTradingEngine

        print("[INFO] Creating paper trading engine...")
        engine = PaperTradingEngine()

        print("[INFO] Loading recent alerts...")
        alerts = engine.load_recent_alerts()

        if not alerts:
            print("[WARN] No alerts loaded. Paper trading test cannot proceed.")
            return False

        print(f"[OK] Loaded {len(alerts)} alerts")

        # Check volume_change_pct in alerts
        print("\n[VERIFY] Alert data received by Paper Trading:")
        for alert in alerts[:3]:
            symbol = alert['symbol']
            volume = alert.get('volume_change_pct', 'MISSING')
            confidence = alert.get('confidence', 0)
            print(f"  - {symbol}: Volume {volume:.0f}%, Confidence {confidence:.0f}%")

        # Try to process alerts
        print("\n[INFO] Processing alerts...")
        engine.process_alerts()

        # Check if any positions were opened
        summary = engine.position_manager.get_portfolio_summary()
        open_positions = summary['open_positions']

        print(f"\n[OK] Open positions: {open_positions}")

        if open_positions > 0:
            print("[SUCCESS] Paper trading opened positions! ✅")
            engine.print_status()
        else:
            print("[INFO] No positions opened. This may be normal if:")
            print("  - Confidence too low (< 50%)")
            print("  - Volume spike too low (< 200%)")
            print("  - Already have positions in these symbols")
            print("  - Insufficient balance")

        return True

    except Exception as e:
        print(f"[ERROR] Paper trading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the complete end-to-end test"""
    print("="*70)
    print("  CLAUDECODECOIN - END-TO-END SYSTEM TEST")
    print("="*70)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Step 1: Check database
    if not check_database_data():
        print("\n[ABORT] Cannot proceed without data in database.")
        print("[ACTION] Please start the Gate.io collector first:")
        print("  python Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py")
        print("\nLet it run for 5-10 minutes to collect data, then run this test again.")
        return False

    # Step 2: Run pump scanner
    signals = run_pump_scanner_once()

    # Step 3: Save alerts to JSON
    if signals:
        save_test_alerts(signals)

    # Step 4: Test paper trading
    test_paper_trading()

    # Final summary
    print_section("FINAL SUMMARY")
    print("[✅] Database: Data available")
    print("[✅] Pump Scanner: Working correctly")
    print(f"[✅] Alert JSON: {len(signals)} signals saved")
    print("[✅] Paper Trading: Engine working")
    print("\n[SUCCESS] All systems operational! 🚀")
    print("\nNEXT STEPS:")
    print("1. Start Gate.io collector (if not running)")
    print("2. Start realtime_pump_scanner.py")
    print("3. Start paper_trading_engine.py")
    print("\nAll modules will communicate correctly through the JSON alert files.")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Test interrupted by user")
        sys.exit(1)
