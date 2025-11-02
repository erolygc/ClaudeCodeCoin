"""
TEST PAPER TRADING - Sahte veri ile test et

Bu script collectors beklemeden paper trading'in çalışıp çalışmadığını test eder.
Sahte fiyat verisi oluşturur ve paper trading'in pozisyon açıp açmadığını kontrol eder.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

print("="*80)
print("🧪 PAPER TRADING TEST MODU")
print("="*80)
print()

# 1. Test veritabanı oluştur
test_db = Path("data_output/binance_data.db")
test_db.parent.mkdir(exist_ok=True)

print("📝 1. Test veritabanı oluşturuluyor...")
conn = sqlite3.connect(str(test_db))
cursor = conn.cursor()

# Tablo oluştur
cursor.execute("""
    CREATE TABLE IF NOT EXISTS klines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER NOT NULL,
        datetime TEXT NOT NULL,
        symbol TEXT NOT NULL,
        interval TEXT NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume REAL NOT NULL,
        number_of_trades INTEGER DEFAULT 0,
        collected_at TEXT NOT NULL,
        exchange TEXT DEFAULT 'gate.io',
        UNIQUE(timestamp, symbol, exchange)
    )
""")

# 2. Sahte fiyat verileri ekle
print("💰 2. Sahte fiyat verileri ekleniyor...")

test_coins = [
    ("BTC_USDT", 67000, 70000),
    ("ETH_USDT", 3200, 3500),
    ("BONK_USDT", 0.000025, 0.000030),
    ("PEPE_USDT", 0.0000085, 0.0000095),
    ("SOL_USDT", 165, 175),
    ("DOGE_USDT", 0.14, 0.16),
    ("SHIB_USDT", 0.000018, 0.000022),
    ("CELO_USDT", 0.62, 0.68),
    ("AAVE_USDT", 145, 155),
    ("MATIC_USDT", 0.58, 0.62),
]

# Son 60 dakika için 1 dakikalık mumlar ekle
base_time = datetime.now()

for symbol, price_min, price_max in test_coins:
    for i in range(60):
        timestamp = base_time - timedelta(minutes=60-i)
        timestamp_unix = int(timestamp.timestamp())

        # Random fiyat oluştur (volatilite ekle)
        base_price = random.uniform(price_min, price_max)
        open_price = base_price * random.uniform(0.995, 1.005)
        high_price = open_price * random.uniform(1.0, 1.01)
        low_price = open_price * random.uniform(0.99, 1.0)
        close_price = random.uniform(low_price, high_price)
        volume = random.uniform(10000, 50000)

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO klines
                (timestamp, datetime, symbol, interval, open, high, low, close, volume, collected_at, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp_unix,
                timestamp.isoformat(),
                symbol,
                "1m",
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                datetime.now().isoformat(),
                "gate.io"
            ))
        except:
            pass  # Duplicate entry

conn.commit()

print(f"   ✅ {len(test_coins)} coin için 60 dakikalık veri eklendi")

# Eklenen verileri doğrula
cursor.execute("SELECT COUNT(DISTINCT symbol) FROM klines WHERE exchange='gate.io'")
coin_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM klines WHERE exchange='gate.io'")
total_records = cursor.fetchone()[0]
conn.close()

print(f"   ✅ Veritabanında {coin_count} coin, {total_records} kayıt var")
print()

# 3. Test alert'leri oluştur
print("🚨 3. Test alert'leri oluşturuluyor...")

alert_dir = Path("pump_alerts")
alert_dir.mkdir(exist_ok=True)

test_alerts = [
    {
        "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
        "symbol": "BONK_USDT",
        "exchange": "gate.io",
        "confidence": 100.0,
        "volume_change_pct": 1030.0,
        "price_change_pct": 5.2,
        "current_price": 0.000027
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=3)).isoformat(),
        "symbol": "PEPE_USDT",
        "exchange": "gate.io",
        "confidence": 95.0,
        "volume_change_pct": 850.0,
        "price_change_pct": 4.8,
        "current_price": 0.0000091
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
        "symbol": "SHIB_USDT",
        "exchange": "gate.io",
        "confidence": 88.0,
        "volume_change_pct": 720.0,
        "price_change_pct": 3.5,
        "current_price": 0.000020
    },
]

alert_file = alert_dir / f"pump_alerts_{datetime.now().strftime('%Y%m%d')}.json"
with open(alert_file, 'w', encoding='utf-8') as f:
    json.dump(test_alerts, f, indent=2, ensure_ascii=False)

print(f"   ✅ {len(test_alerts)} test alert oluşturuldu")
print()

# 4. Özet
print("="*80)
print("✅ TEST ORTAMI HAZIR!")
print("="*80)
print()
print("📊 Oluşturulan veriler:")
print(f"   • Veritabanı: {test_db}")
print(f"   • {coin_count} coin için fiyat verisi")
print(f"   • {len(test_alerts)} adet pump alert")
print()
print("🚀 ŞİMDİ YAPILACAKLAR:")
print()
print("1. Paper Trading'i başlatın:")
print("   python Phase7_PaperTrading\\paper_trading_engine.py")
print()
print("2. Şunları göreceksiniz:")
print("   ✅ Fiyat verisi VAR (3 alert)")
print("      └── BONK_USDT (100%, 1030%)")
print("      └── PEPE_USDT (95%, 850%)")
print("      └── SHIB_USDT (88%, 720%)")
print("   🎯 BONK_USDT için pozisyon açılıyor...")
print("   ✅ Pozisyon açıldı: BONK_USDT")
print()
print("="*80)
