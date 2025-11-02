"""
RESET TO PRODUCTION - Test verilerini temizle ve gerçek sisteme geç

Bu script:
1. Test veritabanını siler
2. Test pozisyonlarını siler
3. Test alert'lerini siler
4. Sistemi production için hazırlar
"""

import os
import shutil
from pathlib import Path

print("="*80)
print("PRODUCTION RESET - Test Verilerini Temizleme")
print("="*80)
print()

# 1. Test database'ini sil
db_file = Path("data_output/binance_data.db")
if db_file.exists():
    print(f"1. Test veritabani siliniyor: {db_file}")
    db_file.unlink()
    print("   TAMAMLANDI - Database temizlendi")
else:
    print("1. Database zaten yok, atlanıyor...")

print()

# 2. Test pozisyonlarını sil
positions_file = Path("Phase7_PaperTrading/paper_trading_state.json")
if positions_file.exists():
    print(f"2. Test pozisyonlari siliniyor: {positions_file}")
    positions_file.unlink()
    print("   TAMAMLANDI - Pozisyonlar temizlendi ($10,000 bakiye sıfırlandı)")
else:
    print("2. Pozisyon dosyası zaten yok, atlanıyor...")

print()

# 3. Test alert'lerini sil
alerts_dir = Path("pump_alerts")
if alerts_dir.exists():
    print(f"3. Test alert'leri siliniyor: {alerts_dir}")
    # Tüm JSON dosyalarını sil
    deleted_count = 0
    for alert_file in alerts_dir.glob("*.json"):
        alert_file.unlink()
        deleted_count += 1
    print(f"   TAMAMLANDI - {deleted_count} alert dosyası silindi")
else:
    print("3. Alert dizini zaten yok, atlanıyor...")

print()
print("="*80)
print("TEMIZLEME TAMAMLANDI!")
print("="*80)
print()
print("Simdi yapilacaklar:")
print()
print("1. Collectors calistirarak gercek veri toplamaya baslayin")
print("2. 30-60 dakika bekleyin (veri birikimi icin)")
print("3. Pump Scanner gercek sinyalleri algilayacak")
print("4. Paper Trading gercek pozisyonlar acacak")
print()
print("Sistemin tamami START_ALL_SYSTEMS_MULTI_COIN.bat ile baslatilabilir")
print("="*80)
