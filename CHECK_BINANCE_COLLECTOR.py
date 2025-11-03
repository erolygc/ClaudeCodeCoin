"""
CHECK BINANCE COLLECTOR - Binance Collector'ın gerçek durumunu kontrol et

Bu script:
1. Binance için hangi coinlerin veri toplandığını gösterir
2. Eksik coinleri listeler
3. Binance Collector'ın restart edilip edilmediğini anlar
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Config'den coin listesini al
sys.path.insert(0, 'config')
from trading_pairs import BINANCE_SYMBOLS

print("=" * 100)
print("🔍 BINANCE COLLECTOR DURUM KONTROLU")
print("=" * 100)
print()

# Beklenen coin listesi
expected_binance = set(BINANCE_SYMBOLS)
print(f"📋 CONFIG'DE TANIMLI BINANCE COİNLERİ: {len(expected_binance)} adet")
print()

# Database kontrolü
db_file = Path("data_output/binance_data.db")

if not db_file.exists():
    print("❌ DATABASE BULUNAMADI!")
    exit(1)

conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# SON 5 DAKİKADA veri toplanan Binance coinleri
five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")

cursor.execute("""
    SELECT
        symbol,
        COUNT(*) as bar_count,
        MAX(datetime) as last_bar
    FROM klines
    WHERE exchange = 'binance' AND datetime >= ?
    GROUP BY symbol
    ORDER BY last_bar DESC
""", (five_mins_ago,))

active_coins = cursor.fetchall()

print(f"📊 SON 5 DAKİKADA AKTİF BINANCE COİNLERİ: {len(active_coins)} adet")
print()

if len(active_coins) == 0:
    print("❌ BINANCE COLLECTOR ÇALIŞMIYOR!")
    print()
    print("ÇÖZÜM:")
    print("  1. Binance Collector penceresini kontrol et")
    print("  2. Hata mesajı varsa oku")
    print("  3. Pencereyi kapat ve yeniden başlat")
    conn.close()
    exit(1)

# Aktif coinleri göster (son 10 tanesi)
print("Son güncellenen coinler:")
for symbol, bar_count, last_bar in active_coins[:10]:
    print(f"  {symbol:15s} - {bar_count:2d} bar | Son: {last_bar}")

print()

# Eksik coinleri bul
active_symbols = set([coin[0] for coin in active_coins])
missing_coins = expected_binance - active_symbols

print("=" * 100)
print("📊 KARŞILAŞTIRMA")
print("=" * 100)
print()

print(f"✅ Veri toplanan:  {len(active_symbols):3d} / {len(expected_binance)} coin")
print(f"❌ Eksik olan:     {len(missing_coins):3d} / {len(expected_binance)} coin")
print()

if len(missing_coins) > 0:
    print("EKSİK COİNLER:")
    missing_list = sorted(list(missing_coins))

    # İlk 30 eksik coini göster
    for i in range(0, min(30, len(missing_list)), 3):
        line = "  "
        for j in range(3):
            if i + j < len(missing_list):
                line += f"{missing_list[i+j]:15s} "
        print(line)

    if len(missing_list) > 30:
        print(f"  ... ve {len(missing_list) - 30} tane daha")

    print()

# Tanı
print("=" * 100)
print("🔍 TANI")
print("=" * 100)
print()

if len(active_symbols) < 100:
    print("❌ SORUN: Binance Collector ESKİ LİSTEYLE ÇALIŞIYOR!")
    print()
    print(f"   Beklenen: {len(expected_binance)} coin (YENİ liste)")
    print(f"   Toplanan: {len(active_symbols)} coin (ESKİ liste)")
    print()
    print("   Bu Binance Collector'ın RESTART EDİLMEDİĞİ anlamına gelir!")
    print()
    print("🔧 ÇÖZÜM:")
    print()
    print("   1. BINANCE COLLECTOR PENCERESİNİ BUL")
    print("      • Başlıkta \"Binance Collector\" yazıyor")
    print()
    print("   2. BAŞLANGIÇ MESAJINI KONTROL ET")
    print("      • Kaç coin yüklendi?")
    print("      • 93 coin diyorsa → ESKİ! Kapat!")
    print("      • 171 coin diyorsa → YENİ! Doğru!")
    print()
    print("   3. ESKİYSE KAPAT VE YENİDEN BAŞLAT")
    print("      • Pencereyi X ile kapat")
    print("      • Yeni terminal aç:")
    print()
    print("        cd Phase1_DataBackbone\\data_collectors")
    print("        python binance_collector_multi_coin.py")
    print()
    print("   4. YENİ PENCEREDE ŞU MESAJI GÖR:")
    print("      \"📊 171 trading pairs yüklendi\"")
    print()
    print("   5. 2 DAKİKA BEKLE VE DOĞRULA:")
    print("      python CHECK_BINANCE_COLLECTOR.py")
    print()

elif len(active_symbols) < len(expected_binance) * 0.9:
    print("⚠️  UYARI: Bazı coinler henüz veri göndermiyor")
    print()
    print(f"   Beklenen: {len(expected_binance)} coin")
    print(f"   Aktif:    {len(active_symbols)} coin ({len(active_symbols)/len(expected_binance)*100:.0f}%)")
    print()
    print("   Durum: Binance Collector DOĞRU başladı ama henüz tüm coinler aktif değil")
    print()
    print("   ÇÖZÜM:")
    print("      • 5-10 dakika daha bekle")
    print("      • Bazı coinler düşük likiditeye sahip, veri gelmesi uzun sürebilir")
    print("      • Toplam coin sayısı 90%'ı geçerse sistem çalışmaya başlar")
    print()

else:
    print("✅ Binance Collector DOĞRU ÇALIŞIYOR!")
    print()
    print(f"   {len(active_symbols)} / {len(expected_binance)} coin aktif ({len(active_symbols)/len(expected_binance)*100:.0f}%)")
    print()
    print("   Sistem hazır! Paper Trading pozisyon açmaya başlayabilir.")
    print()

conn.close()

print("=" * 100)
