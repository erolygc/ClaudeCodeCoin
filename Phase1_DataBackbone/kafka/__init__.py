"""
Kafka module for ClaudeCodeCoin
Handles message brokering between data collectors and processors
"""

from .kafka_producer import CustomKafkaProducer

__all__ = ["CustomKafkaProducer"]
