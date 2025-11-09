"""
PRODUCTION MODE - Live Paper Trading
====================================
Gerçek Gate.io verisi ile sanal para trading
Sıkı filtreler: 70% confidence, 800% volume spike
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Phase7_PaperTrading"))

# Import after path setup
from Phase7_PaperTrading.paper_trading_engine import PaperTradingEngine
import Phase7_PaperTrading.config as config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production_paper_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function"""
    print()
    print("="*80)
    print("PRODUCTION MODE - LIVE PAPER TRADING")
    print("="*80)
    print()
    print("Real-time trading with STRICT filters")
    print("Data source: Live Gate.io WebSocket (REAL DATA)")
    print("Trading: Virtual money only (SAFE)")
    print()
    print("="*80)
    print()

    # PRODUCTION MODE - Sıkı filtreler
    config.MIN_CONFIDENCE_TO_TRADE = 70.0  # Sadece yüksek güvenilirlik
    config.MIN_VOLUME_SPIKE = 800.0  # Gerçek pump'lar (8x hacim)
    config.STOP_LOSS_PERCENT = 5.0
    config.TAKE_PROFIT_PERCENT = {
        'CRITICAL': 25.0,
        'HIGH': 20.0,
        'MEDIUM': 15.0,
        'LOW': 10.0
    }

    logger.info("")
    logger.info("======================================================================")
    logger.info("PRODUCTION MODE - LIVE TRADING (Strict Filters)")
    logger.info("======================================================================")
    logger.info(f"Min Confidence: {config.MIN_CONFIDENCE_TO_TRADE}%")
    logger.info(f"Min Volume Spike: {config.MIN_VOLUME_SPIKE}%")
    logger.info(f"Stop Loss: {config.STOP_LOSS_PERCENT}%")
    logger.info(f"Take Profit: {config.TAKE_PROFIT_PERCENT}")
    logger.info("======================================================================")
    logger.info("")

    # Start paper trading engine
    engine = PaperTradingEngine()

    # Run with 30 second intervals
    engine.run(interval_seconds=30)

if __name__ == "__main__":
    main()
