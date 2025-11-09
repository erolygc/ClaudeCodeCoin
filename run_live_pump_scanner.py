"""
Live Pump Scanner
Sürekli çalışan pump detection sistemi
"""
import sys
from pathlib import Path

# Proje kök dizinini ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import time
import logging
from datetime import datetime
from Phase6_PumpDetection.pump_detection_engine import PumpDetectionEngine

# Logs klasörünü oluştur
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'live_pump_scanner.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    print()
    print("=" * 80)
    print("LIVE PUMP SCANNER")
    print("=" * 80)
    print()
    print("Continuous pump detection from live Gate.io data")
    print("Scan interval: 60 seconds")
    print("Alert output: pump_alerts/")
    print()
    print("=" * 80)
    print()

    # Pump scanner'ı başlat
    scanner = PumpDetectionEngine(db_path="data_output/binance_data.db")

    # Gate.io symbols - ilk 20 coin ile başla (test için)
    # Production'da tüm coinler taranır
    test_symbols = [
        "BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "ADA_USDT",
        "DOGE_USDT", "MATIC_USDT", "DOT_USDT", "AVAX_USDT", "TRX_USDT",
        "LINK_USDT", "ATOM_USDT", "LTC_USDT", "UNI_USDT", "ETC_USDT",
        "SHIB_USDT", "PEPE_USDT", "FLOKI_USDT", "BONK_USDT", "WIF_USDT"
    ]

    logger.info(f"[SCANNER] Monitoring {len(test_symbols)} coins")
    logger.info(f"[SCANNER] Symbols: {', '.join(test_symbols[:5])}...")
    logger.info("")

    scan_count = 0

    try:
        while True:
            scan_count += 1
            logger.info(f"[SCAN #{scan_count}] {datetime.now().strftime('%H:%M:%S')}")

            all_signals = []

            # Her coin için analiz yap
            for symbol in test_symbols:
                signals = scanner.analyze_symbol(symbol, exchange="gate.io")

                if signals:
                    all_signals.extend(signals)
                    for signal in signals:
                        logger.info(f"  [PUMP DETECTED] {signal.symbol} - {signal.level} ({signal.confidence:.0f}%)")
                        logger.info(f"    Price: {signal.price_change_pct:+.1f}%, Volume: {signal.volume_change_pct:.0f}%")

            if all_signals:
                logger.info(f"[SCAN #{scan_count}] Found {len(all_signals)} pump signals")
                # Scanner otomatik olarak pump_alerts/ klasörüne kaydeder
            else:
                logger.info(f"[SCAN #{scan_count}] No pumps detected")

            logger.info("")

            # 60 saniye bekle
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 80)
        logger.info("PUMP SCANNER STOPPED")
        logger.info("=" * 80)
        logger.info(f"Total scans: {scan_count}")
        logger.info("")

if __name__ == "__main__":
    main()
