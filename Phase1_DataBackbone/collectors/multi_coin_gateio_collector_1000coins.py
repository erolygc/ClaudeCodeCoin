"""
Gate.io Data Collector - 1000 Coin System
==========================================
550 Gate.io USDT pairs için tek instance yeterli
Gate.io WebSocket yüksek kapasiteyi destekler

Kullanım:
    python multi_coin_gateio_collector_1000coins.py
"""

import sys
import json
import asyncio
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
import websockets

# Config dosyasını import et
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'config'))
from trading_pairs_1000coins import get_gateio_symbols

# Database setup
DB_FILE = Path(__file__).parent.parent.parent / "data_output" / "binance_data.db"
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "gateio_collector_1000coins.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("GateIOCollector-1000")

def init_database():
    """Initialize database with required tables"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS klines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            symbol TEXT NOT NULL,
            interval TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume REAL NOT NULL,
            number_of_trades INTEGER DEFAULT 0,
            collected_at TEXT NOT NULL,
            exchange TEXT DEFAULT 'gate.io',
            UNIQUE(timestamp, symbol, exchange)
        )
    """)

    # Indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_symbol_datetime
        ON klines(symbol, datetime)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_exchange_datetime
        ON klines(exchange, datetime)
    """)

    conn.commit()
    conn.close()

class GateIOCollector:
    """Gate.io 1000-Coin Data Collector"""

    def __init__(self, symbols):
        self.symbols = symbols
        self.conn = None
        self.message_count = 0
        self.save_count = 0
        self.ws_url = "wss://api.gateio.ws/ws/v4/"

    def initialize_db(self):
        """Initialize database connection"""
        self.conn = sqlite3.connect(str(DB_FILE))
        logger.info("Database connection established")

    def process_message(self, msg):
        """Process incoming kline message"""
        try:
            if msg.get('event') == 'update' and msg.get('channel') == 'spot.candlesticks':
                self.message_count += 1

                result = msg.get('result', {})

                # Extract data
                timestamp = result['t']
                symbol = result['n'].replace('spot.candlesticks.1m.', '')

                # Parse OHLCV - Gate.io format: [timestamp_str, volume_str, close_str, high_str, low_str, open_str, ...]
                ohlcv = result.get('c', [])

                if len(ohlcv) < 6:
                    return  # Skip incomplete data

                # Helper function to safely convert to float
                def safe_float(value, default=0.0):
                    try:
                        if value == '.' or value == '' or value is None:
                            return default
                        return float(value)
                    except (ValueError, TypeError):
                        return default

                # Parse values with safety checks
                open_price = safe_float(ohlcv[5])
                high_price = safe_float(ohlcv[3])
                low_price = safe_float(ohlcv[4])
                close_price = safe_float(ohlcv[2])
                volume = safe_float(ohlcv[1])

                # Skip if all prices are 0
                if open_price == 0 and high_price == 0 and low_price == 0 and close_price == 0:
                    return

                datetime_str = datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
                collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insert into database using OLD schema
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO klines
                    (timestamp, datetime, symbol, interval, open, high, low, close, volume,
                     number_of_trades, collected_at, exchange)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(timestamp),
                    datetime_str,
                    symbol,
                    "1m",
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                    0,  # number_of_trades
                    collected_at,
                    "gate.io"
                ))

                self.conn.commit()
                self.save_count += 1

                if self.save_count % 100 == 0:
                    logger.info(f"Saved {self.save_count} candles (Messages: {self.message_count})")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def subscribe_to_symbols(self, websocket):
        """Subscribe to kline streams for all symbols"""
        subscribe_messages = []

        for symbol in self.symbols:
            subscribe_msg = {
                "time": int(datetime.now().timestamp()),
                "channel": "spot.candlesticks",
                "event": "subscribe",
                "payload": ["1m", symbol]
            }
            subscribe_messages.append(subscribe_msg)

        # Send subscriptions in batches
        batch_size = 50
        for i in range(0, len(subscribe_messages), batch_size):
            batch = subscribe_messages[i:i+batch_size]

            for msg in batch:
                await websocket.send(json.dumps(msg))

            logger.info(f"Subscribed to {len(batch)} symbols (Total: {min(i+batch_size, len(self.symbols))}/{len(self.symbols)})")
            await asyncio.sleep(0.5)  # Small delay between batches

    async def start_websocket(self):
        """Start WebSocket connection"""
        logger.info(f"Connecting to Gate.io WebSocket...")

        async with websockets.connect(self.ws_url) as websocket:
            logger.info(f"Connected! Subscribing to {len(self.symbols)} symbols...")

            await self.subscribe_to_symbols(websocket)

            logger.info("="*80)
            logger.info("🟢 GATE.IO COLLECTOR ACTIVE - Monitoring 550 coins")
            logger.info("="*80)

            # Receive messages
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    self.process_message(data)

                except Exception as e:
                    logger.error(f"WebSocket error: {e}")
                    await asyncio.sleep(5)

    async def run(self):
        """Main run loop"""
        try:
            self.initialize_db()

            logger.info("="*80)
            logger.info("🚀 GATE.IO COLLECTOR STARTED (1000 COIN SYSTEM)")
            logger.info("="*80)
            logger.info(f"Monitoring: {len(self.symbols)} coins")
            logger.info(f"Top 5: {self.symbols[:5]}")
            logger.info("="*80)

            while True:
                try:
                    await self.start_websocket()

                except Exception as e:
                    logger.error(f"Connection error: {e}")
                    logger.info("Reconnecting in 10 seconds...")
                    await asyncio.sleep(10)

        except KeyboardInterrupt:
            logger.info("Shutting down...")

        finally:
            if self.conn:
                self.conn.close()

            logger.info(f"Final stats - Messages: {self.message_count}, Saved: {self.save_count}")

async def main():
    """Main entry point"""
    # Initialize database
    init_database()

    # Get symbols from config
    symbols = get_gateio_symbols()

    logger.info(f"Loaded {len(symbols)} Gate.io symbols from config")

    # Create and run collector
    collector = GateIOCollector(symbols)
    await collector.run()

if __name__ == "__main__":
    print()
    print("="*80)
    print("🔶 GATE.IO COLLECTOR - 1000 COIN SYSTEM")
    print("="*80)
    print()
    print("Starting collector...")
    print()

    asyncio.run(main())
