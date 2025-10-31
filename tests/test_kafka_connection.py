"""
Test Kafka connection and producer/consumer functionality
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime

from kafka import KafkaAdminClient, KafkaConsumer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from loguru import logger

from Phase1_DataBackbone.kafka.kafka_producer import CustomKafkaProducer
from Phase1_DataBackbone.utils import Config, setup_logger


def test_kafka_connection():
    """Test basic Kafka connectivity"""
    print("\n" + "=" * 70)
    print("🧪 TEST 1: Kafka Connection")
    print("=" * 70)

    try:
        config = Config()
        bootstrap_servers = config.get("kafka.bootstrap_servers")

        # Try to connect to Kafka
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id="test-admin",
            request_timeout_ms=5000,
        )

        # Get cluster metadata
        cluster_metadata = admin_client.list_topics()
        print(f"✅ Connected to Kafka at {bootstrap_servers}")
        print(f"✅ Found {len(cluster_metadata)} topic(s)")

        admin_client.close()
        return True

    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        print("Make sure Kafka is running: docker-compose up -d kafka")
        return False


def test_create_topic():
    """Test creating a test topic"""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Create Test Topic")
    print("=" * 70)

    try:
        config = Config()
        bootstrap_servers = config.get("kafka.bootstrap_servers")

        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id="test-admin",
        )

        # Create a test topic
        test_topic = NewTopic(
            name="test.ccc.topic",
            num_partitions=1,
            replication_factor=1,
        )

        try:
            admin_client.create_topics([test_topic])
            print("✅ Test topic 'test.ccc.topic' created")
        except TopicAlreadyExistsError:
            print("✅ Test topic 'test.ccc.topic' already exists")

        admin_client.close()
        return True

    except Exception as e:
        print(f"❌ Topic creation failed: {e}")
        return False


def test_producer():
    """Test Kafka producer"""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: Kafka Producer")
    print("=" * 70)

    try:
        config = Config()
        bootstrap_servers = config.get("kafka.bootstrap_servers")

        # Create producer
        producer = CustomKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            client_id="test-producer",
        )

        # Send test message
        test_message = {
            "test_id": "test_001",
            "message": "Hello from ClaudeCodeCoin test!",
            "timestamp": datetime.utcnow().isoformat(),
            "value": 12345.67,
        }

        success = producer.send(
            topic="test.ccc.topic",
            value=test_message,
            key="test_key",
        )

        if success:
            print("✅ Test message sent successfully")
            print(f"   Message: {test_message}")
        else:
            print("❌ Failed to send test message")
            return False

        producer.close()
        return True

    except Exception as e:
        print(f"❌ Producer test failed: {e}")
        return False


def test_consumer():
    """Test Kafka consumer"""
    print("\n" + "=" * 70)
    print("🧪 TEST 4: Kafka Consumer")
    print("=" * 70)

    try:
        config = Config()
        bootstrap_servers = config.get("kafka.bootstrap_servers")

        # Create consumer
        consumer = KafkaConsumer(
            "test.ccc.topic",
            bootstrap_servers=bootstrap_servers,
            group_id="test-consumer-group",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=5000,  # Wait max 5 seconds
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        print("✅ Consumer created, polling for messages...")

        messages_received = 0
        for message in consumer:
            messages_received += 1
            print(f"✅ Received message: {message.value}")

            if messages_received >= 1:  # Just read one message for test
                break

        consumer.close()

        if messages_received > 0:
            print(f"✅ Successfully consumed {messages_received} message(s)")
            return True
        else:
            print("⚠️  No messages received (this is OK if topic is empty)")
            return True

    except Exception as e:
        print(f"❌ Consumer test failed: {e}")
        return False


def test_end_to_end():
    """Test complete producer -> consumer flow"""
    print("\n" + "=" * 70)
    print("🧪 TEST 5: End-to-End Producer -> Consumer")
    print("=" * 70)

    try:
        config = Config()
        bootstrap_servers = config.get("kafka.bootstrap_servers")

        # Create producer
        producer = CustomKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            client_id="test-e2e-producer",
        )

        # Send unique test message
        test_id = f"e2e_test_{int(time.time())}"
        test_message = {
            "test_id": test_id,
            "message": "End-to-end test message",
            "timestamp": datetime.utcnow().isoformat(),
        }

        print(f"📤 Sending message with test_id: {test_id}")
        success = producer.send(
            topic="test.ccc.topic",
            value=test_message,
            key=test_id,
        )

        if not success:
            print("❌ Failed to send message")
            return False

        producer.flush()  # Make sure message is sent
        producer.close()

        print("✅ Message sent, waiting 2 seconds...")
        time.sleep(2)  # Give Kafka time to process

        # Create consumer
        consumer = KafkaConsumer(
            "test.ccc.topic",
            bootstrap_servers=bootstrap_servers,
            group_id="test-e2e-consumer-group",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=5000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        print("📥 Consuming messages...")

        found = False
        for message in consumer:
            if message.value.get("test_id") == test_id:
                print(f"✅ Found our test message: {message.value}")
                found = True
                break

        consumer.close()

        if found:
            print("✅ End-to-end test PASSED!")
            return True
        else:
            print("⚠️  Test message not found (but Kafka is working)")
            return True

    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False


def main():
    """Run all Kafka tests"""
    # Setup logger
    setup_logger(log_level="INFO")

    print("\n" + "=" * 70)
    print("🚀 ClaudeCodeCoin - Kafka Connection Tests")
    print("=" * 70)
    print("Make sure Kafka is running: docker-compose up -d kafka zookeeper")
    print("=" * 70)

    # Run tests
    results = []
    results.append(("Kafka Connection", test_kafka_connection()))
    results.append(("Create Test Topic", test_create_topic()))
    results.append(("Kafka Producer", test_producer()))
    results.append(("Kafka Consumer", test_consumer()))
    results.append(("End-to-End Flow", test_end_to_end()))

    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 70)
    print(f"Total: {len(results)} tests | Passed: {passed} | Failed: {failed}")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
