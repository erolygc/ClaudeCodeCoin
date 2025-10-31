"""
Test database connection and basic operations
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime

from loguru import logger

from Phase1_DataBackbone.storage.database import TimescaleDBConnection
from Phase1_DataBackbone.utils import Config, setup_logger


def test_database_connection():
    """Test basic database connectivity"""
    print("\n" + "=" * 70)
    print("🧪 TEST 1: Database Connection")
    print("=" * 70)

    try:
        db = TimescaleDBConnection()
        print("✅ Database connection initialized")

        # Test simple query
        result = db.execute_query("SELECT version();")
        print(f"✅ PostgreSQL version: {result[0][0][:50]}...")

        # Test TimescaleDB
        result = db.execute_query("SELECT extversion FROM pg_extension WHERE extname='timescaledb';")
        if result:
            print(f"✅ TimescaleDB version: {result[0][0]}")
        else:
            print("⚠️  TimescaleDB extension not found")

        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_table_existence():
    """Test if tables exist"""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Table Existence")
    print("=" * 70)

    try:
        db = TimescaleDBConnection()

        tables_to_check = [
            "raw_klines",
            "raw_orderbook",
            "raw_trades",
            "funding_rates",
            "open_interest",
            "indicators",
            "signals",
            "orders",
            "positions",
        ]

        all_exist = True
        for table_name in tables_to_check:
            result = db.execute_query(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name);",
                {"table_name": table_name},
            )
            exists = result[0][0]

            if exists:
                print(f"✅ Table '{table_name}' exists")
            else:
                print(f"❌ Table '{table_name}' does NOT exist")
                all_exist = False

        return all_exist

    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False


def test_insert_sample_data():
    """Test inserting sample kline data"""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: Insert Sample Data")
    print("=" * 70)

    try:
        db = TimescaleDBConnection()

        # Sample kline data
        sample_data = {
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
            "exchange": "binance",
            "symbol": "BTCUSDT",
            "interval": "1m",
            "open": 50000.0,
            "high": 50100.0,
            "low": 49900.0,
            "close": 50050.0,
            "volume": 123.45,
            "close_volume": 6172500.0,
            "number_of_trades": 1500,
            "taker_buy_base_volume": 61.0,
            "taker_buy_quote_volume": 3050000.0,
            "open_time": datetime.utcnow().isoformat(),
            "collected_at": datetime.utcnow().isoformat(),
        }

        success = db.insert_kline(sample_data)

        if success:
            print("✅ Sample data inserted successfully")

            # Verify insertion
            result = db.execute_query(
                "SELECT COUNT(*) FROM raw_klines WHERE symbol = 'BTCUSDT';"
            )
            count = result[0][0]
            print(f"✅ Found {count} record(s) for BTCUSDT")

            return True
        else:
            print("❌ Failed to insert sample data")
            return False

    except Exception as e:
        print(f"❌ Insert test failed: {e}")
        return False


def test_query_data():
    """Test querying data"""
    print("\n" + "=" * 70)
    print("🧪 TEST 4: Query Data")
    print("=" * 70)

    try:
        db = TimescaleDBConnection()

        # Get latest klines
        klines = db.get_latest_klines(
            exchange="binance", symbol="BTCUSDT", interval="1m", limit=5
        )

        if klines:
            print(f"✅ Retrieved {len(klines)} kline(s)")
            for i, kline in enumerate(klines[:3], 1):
                print(f"   {i}. Time: {kline['time']}, Close: {kline['close']}, Volume: {kline['volume']}")
            return True
        else:
            print("⚠️  No data found (this is OK if database is empty)")
            return True

    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False


def main():
    """Run all database tests"""
    # Setup logger
    setup_logger(log_level="INFO")

    print("\n" + "=" * 70)
    print("🚀 ClaudeCodeCoin - Database Connection Tests")
    print("=" * 70)
    print("Make sure TimescaleDB is running: docker-compose up -d timescaledb")
    print("And schema is loaded: psql -f Phase1_DataBackbone/storage/timescaledb_schema.sql")
    print("=" * 70)

    # Run tests
    results = []
    results.append(("Database Connection", test_database_connection()))
    results.append(("Table Existence", test_table_existence()))
    results.append(("Insert Sample Data", test_insert_sample_data()))
    results.append(("Query Data", test_query_data()))

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
