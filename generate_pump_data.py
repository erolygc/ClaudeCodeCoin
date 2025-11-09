"""
Generate Strong Pump Data for Testing
3-4 coin için güçlü pump senaryoları oluştur
"""
import sqlite3
import random
from datetime import datetime, timedelta
import numpy as np

DB_FILE = "data_output/binance_data.db"

def create_strong_pump(symbol: str, base_price: float):
    """Güçlü pump verisi oluştur - %70+ confidence için"""

    data = []
    current_time = datetime.now() - timedelta(minutes=100)

    # İlk 80 bar: Normal hareket
    current_price = base_price
    for i in range(80):
        volatility = 0.005  # %0.5
        price_change = random.uniform(-volatility, volatility)

        current_price = current_price * (1 + price_change)
        open_price = current_price
        high_price = current_price * (1 + random.uniform(0, 0.005))
        low_price = current_price * (1 - random.uniform(0, 0.005))
        close_price = random.uniform(low_price, high_price)

        # Normal volume
        volume = random.uniform(500000, 1000000)

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

    # Son 20 bar: GÜÇLÜ PUMP!
    print(f"  🚀 PUMP starting at bar 80 for {symbol}")
    print(f"     Base price: ${current_price:.6f}")

    pump_entry_price = current_price

    for i in range(20):
        # Güçlü yükseliş
        price_change = random.uniform(0.05, 0.12)  # %5-12 artış per bar

        current_price = current_price * (1 + price_change)
        open_price = data[-1]['close'] if data else current_price
        high_price = current_price * 1.02
        low_price = open_price * 0.98
        close_price = current_price

        # Çok yüksek hacim (10-20x)
        volume_multiplier = random.uniform(10, 20)
        volume = random.uniform(500000, 1000000) * volume_multiplier

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
            'number_of_trades': int(volume / 80),
            'collected_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'exchange': 'gate.io'
        })

        current_time += timedelta(minutes=1)

    pump_exit_price = current_price
    pump_pct = ((pump_exit_price - pump_entry_price) / pump_entry_price) * 100

    print(f"     Pump gain: +{pump_pct:.1f}%")
    print(f"     Exit price: ${pump_exit_price:.6f}")

    return data

def main():
    print("=" * 80)
    print("STRONG PUMP DATA GENERATOR")
    print("=" * 80)
    print()

    # Pump coinleri
    pump_coins = [
        ("PEPE_USDT", 0.000015),
        ("BONK_USDT", 0.000025),
        ("WIF_USDT", 2.5),
        ("FLOKI_USDT", 0.00018),
    ]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for symbol, base_price in pump_coins:
        print(f"Creating strong pump for {symbol}...")

        # Eski veriyi sil
        cursor.execute("DELETE FROM klines WHERE symbol = ?", (symbol,))

        # Yeni veri oluştur
        data = create_strong_pump(symbol, base_price)

        # Database'e ekle
        for row in data:
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

        print(f"  ✅ {len(data)} bars inserted\n")

    conn.commit()
    conn.close()

    print("=" * 80)
    print(f"✅ {len(pump_coins)} coins with STRONG PUMPS created!")
    print("=" * 80)

if __name__ == "__main__":
    main()
