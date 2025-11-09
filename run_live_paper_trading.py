"""
Live Paper Trading Engine
Gerçek veri ile sanal trading
"""
import sys
from pathlib import Path

# Proje kök dizinini ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from Phase7_PaperTrading.paper_trading_engine import PaperTradingEngine
from Phase7_PaperTrading import config

# Logs klasörünü oluştur
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'live_paper_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    print()
    print("=" * 80)
    print("LIVE PAPER TRADING ENGINE")
    print("=" * 80)
    print()
    print("Real-time trading with virtual money")
    print("Data source: Live Gate.io WebSocket")
    print("Signals: pump_alerts/ (from pump scanner)")
    print()
    print("=" * 80)
    print()

    # TEST MODE - Daha fazla sinyal görmek için
    config.MIN_CONFIDENCE_TO_TRADE = 70.0  # %70+ confidence
    config.MIN_VOLUME_SPIKE = 100.0  # TEST: %100+ volume spike (daha fazla sinyal)

    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST MODE - LIVE TRADING (More Signals)")
    logger.info("=" * 70)
    logger.info(f"Min Confidence: {config.MIN_CONFIDENCE_TO_TRADE}%")
    logger.info(f"Min Volume Spike: {config.MIN_VOLUME_SPIKE}%")
    logger.info(f"Stop Loss: {config.STOP_LOSS_PERCENT}%")
    logger.info(f"Take Profit: {config.TAKE_PROFIT_PERCENT}")
    logger.info("=" * 70)
    logger.info("")

    # Engine'i başlat
    engine = PaperTradingEngine()

    # Ana döngüyü başlat (her 30 saniyede bir kontrol)
    engine.run(interval_seconds=30)

if __name__ == "__main__":
    main()
