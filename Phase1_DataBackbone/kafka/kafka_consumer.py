"""
Kafka Consumer Module
Consumes messages from Kafka topics and processes them (e.g., save to database)
"""

import json
import sys
from typing import Callable, List, Optional

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from loguru import logger

sys.path.append(str(__file__ + "/../../.."))

from Phase1_DataBackbone.storage.database import TimescaleDBConnection
from Phase1_DataBackbone.utils import Config


class KlineConsumer:
    """
    Consumes candlestick (kline) data from Kafka and saves to TimescaleDB
    """

    def __init__(
        self,
        topics: List[str],
        group_id: str = "kline-consumer-group",
        auto_offset_reset: str = "latest",
    ):
        """
        Initialize Kafka consumer for kline data

        Args:
            topics: List of Kafka topics to subscribe to
            group_id: Consumer group ID
            auto_offset_reset: Where to start reading ('earliest' or 'latest')
        """
        self.topics = topics
        self.group_id = group_id

        # Configuration
        config = Config()
        kafka_bootstrap = config.get("kafka.bootstrap_servers")

        # Initialize Kafka consumer
        try:
            self.consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=kafka_bootstrap,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
                consumer_timeout_ms=1000,  # Timeout for polling
            )
            logger.info(
                f"✅ Kafka consumer initialized: topics={topics}, group_id={group_id}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            raise

        # Initialize database connection
        self.db = TimescaleDBConnection()

        # Statistics
        self.messages_consumed = 0
        self.messages_saved = 0
        self.errors = 0
        self.is_running = False

    def process_kline_message(self, message_value: dict) -> bool:
        """
        Process and save kline message to database

        Args:
            message_value: Deserialized message from Kafka

        Returns:
            True if successfully saved, False otherwise
        """
        try:
            # Save to database
            success = self.db.insert_kline(message_value)

            if success:
                self.messages_saved += 1
                logger.info(
                    f"💾 Saved: {message_value['symbol']} {message_value['interval']} | "
                    f"C: {message_value['close']} | V: {message_value['volume']}"
                )
            else:
                self.errors += 1
                logger.error(f"Failed to save kline to database: {message_value['symbol']}")

            return success

        except Exception as e:
            self.errors += 1
            logger.error(f"Error processing kline message: {e}")
            return False

    def start(self, message_handler: Optional[Callable] = None):
        """
        Start consuming messages from Kafka

        Args:
            message_handler: Custom message handler function (optional)
                           If not provided, uses default process_kline_message
        """
        logger.info(f"🚀 Starting Kafka consumer for topics: {self.topics}")
        self.is_running = True

        handler = message_handler or self.process_kline_message

        try:
            for message in self.consumer:
                if not self.is_running:
                    break

                self.messages_consumed += 1

                logger.debug(
                    f"📥 Consumed from {message.topic} "
                    f"[partition: {message.partition}, offset: {message.offset}]"
                )

                # Process message
                handler(message.value)

                # Log statistics every 100 messages
                if self.messages_consumed % 100 == 0:
                    self._print_statistics()

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
            self.stop()
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
            self.stop()
        except Exception as e:
            logger.error(f"Unexpected error in consumer loop: {e}")
            self.stop()

    def stop(self):
        """Stop the consumer and clean up resources"""
        logger.info("Stopping Kafka consumer...")
        self.is_running = False

        if self.consumer:
            self.consumer.close()

        # Print final statistics
        self._print_statistics()

        logger.info("✅ Consumer stopped gracefully")

    def _print_statistics(self):
        """Print consumption statistics"""
        success_rate = (
            (self.messages_saved / self.messages_consumed * 100)
            if self.messages_consumed > 0
            else 0
        )

        logger.info(
            f"📊 Stats: Consumed={self.messages_consumed}, "
            f"Saved={self.messages_saved}, "
            f"Errors={self.errors}, "
            f"Success Rate={success_rate:.2f}%"
        )


def main():
    """Main entry point"""
    from Phase1_DataBackbone.utils import setup_logger

    # Setup logger
    config = Config()
    log_level = config.get("logging.level", "INFO")
    log_file = config.get("logging.file", "logs/kafka_consumer.log")
    setup_logger(log_level=log_level, log_file=log_file)

    # Get configuration
    topics = [config.get("kafka.topics.raw_klines", "raw.klines.1m")]

    logger.info("=" * 70)
    logger.info("🚀 ClaudeCodeCoin - Kafka Kline Consumer")
    logger.info("=" * 70)
    logger.info(f"Topics: {topics}")
    logger.info("=" * 70)

    # Create and start consumer
    consumer = KlineConsumer(topics=topics)

    try:
        consumer.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    finally:
        consumer.stop()


if __name__ == "__main__":
    main()
