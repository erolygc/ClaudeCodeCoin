"""
VERIFY COLLECTOR STARTUP - Collectors'ın doğru coin sayısıyla başladığını doğrula

Bu script:
1. Config'den beklenen coin sayısını alır
2. Son 2 dakikada toplanan unique coin sayısını kontrol eder
3. Collectors'ın doğru başlayıp başlamadığını gösterir

KULLANIM:
- Collectors'ı başlattıktan 2 dakika sonra çalıştır
- Her 30 saniyede bir çalıştırarak ilerlemeyi izle
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys
import time

# Config'den coin listesini al
sys.path.insert(0, 'config')
from trading_pairs import get_all_symbols

def clear_screen():
    """Ekranı temizle (Windows için)"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def check_collector_status():
    """Collector durumunu kontrol et"""

    print("=" * 100)
    print(f"🔍 COLLECTOR STARTUP VERIFICATION - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 100)
    print()

    # Beklenen coin sayıları
    expected_symbols = get_all_symbols()
    binance_expected = len(expected_symbols['binance'])
    gateio_expected = len(expected_symbols['gateio'])
    total_expected = binance_expected + gateio_expected

    print(f"📋 BEKLENEN COİN SAYILARI:")
    print(f"   Binance:  {binance_expected:3d} coin")
    print(f"   Gate.io:  {gateio_expected:3d} coin")
    print(f"   TOPLAM:   {total_expected:3d} coin")
    print()

    # Database kontrolü
    db_file = Path("data_output/binance_data.db")

    if not db_file.exists():
        print("❌ DATABASE HENÜZ OLUŞTURULMADI")
        print()
        print("   Durum: Collectors yeni başladı veya çalışmıyor")
        print()
        print("   Bekle:")
        print("      • Collectors'ı başlattıysan: 30-60 saniye bekle")
        print("      • Hala database oluşmadıysa: Collector pencerelerini kontrol et")
        print()
        return False

    # Database'e bağlan
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Son 2 dakika içinde veri toplanan coinleri say
    two_mins_ago = (datetime.now() - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT exchange, COUNT(DISTINCT symbol) as coin_count
        FROM klines
        WHERE datetime >= ?
        GROUP BY exchange
    """, (two_mins_ago,))

    results = cursor.fetchall()

    binance_active = 0
    gateio_active = 0

    for exchange, count in results:
        if exchange == 'binance':
            binance_active = count
        elif exchange == 'gate.io':
            gateio_active = count

    total_active = binance_active + gateio_active

    # Toplam kayıt sayısı
    cursor.execute("SELECT COUNT(*) FROM klines")
    total_records = cursor.fetchone()[0]

    # Son kayıt zamanı
    cursor.execute("SELECT MAX(datetime) FROM klines")
    last_record = cursor.fetchone()[0]

    conn.close()

    print(f"📊 SON 2 DAKİKADA AKTİF COİNLER:")
    print(f"   Binance:  {binance_active:3d} / {binance_expected:3d} coin", end="")
    if binance_active >= binance_expected:
        print(" ✅")
    elif binance_active >= binance_expected * 0.9:
        print(" ⚠️  (90%+ tamamlandı)")
    elif binance_active > 0:
        print(f" 🔄 ({binance_active/binance_expected*100:.0f}% - veri toplanıyor...)")
    else:
        print(" ❌ (Binance Collector çalışmıyor?)")

    print(f"   Gate.io:  {gateio_active:3d} / {gateio_expected:3d} coin", end="")
    if gateio_active >= gateio_expected:
        print(" ✅")
    elif gateio_active >= gateio_expected * 0.9:
        print(" ⚠️  (90%+ tamamlandı)")
    elif gateio_active > 0:
        print(f" 🔄 ({gateio_active/gateio_expected*100:.0f}% - veri toplanıyor...)")
    else:
        print(" ❌ (Gate.io Collector çalışmıyor?)")

    print(f"   TOPLAM:   {total_active:3d} / {total_expected:3d} coin", end="")
    if total_active >= total_expected * 0.95:
        print(" ✅")
    else:
        print(f" 🔄 ({total_active/total_expected*100:.0f}%)")

    print()
    print(f"💾 DATABASE DURUMU:")
    print(f"   Toplam kayıt: {total_records:,}")
    print(f"   Son kayıt:    {last_record}")
    print()

    # Durum değerlendirmesi
    print("=" * 100)

    if total_active == 0:
        print("❌ COLLECTORS ÇALIŞMIYOR!")
        print()
        print("   ÇÖZÜM:")
        print("      1. Collector pencerelerinin açık olduğunu kontrol et")
        print("      2. Hata mesajı varsa oku")
        print("      3. Gerekirse Collectors'ı restart et")
        print()
        return False

    elif total_active < total_expected * 0.5:
        print("🔄 COLLECTORS YENİ BAŞLADI - VERİ TOPLANMAYA BAŞLADI")
        print()
        progress_pct = (total_active / total_expected) * 100
        print(f"   İlerleme: {progress_pct:.0f}%")
        print(f"   Durum: {total_active} / {total_expected} coin aktif")
        print()
        print("   BEKLEYİN:")
        print("      • Bu scripti 30 saniyede bir çalıştırarak ilerlemeyi izle")
        print("      • 2-5 dakika içinde tüm coinler aktif olacak")
        print()
        return False

    elif total_active < total_expected * 0.95:
        print("⚠️  COLLECTORS NEREDEYSE TAMAM")
        print()
        progress_pct = (total_active / total_expected) * 100
        print(f"   İlerleme: {progress_pct:.0f}%")
        print(f"   Durum: {total_active} / {total_expected} coin aktif")
        print()
        missing = total_expected - total_active
        print(f"   Son {missing} coin bekleniyor...")
        print("   • 1-2 dakika daha bekle")
        print()
        return False

    else:
        print("✅ COLLECTORS BAŞARIYLA BAŞLADI!")
        print()
        print(f"   Binance:  {binance_active} / {binance_expected} coin ✅")
        print(f"   Gate.io:  {gateio_active} / {gateio_expected} coin ✅")
        print(f"   TOPLAM:   {total_active} / {total_expected} coin ✅")
        print()
        print("   Sistem hazır! Şimdi:")
        print("      1. 15-30 dakika daha veri birikimini bekle")
        print("      2. Paper Trading otomatik olarak pozisyon açmaya başlayacak")
        print("      3. Dashboard'da pozisyonları izle")
        print()
        print("   İlerlemeyi izlemek için:")
        print("      python SYSTEM_STATUS_CHECK.py")
        print()
        return True

if __name__ == "__main__":
    # İlk kontrol
    all_ok = check_collector_status()

    if not all_ok:
        print()
        print("🔄 Bu scripti tekrar çalıştırmak için:")
        print("   python VERIFY_COLLECTOR_STARTUP.py")
        print()
        print("💡 Otomatik izleme için:")
        print("   Her 30 saniyede bir çalıştır ve ilerlemeyi izle")

    print("=" * 100)
