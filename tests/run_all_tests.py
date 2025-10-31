#!/usr/bin/env python
"""
Master test script - runs all Phase 1 tests
"""

import subprocess
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print_header(f"Running: {description}")

    script_path = project_root / "tests" / script_name

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(project_root),
            capture_output=False,
            text=True,
        )

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Failed to run test: {e}")
        return False


def check_docker_services():
    """Check if Docker services are running"""
    print_header("Checking Docker Services")

    try:
        result = subprocess.run(
            ["docker-compose", "ps"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(result.stdout)
            print("✅ Docker Compose is accessible")
            return True
        else:
            print("❌ Docker Compose check failed")
            print(result.stderr)
            return False

    except FileNotFoundError:
        print("❌ Docker Compose not found. Please install Docker.")
        return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🚀 ClaudeCodeCoin - Complete Phase 1 Test Suite")
    print("=" * 70)
    print("This script will run all Phase 1 POC tests")
    print("=" * 70)

    # Check Docker first
    docker_ok = check_docker_services()

    if not docker_ok:
        print("\n⚠️  Docker services check failed!")
        print("Please make sure Docker is running:")
        print("  docker-compose up -d")
        print("\nContinuing with tests anyway...\n")

    # Wait a bit for services to be ready
    time.sleep(2)

    # Run tests
    test_results = {}

    # Test 1: Database
    test_results["Database Tests"] = run_test_script(
        "test_database_connection.py",
        "Database Connection Tests"
    )

    time.sleep(1)

    # Test 2: Kafka
    test_results["Kafka Tests"] = run_test_script(
        "test_kafka_connection.py",
        "Kafka Connection Tests"
    )

    # Print final summary
    print_header("FINAL TEST SUMMARY")

    passed = sum(1 for result in test_results.values() if result)
    failed = sum(1 for result in test_results.values() if not result)

    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print("\n" + "=" * 70)
    print(f"Total Test Suites: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Phase 1 POC is working correctly!")
        print("\nNext steps:")
        print("1. Start Binance collector: python Phase1_DataBackbone/collectors/binance_collector.py")
        print("2. Start Kafka consumer: python Phase1_DataBackbone/kafka/kafka_consumer.py")
        print("3. Check Kafka UI: http://localhost:8080")
        print("4. Check Grafana: http://localhost:3000")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("Please check the logs above for details.")
        print("\nCommon issues:")
        print("- Make sure Docker services are running: docker-compose up -d")
        print("- Check logs: docker-compose logs <service-name>")
        print("- Load database schema: docker exec -i ccc-timescaledb psql -U ccc_user -d ccc_trading < Phase1_DataBackbone/storage/timescaledb_schema.sql")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
