"""
Live Gate.io Data Collector
Gerçek zamanlı veri toplar - 550 coin için
"""
import sys
from pathlib import Path

# Proje kök dizinini ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Phase1_DataBackbone.collectors.multi_coin_gateio_collector_1000coins import main
import asyncio

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("LIVE GATE.IO DATA COLLECTOR")
    print("=" * 80)
    print()
    print("Real-time data collection for 550 coins")
    print("WebSocket: wss://api.gateio.ws/ws/v4/")
    print("Interval: 1 minute candles")
    print("Database: data_output/binance_data.db")
    print()
    print("=" * 80)
    print()
    print("Press Ctrl+C to stop...")
    print()

    asyncio.run(main())
