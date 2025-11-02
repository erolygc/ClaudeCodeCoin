"""
CHECK COLLECTORS - Collectors'ın durumunu kontrol et

Bu script:
1. Database'de hangi coinler var kontrol eder
2. Hangi coinler için veri toplanmış gösterir
3. Eksik coinleri listeler
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Config'den coin listesini al
sys.path.insert(0, 'config')
from trading_pairs import get_all_symbols

print("="*80)
print("COLLECTORS DURUM KONTROLU")
print("="*80)
print()

# Database kontrolü
db_file = Path("data_output/binance_data.db")

if not db_file.exists():
    print("HATA: Database bulunamadi!")
    print(f"Beklenen konum: {db_file.absolute()}")
    print()
    print("Collectors hic veri toplamamis!")
    print()
    print("Cozum:")
    print("  1. START_ALL_SYSTEMS_MULTI_COIN.bat calistir")
    print("  2. Collectors pencerelerinde veri toplandigini kontrol et")
    print("  3. 5-10 dakika bekle")
    print("  4. Bu scripti tekrar calistir")
    exit(1)

# Database'e bağlan
conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Son 30 dakika içinde veri toplanan coinleri listele
thirty_mins_ago = (datetime.now() - timedelta(minutes=30)).isoformat()

cursor.execute("""
    SELECT
        symbol,
        exchange,
        COUNT(*) as bar_count,
        MIN(datetime) as first_bar,
        MAX(datetime) as last_bar
    FROM klines
    WHERE datetime >= ?
    GROUP BY symbol, exchange
    ORDER BY exchange, symbol
""", (thirty_mins_ago,))

results = cursor.fetchall()

if not results:
    print("UYARI: Son 30 dakikada hic veri toplanmamis!")
    print()
    print("Collectors calismiyor olabilir. Kontrol et:")
    print("  - Collectors pencereleri acik mi?")
    print("  - Hata mesaji var mi?")
    print("  - Internet baglantisi var mi?")
    conn.close()
    exit(1)

# Beklenen coin listesi
expected_symbols = get_all_symbols()
binance_expected = set(expected_symbols['binance'])
gateio_expected = set([s.replace('_', '') if '_' in s else s for s in expected_symbols['gateio']])

# Toplanan coinler
binance_collected = set()
gateio_collected = set()

print("Son 30 dakikada toplanan veriler:")
print()

for symbol, exchange, bar_count, first_bar, last_bar in results:
    if exchange == 'binance':
        binance_collected.add(symbol)
    elif exchange == 'gate.io':
        gateio_collected.add(symbol)

    print(f"  {exchange:10s} {symbol:15s} - {bar_count:3d} bar | {first_bar[:16]} -> {last_bar[:16]}")

print()
print("="*80)
print("OZET")
print("="*80)
print()

print(f"Binance:")
print(f"  Beklenen: {len(binance_expected)} coin")
print(f"  Toplanan: {len(binance_collected)} coin")
print(f"  Eksik:    {len(binance_expected - binance_collected)} coin")

if len(binance_expected - binance_collected) > 0:
    missing = list(binance_expected - binance_collected)[:10]
    print(f"  Ornek eksikler: {', '.join(missing)}")

print()

print(f"Gate.io:")
print(f"  Beklenen: {len(gateio_expected)} coin (underscoreli format)")
print(f"  Toplanan: {len(gateio_collected)} coin")
print(f"  Eksik:    {len(gateio_expected - gateio_collected)} coin")

if len(gateio_expected - gateio_collected) > 0:
    missing = list(gateio_expected - gateio_collected)[:10]
    print(f"  Ornek eksikler: {', '.join(missing)}")

print()

# Collectors restart gerekiyor mu?
total_expected = len(binance_expected) + len(gateio_expected)
total_collected = len(binance_collected) + len(gateio_collected)

if total_collected < total_expected * 0.5:  # %50'den az toplandi
    print("⚠️  UYARI: Beklenen coinlerin %50'sinden azi toplaniyor!")
    print()
    print("COZUM:")
    print("  1. Tum Collector pencerelerini kapat")
    print("  2. git pull ile son coin listesini cek")
    print("  3. START_ALL_SYSTEMS_MULTI_COIN.bat ile tekrar baslat")
    print("  4. 30 dakika bekle")
elif total_collected < total_expected * 0.9:  # %90'dan az toplandı
    print("⚠️  Uyari: Bazi coinler eksik, collectors restart edilmeli")
else:
    print("✅ Collectors dogru sekilde calisiy or!")

conn.close()
