"""
Kafka Producer Module
Handles sending data to Kafka topics with proper serialization and error handling
"""

import json
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger


class CustomKafkaProducer:
    """
    Wrapper around KafkaProducer with custom error handling and serialization
    """

    def __init__(
        self,
        bootstrap_servers: str,
        client_id: str = "ccc-producer",
        acks: str = "all",
        retries: int = 3,
        compression_type: str = "gzip",
    ):
        """
        Initialize Kafka Producer

        Args:
            bootstrap_servers: Kafka broker address(es)
            client_id: Client identifier
            acks: Acknowledgment policy ('all', '0', '1')
            retries: Number of retry attempts
            compression_type: Compression algorithm ('gzip', 'snappy', 'lz4', None)
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                client_id=client_id,
                acks=acks,
                retries=retries,
                compression_type=compression_type,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            logger.info(
                f"Kafka Producer initialized: {bootstrap_servers}, client_id={client_id}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka Producer: {e}")
            raise

    def send(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        partition: Optional[int] = None,
    ) -> bool:
        """
        Send message to Kafka topic

        Args:
            topic: Kafka topic name
            value: Message payload (will be JSON serialized)
            key: Message key (optional, used for partitioning)
            partition: Specific partition to send to (optional)

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            future = self.producer.send(
                topic=topic,
                value=value,
                key=key,
                partition=partition,
            )

            # Wait for confirmation (blocking with timeout)
            record_metadata = future.get(timeout=10)

            logger.debug(
                f"Message sent to {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            return True

        except KafkaError as e:
            logger.error(f"Kafka error while sending message to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending message to {topic}: {e}")
            return False

    def send_async(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        callback: Optional[callable] = None,
    ):
        """
        Send message asynchronously without waiting for confirmation

        Args:
            topic: Kafka topic name
            value: Message payload
            key: Message key (optional)
            callback: Callback function to handle success/error
        """
        try:
            future = self.producer.send(topic=topic, value=value, key=key)

            if callback:
                future.add_callback(callback)
            else:
                # Default callback
                future.add_callback(self._on_send_success)
                future.add_errback(self._on_send_error)

        except Exception as e:
            logger.error(f"Error sending async message to {topic}: {e}")

    def _on_send_success(self, record_metadata):
        """Default success callback"""
        logger.debug(
            f"Message delivered to {record_metadata.topic} "
            f"[{record_metadata.partition}] @ offset {record_metadata.offset}"
        )

    def _on_send_error(self, exception):
        """Default error callback"""
        logger.error(f"Message delivery failed: {exception}")

    def flush(self, timeout: Optional[float] = None):
        """
        Flush all buffered messages

        Args:
            timeout: Maximum time to wait (seconds)
        """
        try:
            self.producer.flush(timeout=timeout)
            logger.debug("Kafka producer flushed")
        except Exception as e:
            logger.error(f"Error flushing Kafka producer: {e}")

    def close(self, timeout: Optional[float] = None):
        """
        Close the producer and flush remaining messages

        Args:
            timeout: Maximum time to wait for pending messages (seconds)
        """
        try:
            self.producer.close(timeout=timeout)
            logger.info("Kafka producer closed")
        except Exception as e:
            logger.error(f"Error closing Kafka producer: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
