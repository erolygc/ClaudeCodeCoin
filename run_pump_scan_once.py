"""
Pump Scanner - Tek Seferlik Tarama
Test için tüm coinleri tara ve sonuçları göster
"""
import sys
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).parent / "Phase6_PumpDetection"))

from Phase6_PumpDetection.pump_detection_engine import PumpDetectionEngine

def main():
    print("=" * 80)
    print("PUMP SCANNER - SINGLE SCAN")
    print("=" * 80)
    print()

    engine = PumpDetectionEngine(db_path="data_output/binance_data.db")

    # Test sembolleri
    symbols = [
        "BTC_USDT", "ETH_USDT", "SOL_USDT", "PEPE_USDT", "SHIB_USDT",
        "WIF_USDT", "BONK_USDT", "FLOKI_USDT", "DOGE_USDT", "ARB_USDT",
        "OP_USDT", "MATIC_USDT", "AVAX_USDT", "LINK_USDT", "UNI_USDT",
    ]

    print(f"Scanning {len(symbols)} symbols for pump signals...\n")

    all_signals = []

    for symbol in symbols:
        print(f"📊 Analyzing {symbol}...", end=" ")

        try:
            signals = engine.analyze_symbol(symbol, exchange="gate.io")

            if signals:
                print(f"✅ {len(signals)} signal(s) found!")
                for signal in signals:
                    all_signals.append(signal)
                    print(f"   🔔 {signal.level.value.upper()}: {signal.message}")
                    print(f"      Confidence: {signal.confidence:.1f}%")
                    print(f"      Price change: {signal.price_change_pct:+.2f}%")
                    print(f"      Volume change: {signal.volume_change_pct:+.0f}%")
            else:
                print("⚪ No signals")

        except Exception as e:
            print(f"❌ Error: {e}")

    print()
    print("=" * 80)
    print(f"SCAN COMPLETE")
    print("=" * 80)
    print(f"Total signals found: {len(all_signals)}")

    if all_signals:
        print()
        print("🔥 TOP PUMP SIGNALS:")
        print("-" * 80)

        # Confidence'a göre sırala
        sorted_signals = sorted(all_signals, key=lambda x: x.confidence, reverse=True)

        for i, signal in enumerate(sorted_signals[:5], 1):
            print(f"{i}. {signal.symbol}")
            print(f"   Level: {signal.level.value.upper()} | Confidence: {signal.confidence:.1f}%")
            print(f"   Price: {signal.price_change_pct:+.2f}% | Volume: {signal.volume_change_pct:+.0f}%")
            print(f"   Message: {signal.message}")
            print()

        # Pump alert dosyasını oluştur (paper trading için)
        import json
        from datetime import datetime

        alert_file = Path("pump_alerts") / f"pump_alerts_{datetime.now().strftime('%Y%m%d')}.json"
        alert_file.parent.mkdir(exist_ok=True)

        alerts_data = [s.to_dict() for s in all_signals]

        with open(alert_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)

        print(f"💾 Alerts saved to: {alert_file}")

    print("=" * 80)

if __name__ == "__main__":
    main()
