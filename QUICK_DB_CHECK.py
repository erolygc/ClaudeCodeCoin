"""
Hızlı Database Kontrolü - Son toplanan verileri göster
"""
import sqlite3
from pathlib import Path

db_file = Path("data_output/binance_data.db")

if not db_file.exists():
    print("❌ Database bulunamadı!")
    exit(1)

conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Son 10 kayıt
print("=" * 80)
print("SON 10 KAYIT")
print("=" * 80)
cursor.execute("""
    SELECT datetime, symbol, exchange, close, volume
    FROM klines
    ORDER BY datetime DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0][:19]:20s} | {row[1]:15s} | {row[2]:10s} | ${row[3]:.4f} | Vol: {row[4]:.2f}")

print()

# Coin sayısı
print("=" * 80)
print("EXCHANGE BAŞINA COIN SAYISI")
print("=" * 80)
cursor.execute("""
    SELECT exchange, COUNT(DISTINCT symbol) as coin_count
    FROM klines
    GROUP BY exchange
""")

for row in cursor.fetchall():
    print(f"{row[0]:15s}: {row[1]} coin")

print()

# Toplam kayıt sayısı
print("=" * 80)
print("TOPLAM İSTATİSTİKLER")
print("=" * 80)
cursor.execute("SELECT COUNT(*) FROM klines")
total = cursor.fetchone()[0]
print(f"Toplam kayıt: {total:,}")

cursor.execute("SELECT MIN(datetime), MAX(datetime) FROM klines")
min_dt, max_dt = cursor.fetchone()
print(f"İlk kayıt: {min_dt}")
print(f"Son kayıt: {max_dt}")

print()

# Datetime formatını kontrol et
print("=" * 80)
print("DATETIME FORMAT KONTROLÜ")
print("=" * 80)
cursor.execute("SELECT datetime FROM klines LIMIT 5")
for row in cursor.fetchall():
    dt_str = row[0]
    print(f"Format: {dt_str} (uzunluk: {len(dt_str)})")

conn.close()
