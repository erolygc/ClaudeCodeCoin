"""
Test Data Generator - Gerçekçi kripto verisi üret
Pump detection ve paper trading test için
"""
import sqlite3
import random
from datetime import datetime, timedelta
import numpy as np

DB_FILE = "data_output/binance_data.db"

# Test için semboller
TEST_SYMBOLS = [
    "BTC_USDT", "ETH_USDT", "SOL_USDT", "PEPE_USDT", "SHIB_USDT",
    "WIF_USDT", "BONK_USDT", "FLOKI_USDT", "DOGE_USDT", "ARB_USDT",
    "OP_USDT", "MATIC_USDT", "AVAX_USDT", "LINK_USDT", "UNI_USDT",
]

def generate_realistic_price_data(symbol: str, bars: int = 200):
    """Gerçekçi fiyat verisi üret (bazı coinlerde pump simüle et)"""

    # Başlangıç fiyatı
    if "BTC" in symbol:
        base_price = 45000.0
    elif "ETH" in symbol:
        base_price = 2500.0
    elif "SOL" in symbol:
        base_price = 100.0
    elif "PEPE" in symbol or "SHIB" in symbol:
        base_price = 0.000015
    else:
        base_price = random.uniform(0.5, 50.0)

    # Veri üret
    data = []
    current_time = datetime.now() - timedelta(minutes=bars)
    current_price = base_price

    # Bu coin pump olacak mı? (30% şans)
    will_pump = random.random() < 0.3
    pump_start_bar = random.randint(bars - 30, bars - 10) if will_pump else -1

    for i in range(bars):
        # Normal volatilite
        volatility = 0.01  # %1

        # Pump simülasyonu
        if will_pump and i >= pump_start_bar and i < pump_start_bar + 20:
            # Pump phase: Hızlı yükseliş
            price_change = random.uniform(0.03, 0.08)  # %3-8 artış
            volume_multiplier = random.uniform(5, 15)  # 5-15x hacim
        elif will_pump and i >= pump_start_bar + 20:
            # Dump phase: Düşüş
            price_change = random.uniform(-0.05, -0.02)
            volume_multiplier = random.uniform(2, 5)
        else:
            # Normal hareket
            price_change = random.uniform(-volatility, volatility)
            volume_multiplier = 1.0

        # Fiyat hesapla
        current_price = current_price * (1 + price_change)
        open_price = current_price
        high_price = current_price * (1 + random.uniform(0, 0.01))
        low_price = current_price * (1 - random.uniform(0, 0.01))
        close_price = random.uniform(low_price, high_price)

        # Hacim
        base_volume = random.uniform(100000, 1000000)
        volume = base_volume * volume_multiplier

        # Timestamp
        timestamp = int(current_time.timestamp())
        datetime_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        data.append({
            'timestamp': timestamp,
            'datetime': datetime_str,
            'symbol': symbol,
            'interval': '1m',
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume,
            'number_of_trades': int(volume / 100),
            'collected_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'exchange': 'gate.io'
        })

        current_time += timedelta(minutes=1)
        current_price = close_price

    return data

def insert_test_data():
    """Test verisini database'e ekle"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    total_inserted = 0

    print("=" * 80)
    print("TEST DATA GENERATOR")
    print("=" * 80)
    print()

    for symbol in TEST_SYMBOLS:
        print(f"Generating data for {symbol}...")

        data = generate_realistic_price_data(symbol, bars=200)

        for row in data:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO klines
                    (timestamp, datetime, symbol, interval, open, high, low, close,
                     volume, number_of_trades, collected_at, exchange)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['timestamp'], row['datetime'], row['symbol'], row['interval'],
                    row['open'], row['high'], row['low'], row['close'],
                    row['volume'], row['number_of_trades'], row['collected_at'],
                    row['exchange']
                ))
                total_inserted += 1
            except Exception as e:
                print(f"  Error: {e}")

        print(f"  ✅ {len(data)} bars inserted")

    conn.commit()
    conn.close()

    print()
    print("=" * 80)
    print(f"✅ Total inserted: {total_inserted} records")
    print(f"✅ Symbols: {len(TEST_SYMBOLS)}")
    print(f"✅ Database ready for testing!")
    print("=" * 80)

if __name__ == "__main__":
    insert_test_data()
