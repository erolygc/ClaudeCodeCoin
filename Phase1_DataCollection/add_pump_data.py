"""
Add artificial pump patterns to test database
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

db_path = Path("data_output/binance_data.db")

print("Adding pump data to database...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the last 10 bars for BTC_USDT
cursor.execute("""
    SELECT timestamp, datetime, open, high, low, close, volume
    FROM klines
    WHERE symbol = 'BTC_USDT' AND exchange = 'gate.io'
    ORDER BY timestamp DESC
    LIMIT 10
""")
rows = cursor.fetchall()

print(f"\n🔍 Original last 10 bars for BTC_USDT:")
for i, row in enumerate(reversed(rows)):
    print(f"   {i+1}. {row[1]} - Close: ${row[5]:.2f}, Volume: {row[6]:.0f}")

# Modify the last 5 bars to create a pump pattern
# Increase price by 15% and volume by 5x
print(f"\n💉 Injecting pump pattern (last 5 bars: +15% price, 5x volume)...")

for i in range(5):
    row = rows[i]  # Last 5 bars (already in reverse order)
    timestamp, dt, open_p, high_p, low_p, close_p, volume = row

    # Pump: 15% price increase, 5x volume
    pump_multiplier = 1.15
    volume_multiplier = 5.0

    new_open = open_p * pump_multiplier
    new_high = high_p * pump_multiplier
    new_low = low_p * pump_multiplier
    new_close = close_p * pump_multiplier
    new_volume = volume * volume_multiplier

    cursor.execute("""
        UPDATE klines
        SET open = ?, high = ?, low = ?, close = ?, volume = ?
        WHERE symbol = 'BTC_USDT' AND exchange = 'gate.io' AND timestamp = ?
    """, (new_open, new_high, new_low, new_close, new_volume, timestamp))

# Do the same for ETH_USDT
cursor.execute("""
    SELECT timestamp, datetime, open, high, low, close, volume
    FROM klines
    WHERE symbol = 'ETH_USDT' AND exchange = 'gate.io'
    ORDER BY timestamp DESC
    LIMIT 10
""")
rows = cursor.fetchall()

for i in range(5):
    row = rows[i]
    timestamp, dt, open_p, high_p, low_p, close_p, volume = row

    pump_multiplier = 1.12
    volume_multiplier = 4.0

    new_open = open_p * pump_multiplier
    new_high = high_p * pump_multiplier
    new_low = low_p * pump_multiplier
    new_close = close_p * pump_multiplier
    new_volume = volume * volume_multiplier

    cursor.execute("""
        UPDATE klines
        SET open = ?, high = ?, low = ?, close = ?, volume = ?
        WHERE symbol = 'ETH_USDT' AND exchange = 'gate.io' AND timestamp = ?
    """, (new_open, new_high, new_low, new_close, new_volume, timestamp))

conn.commit()

# Verify changes
print(f"\n✅ Pump data added successfully!")

cursor.execute("""
    SELECT timestamp, datetime, open, high, low, close, volume
    FROM klines
    WHERE symbol = 'BTC_USDT' AND exchange = 'gate.io'
    ORDER BY timestamp DESC
    LIMIT 10
""")
rows = cursor.fetchall()

print(f"\n📊 Modified last 10 bars for BTC_USDT:")
for i, row in enumerate(reversed(rows)):
    print(f"   {i+1}. {row[1]} - Close: ${row[5]:.2f}, Volume: {row[6]:.0f}")

conn.close()

print("\n✨ Ready to test pump detection!")
