"""
Create test database with sample data for testing
"""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Create data_output directory
output_dir = Path("data_output")
output_dir.mkdir(exist_ok=True)

db_path = output_dir / "binance_data.db"

print("Creating test database...")

# Create database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS klines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        exchange TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        datetime TEXT NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume REAL NOT NULL,
        UNIQUE(symbol, exchange, timestamp)
    )
""")

# Generate sample data for BTC_USDT
print("Generating sample data for BTC_USDT...")

base_time = datetime.now() - timedelta(days=7)  # Last 7 days
base_price = 67000.0

data = []
for i in range(10000):  # 10000 1-minute bars (about 1 week)
    timestamp = int((base_time + timedelta(minutes=i)).timestamp() * 1000)
    dt = (base_time + timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S')

    # Random walk price
    price_change = np.random.randn() * 100
    base_price += price_change

    open_price = base_price
    high_price = base_price + abs(np.random.randn() * 50)
    low_price = base_price - abs(np.random.randn() * 50)
    close_price = base_price + np.random.randn() * 50
    volume = np.random.uniform(1000000, 5000000)

    data.append((
        'BTC_USDT', 'gate.io', timestamp, dt,
        open_price, high_price, low_price, close_price, volume
    ))

# Insert data
cursor.executemany("""
    INSERT OR IGNORE INTO klines (symbol, exchange, timestamp, datetime, open, high, low, close, volume)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", data)

# Generate sample data for ETH_USDT
print("Generating sample data for ETH_USDT...")

base_price = 3500.0
data = []
for i in range(10000):
    timestamp = int((base_time + timedelta(minutes=i)).timestamp() * 1000)
    dt = (base_time + timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S')

    price_change = np.random.randn() * 10
    base_price += price_change

    open_price = base_price
    high_price = base_price + abs(np.random.randn() * 5)
    low_price = base_price - abs(np.random.randn() * 5)
    close_price = base_price + np.random.randn() * 5
    volume = np.random.uniform(500000, 2000000)

    data.append((
        'ETH_USDT', 'gate.io', timestamp, dt,
        open_price, high_price, low_price, close_price, volume
    ))

cursor.executemany("""
    INSERT OR IGNORE INTO klines (symbol, exchange, timestamp, datetime, open, high, low, close, volume)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", data)

# Generate sample data for SOL_USDT
print("Generating sample data for SOL_USDT...")

base_price = 145.0
data = []
for i in range(10000):
    timestamp = int((base_time + timedelta(minutes=i)).timestamp() * 1000)
    dt = (base_time + timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S')

    price_change = np.random.randn() * 2
    base_price += price_change

    open_price = base_price
    high_price = base_price + abs(np.random.randn() * 1)
    low_price = base_price - abs(np.random.randn() * 1)
    close_price = base_price + np.random.randn() * 1
    volume = np.random.uniform(200000, 1000000)

    data.append((
        'SOL_USDT', 'gate.io', timestamp, dt,
        open_price, high_price, low_price, close_price, volume
    ))

cursor.executemany("""
    INSERT OR IGNORE INTO klines (symbol, exchange, timestamp, datetime, open, high, low, close, volume)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", data)

conn.commit()

# Verify
cursor.execute("SELECT symbol, COUNT(*) FROM klines GROUP BY symbol")
results = cursor.fetchall()

print("\n✅ Test database created successfully!")
print(f"📁 Location: {db_path.absolute()}")
print("\n📊 Data summary:")
for symbol, count in results:
    print(f"   {symbol}: {count} bars")

conn.close()

print("\n✨ Ready to test!")
