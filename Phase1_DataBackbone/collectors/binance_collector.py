"""
Binance WebSocket Data Collector
Collects real-time OHLCV (candlestick) data from Binance and sends to Kafka
"""

import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import websocket
from loguru import logger

# Add parent directory to path for imports
sys.path.append(str(__file__ + "/../../.."))

from Phase1_DataBackbone.kafka.kafka_producer import CustomKafkaProducer
from Phase1_DataBackbone.utils import Config, setup_logger


class BinanceKlineCollector:
    """
    Collects real-time candlestick (kline) data from Binance WebSocket API
    """

    def __init__(
        self,
        symbols: List[str],
        interval: str = "1m",
        kafka_topic: str = "raw.klines.1m",
        testnet: bool = False,
    ):
        """
        Initialize Binance Kline Collector

        Args:
            symbols: List of trading pairs (e.g., ['BTCUSDT', 'ETHUSDT'])
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            kafka_topic: Kafka topic to send data to
            testnet: Use Binance testnet if True
        """
        self.symbols = [s.lower().replace("/", "") for s in symbols]
        self.interval = interval
        self.kafka_topic = kafka_topic
        self.testnet = testnet

        # Configuration
        self.config = Config()
        kafka_bootstrap = self.config.get("kafka.bootstrap_servers")

        # Initialize Kafka producer
        try:
            self.kafka_producer = CustomKafkaProducer(
                bootstrap_servers=kafka_bootstrap,
                client_id=f"binance-collector-{interval}",
            )
            logger.info(f"Kafka producer initialized for topic: {kafka_topic}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise

        # WebSocket connection
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_running = False

        # Build WebSocket URL
        self.ws_url = self._build_ws_url()

        # Statistics
        self.messages_received = 0
        self.messages_sent = 0
        self.errors = 0
        self.start_time = None

    def _build_ws_url(self) -> str:
        """Build Binance WebSocket URL for multiple symbols"""
        if self.testnet:
            base_url = "wss://testnet.binance.vision/stream"
        else:
            base_url = "wss://stream.binance.com:9443/stream"

        # Build streams for all symbols
        # Format: btcusdt@kline_1m/ethusdt@kline_1m/...
        streams = [f"{symbol}@kline_{self.interval}" for symbol in self.symbols]
        streams_param = "/".join(streams)

        url = f"{base_url}?streams={streams_param}"
        logger.info(f"WebSocket URL: {url}")
        return url

    def _on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            self.messages_received += 1
            data = json.loads(message)

            # Binance multi-stream format: {"stream": "btcusdt@kline_1m", "data": {...}}
            if "data" in data:
                kline_data = data["data"]
                stream_name = data["stream"]
                symbol = stream_name.split("@")[0].upper()

                # Extract kline information
                k = kline_data["k"]

                # Prepare message for Kafka
                kafka_message = {
                    "exchange": "binance",
                    "symbol": symbol,
                    "interval": k["i"],
                    "timestamp": k["t"],  # Kline start time
                    "open_time": datetime.fromtimestamp(k["t"] / 1000).isoformat(),
                    "close_time": datetime.fromtimestamp(k["T"] / 1000).isoformat(),
                    "open": float(k["o"]),
                    "high": float(k["h"]),
                    "low": float(k["l"]),
                    "close": float(k["c"]),
                    "volume": float(k["v"]),
                    "close_volume": float(k["q"]),  # Quote asset volume
                    "number_of_trades": k["n"],
                    "is_closed": k["x"],  # Is this kline closed?
                    "taker_buy_base_volume": float(k["V"]),
                    "taker_buy_quote_volume": float(k["Q"]),
                    "collected_at": datetime.utcnow().isoformat(),
                }

                # Send to Kafka (only send closed candles to reduce noise)
                if k["x"]:  # Kline is closed
                    success = self.kafka_producer.send(
                        topic=self.kafka_topic,
                        value=kafka_message,
                        key=symbol,
                    )

                    if success:
                        self.messages_sent += 1
                        logger.info(
                            f"📊 {symbol} {self.interval} | "
                            f"O: {k['o']} H: {k['h']} L: {k['l']} C: {k['c']} | "
                            f"V: {k['v']} | Sent to Kafka"
                        )
                    else:
                        self.errors += 1
                        logger.error(f"Failed to send message to Kafka: {symbol}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            self.errors += 1
        except KeyError as e:
            logger.error(f"Missing key in message: {e}")
            self.errors += 1
        except Exception as e:
            logger.error(f"Unexpected error processing message: {e}")
            self.errors += 1

    def _on_error(self, ws, error):
        """Handle WebSocket error"""
        logger.error(f"WebSocket error: {error}")
        self.errors += 1

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        logger.warning(
            f"WebSocket connection closed: code={close_status_code}, msg={close_msg}"
        )
        self.is_running = False

    def _on_open(self, ws):
        """Handle WebSocket open"""
        logger.info(f"🚀 WebSocket connection opened for {len(self.symbols)} symbols")
        logger.info(f"Collecting {self.interval} klines for: {', '.join(self.symbols)}")
        self.is_running = True
        self.start_time = time.time()

    def start(self):
        """Start the WebSocket connection and data collection"""
        logger.info("Starting Binance Kline Collector...")

        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open,
            )

            # Run forever with auto-reconnect
            self.ws.run_forever(
                ping_interval=20,  # Send ping every 20 seconds
                ping_timeout=10,  # Wait 10 seconds for pong
            )

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
            self.stop()
        except Exception as e:
            logger.error(f"Fatal error in WebSocket connection: {e}")
            self.stop()

    def stop(self):
        """Stop the collector and clean up resources"""
        logger.info("Stopping Binance Kline Collector...")
        self.is_running = False

        if self.ws:
            self.ws.close()

        # Close Kafka producer
        self.kafka_producer.close()

        # Print statistics
        if self.start_time:
            duration = time.time() - self.start_time
            logger.info(f"📊 Collection Statistics:")
            logger.info(f"  Duration: {duration:.2f} seconds")
            logger.info(f"  Messages received: {self.messages_received}")
            logger.info(f"  Messages sent to Kafka: {self.messages_sent}")
            logger.info(f"  Errors: {self.errors}")
            if self.messages_sent > 0:
                logger.info(
                    f"  Success rate: {(self.messages_sent / self.messages_received * 100):.2f}%"
                )

        logger.info("✅ Collector stopped gracefully")


def main():
    """Main entry point"""
    # Setup logger
    config = Config()
    log_level = config.get("logging.level", "INFO")
    log_file = config.get("logging.file", "logs/binance_collector.log")
    setup_logger(log_level=log_level, log_file=log_file)

    # Get configuration
    symbols = config.get("data_collection.symbols", ["BTC/USDT", "ETH/USDT"])
    interval = "1m"  # Start with 1 minute candles
    kafka_topic = config.get("kafka.topics.raw_klines", "raw.klines.1m")
    testnet = config.get_secret("binance_testnet", True)

    logger.info("=" * 70)
    logger.info("🚀 ClaudeCodeCoin - Binance Kline Collector")
    logger.info("=" * 70)
    logger.info(f"Symbols: {symbols}")
    logger.info(f"Interval: {interval}")
    logger.info(f"Kafka Topic: {kafka_topic}")
    logger.info(f"Testnet: {testnet}")
    logger.info("=" * 70)

    # Create and start collector
    collector = BinanceKlineCollector(
        symbols=symbols,
        interval=interval,
        kafka_topic=kafka_topic,
        testnet=testnet,
    )

    try:
        collector.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    finally:
        collector.stop()


if __name__ == "__main__":
    main()
