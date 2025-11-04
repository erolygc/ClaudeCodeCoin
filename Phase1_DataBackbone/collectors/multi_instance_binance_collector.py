"""
Multi-Instance Binance Data Collector
======================================
550 coins için 5 ayrı WebSocket instance'ı çalıştırır
Her instance 100-150 coin izler (Binance WebSocket limiti)

Kullanım:
    python multi_instance_binance_collector.py --instance 1
    python multi_instance_binance_collector.py --instance 2
    ...vb.
"""

import sys
import os
import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import asyncio
import logging
from binance import AsyncClient, BinanceSocketManager

# Config dosyasını import et
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'config'))
from trading_pairs_1000coins import get_binance_instance_config

# Database setup
DB_FILE = Path(__file__).parent.parent.parent / "data_output" / "binance_data.db"
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logger(instance_id):
    """Instance-specific logger"""
    logger = logging.getLogger(f"BinanceCollector-{instance_id}")
    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(LOG_DIR / f"binance_collector_instance_{instance_id}.log")
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

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
            exchange TEXT DEFAULT 'binance',
            UNIQUE(timestamp, symbol, exchange)
        )
    """)

    # Indexes for better query performance
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

class BinanceMultiCollector:
    """Multi-instance Binance Data Collector"""

    def __init__(self, instance_id, symbols, logger):
        self.instance_id = instance_id
        self.symbols = symbols
        self.logger = logger
        self.client = None
        self.bsm = None
        self.conn = None
        self.message_count = 0
        self.save_count = 0

    async def initialize(self):
        """Initialize Binance client"""
        self.logger.info(f"Initializing Binance Collector Instance {self.instance_id}")
        self.client = await AsyncClient.create()
        self.bsm = BinanceSocketManager(self.client)

        # Database connection
        self.conn = sqlite3.connect(str(DB_FILE))
        self.logger.info(f"Database connection established")

    async def process_message(self, msg):
        """Process incoming kline message"""
        try:
            if msg['e'] == 'error':
                self.logger.error(f"WebSocket error: {msg}")
                return

            if msg['e'] != 'kline':
                return

            self.message_count += 1

            kline = msg['k']

            # Only save closed candles
            if not kline['x']:
                return

            symbol = kline['s']

            # Parse data
            open_time = kline['t']
            datetime_str = datetime.fromtimestamp(open_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
            collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Convert timestamp to seconds (database uses seconds, not milliseconds)
            timestamp_seconds = int(open_time / 1000)

            # Insert into database using OLD schema
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO klines
                (timestamp, datetime, symbol, interval, open, high, low, close, volume,
                 number_of_trades, collected_at, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp_seconds,
                datetime_str,
                symbol,
                "1m",
                float(kline['o']),
                float(kline['h']),
                float(kline['l']),
                float(kline['c']),
                float(kline['v']),
                kline['n'],  # number of trades
                collected_at,
                "binance"
            ))

            self.conn.commit()
            self.save_count += 1

            if self.save_count % 100 == 0:
                self.logger.info(f"Instance {self.instance_id}: Saved {self.save_count} candles (Messages: {self.message_count})")

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def start_streams(self):
        """Start WebSocket streams for all symbols"""
        self.logger.info(f"Starting streams for {len(self.symbols)} symbols")

        # Convert symbols to lowercase for WebSocket
        streams = [f"{symbol.lower()}@kline_1m" for symbol in self.symbols]

        # Create multiplex socket
        ms = self.bsm.multiplex_socket(streams)

        async with ms as stream:
            self.logger.info(f"Instance {self.instance_id}: WebSocket connected - Monitoring {len(self.symbols)} coins")

            while True:
                try:
                    msg = await stream.recv()
                    await self.process_message(msg)

                except Exception as e:
                    self.logger.error(f"Stream error: {e}")
                    await asyncio.sleep(5)  # Wait before retry

    async def run(self):
        """Main run loop"""
        try:
            await self.initialize()

            self.logger.info("="*80)
            self.logger.info(f"🚀 BINANCE COLLECTOR INSTANCE {self.instance_id} STARTED")
            self.logger.info("="*80)
            self.logger.info(f"Monitoring: {len(self.symbols)} coins")
            self.logger.info(f"Top 5: {self.symbols[:5]}")
            self.logger.info("="*80)

            await self.start_streams()

        except KeyboardInterrupt:
            self.logger.info(f"Instance {self.instance_id}: Shutting down...")

        except Exception as e:
            self.logger.error(f"Fatal error: {e}")

        finally:
            if self.conn:
                self.conn.close()
            if self.client:
                await self.client.close_connection()

            self.logger.info(f"Instance {self.instance_id}: Final stats - Messages: {self.message_count}, Saved: {self.save_count}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Multi-Instance Binance Data Collector')
    parser.add_argument('--instance', type=int, required=True, help='Instance ID (1-5)')
    args = parser.parse_args()

    instance_id = args.instance

    # Validate instance ID
    if instance_id < 1 or instance_id > 5:
        print(f"❌ Invalid instance ID: {instance_id}. Must be 1-5")
        return

    # Initialize database (only once, but safe to call multiple times)
    init_database()

    # Get instance config
    config = get_binance_instance_config(instance_id)

    if not config:
        print(f"❌ No configuration found for instance {instance_id}")
        return

    symbols = config['symbols']

    if len(symbols) == 0:
        print(f"⚠️  Instance {instance_id} has no symbols assigned")
        return

    # Setup logger
    logger = setup_logger(instance_id)

    # Create and run collector
    collector = BinanceMultiCollector(instance_id, symbols, logger)
    await collector.run()

if __name__ == "__main__":
    print()
    print("="*80)
    print("🔷 BINANCE MULTI-INSTANCE COLLECTOR")
    print("="*80)
    print()
    print("Starting collector...")
    print()

    asyncio.run(main())
