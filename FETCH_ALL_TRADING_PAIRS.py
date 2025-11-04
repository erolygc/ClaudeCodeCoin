"""
FETCH ALL TRADING PAIRS - Tüm Binance ve Gate.io USDT paritelerini çek

Bu script:
1. Binance'den tüm aktif USDT paritelerini çeker
2. Gate.io'dan tüm aktif USDT paritelerini çeker
3. Toplam coin sayısını ve listelerini gösterir
4. Yeni config dosyası için hazır formatta yazdırır
"""

import requests
import json
from typing import List, Dict

print("=" * 100)
print("🔍 TÜM TRADING PARİTELERİNİ ÇEKME")
print("=" * 100)
print()

# ====================================================================================
# 1. BINANCE USDT PARİTELERİ
# ====================================================================================
print("📊 1. BINANCE USDT PARİTELERİ")
print("-" * 100)

try:
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    binance_pairs = []

    for symbol in data['symbols']:
        # Sadece USDT paritelerini ve aktif olanları al
        if symbol['symbol'].endswith('USDT') and symbol['status'] == 'TRADING':
            # SPOT trading'i destekleyen
            if symbol['permissions'] and 'SPOT' in symbol['permissions']:
                binance_pairs.append(symbol['symbol'])

    binance_pairs.sort()

    print(f"✅ Binance'den {len(binance_pairs)} USDT paritesi bulundu")
    print()

    # İlk 20 ve son 20'yi göster
    print("İlk 20 parite:")
    for i in range(min(20, len(binance_pairs))):
        print(f"   {i+1:3d}. {binance_pairs[i]}")

    if len(binance_pairs) > 40:
        print(f"   ... ({len(binance_pairs) - 40} tane daha)")
        print()
        print("Son 20 parite:")
        for i in range(max(0, len(binance_pairs) - 20), len(binance_pairs)):
            print(f"   {i+1:3d}. {binance_pairs[i]}")

    print()

except Exception as e:
    print(f"❌ Binance API hatası: {e}")
    binance_pairs = []
    print()

# ====================================================================================
# 2. GATE.IO USDT PARİTELERİ
# ====================================================================================
print("=" * 100)
print("📊 2. GATE.IO USDT PARİTELERİ")
print("-" * 100)

try:
    url = "https://api.gateio.ws/api/v4/spot/currency_pairs"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    gateio_pairs = []

    for pair in data:
        # Sadece USDT paritelerini ve trade edilebilir olanları al
        if pair['id'].endswith('_USDT') and pair['trade_status'] == 'tradable':
            gateio_pairs.append(pair['id'])

    gateio_pairs.sort()

    print(f"✅ Gate.io'dan {len(gateio_pairs)} USDT paritesi bulundu")
    print()

    # İlk 20 ve son 20'yi göster
    print("İlk 20 parite:")
    for i in range(min(20, len(gateio_pairs))):
        print(f"   {i+1:3d}. {gateio_pairs[i]}")

    if len(gateio_pairs) > 40:
        print(f"   ... ({len(gateio_pairs) - 40} tane daha)")
        print()
        print("Son 20 parite:")
        for i in range(max(0, len(gateio_pairs) - 20), len(gateio_pairs)):
            print(f"   {i+1:3d}. {gateio_pairs[i]}")

    print()

except Exception as e:
    print(f"❌ Gate.io API hatası: {e}")
    gateio_pairs = []
    print()

# ====================================================================================
# 3. ÖZET VE ANALİZ
# ====================================================================================
print("=" * 100)
print("📊 ÖZET VE ANALİZ")
print("=" * 100)
print()

total_unique = len(set(binance_pairs + [p.replace('_', '') for p in gateio_pairs]))

print(f"📈 Binance:        {len(binance_pairs):4d} USDT paritesi")
print(f"📈 Gate.io:        {len(gateio_pairs):4d} USDT paritesi")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"📊 TOPLAM:         {len(binance_pairs) + len(gateio_pairs):4d} parite")
print(f"🔗 Benzersiz coin: ~{total_unique:4d} adet")
print()

# ====================================================================================
# 4. TEKNİK LİMİTLER VE ÖNERİLER
# ====================================================================================
print("=" * 100)
print("⚠️  TEKNİK LİMİTLER VE ÖNERİLER")
print("=" * 100)
print()

print("🔴 BINANCE LİMİTLERİ:")
print("   • Maksimum WebSocket stream: 200-300 (önerilir: 100-150)")
print("   • API Rate Limit: 1200 request/minute")
print(f"   • Mevcut parite sayısı: {len(binance_pairs)}")
print()

if len(binance_pairs) > 150:
    print("   ⚠️  ÖNERİ: Binance için MULTIPLE INSTANCE gerekli!")
    print(f"   • Instance 1: İlk {len(binance_pairs)//2} parite")
    print(f"   • Instance 2: Son {len(binance_pairs) - len(binance_pairs)//2} parite")
    print()

print("🟢 GATE.IO LİMİTLERİ:")
print("   • Maksimum WebSocket stream: Yüksek (1000+)")
print("   • API Rate Limit: Yüksek")
print(f"   • Mevcut parite sayısı: {len(gateio_pairs)}")
print("   • Single instance yeterli ✅")
print()

print("💾 DATABASE:")
estimated_size_mb = (len(binance_pairs) + len(gateio_pairs)) * 0.5  # ~0.5MB per coin per day
print(f"   • Günlük tahmini boyut: ~{estimated_size_mb:.0f} MB")
print(f"   • Aylık tahmini boyut: ~{estimated_size_mb * 30 / 1024:.1f} GB")
print()

print("💻 MEMORY:")
estimated_memory_mb = (len(binance_pairs) + len(gateio_pairs)) * 2  # ~2MB per coin
print(f"   • Tahmini RAM kullanımı: ~{estimated_memory_mb:.0f} MB")
print()

# ====================================================================================
# 5. CONFIG DOSYASI İÇİN HAZIR FORMATTA YAZDIR
# ====================================================================================
print("=" * 100)
print("📝 YENİ CONFIG İÇİN PYTHON KODU")
print("=" * 100)
print()

print("# config/trading_pairs.py için:")
print()
print("BINANCE_SYMBOLS = [")
for i, symbol in enumerate(binance_pairs):
    if i % 5 == 0:
        print("    ", end="")
    print(f'"{symbol}"', end="")
    if i < len(binance_pairs) - 1:
        print(", ", end="")
    if (i + 1) % 5 == 0:
        print()
if len(binance_pairs) % 5 != 0:
    print()
print("]")
print()

print("GATEIO_SYMBOLS = [")
for i, symbol in enumerate(gateio_pairs):
    if i % 5 == 0:
        print("    ", end="")
    print(f'"{symbol}"', end="")
    if i < len(gateio_pairs) - 1:
        print(", ", end="")
    if (i + 1) % 5 == 0:
        print()
if len(gateio_pairs) % 5 != 0:
    print()
print("]")
print()

# ====================================================================================
# 6. DOSYAYA KAYDET
# ====================================================================================
print("=" * 100)
print("💾 DOSYAYA KAYDETME")
print("=" * 100)
print()

# JSON formatında kaydet
output = {
    'binance': binance_pairs,
    'gateio': gateio_pairs,
    'total_binance': len(binance_pairs),
    'total_gateio': len(gateio_pairs),
    'total': len(binance_pairs) + len(gateio_pairs),
    'timestamp': '2025-11-03'
}

with open('all_trading_pairs.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ Tüm pariteler 'all_trading_pairs.json' dosyasına kaydedildi")
print()

# Python formatında kaydet
with open('all_trading_pairs.py', 'w', encoding='utf-8') as f:
    f.write('"""\n')
    f.write('Tüm Binance ve Gate.io USDT Trading Pairs\n')
    f.write(f'Toplam: {len(binance_pairs) + len(gateio_pairs)} parite\n')
    f.write('Otomatik oluşturuldu: 2025-11-03\n')
    f.write('"""\n\n')

    f.write(f"# Binance USDT Pairs ({len(binance_pairs)} adet)\n")
    f.write("BINANCE_SYMBOLS = [\n")
    for i, symbol in enumerate(binance_pairs):
        if i % 5 == 0:
            f.write("    ")
        f.write(f'"{symbol}"')
        if i < len(binance_pairs) - 1:
            f.write(", ")
        if (i + 1) % 5 == 0:
            f.write("\n")
    if len(binance_pairs) % 5 != 0:
        f.write("\n")
    f.write("]\n\n")

    f.write(f"# Gate.io USDT Pairs ({len(gateio_pairs)} adet)\n")
    f.write("GATEIO_SYMBOLS = [\n")
    for i, symbol in enumerate(gateio_pairs):
        if i % 5 == 0:
            f.write("    ")
        f.write(f'"{symbol}"')
        if i < len(gateio_pairs) - 1:
            f.write(", ")
        if (i + 1) % 5 == 0:
            f.write("\n")
    if len(gateio_pairs) % 5 != 0:
        f.write("\n")
    f.write("]\n")

print("✅ Python formatı 'all_trading_pairs.py' dosyasına kaydedildi")
print()

print("=" * 100)
print("✅ İŞLEM TAMAMLANDI")
print("=" * 100)
print()

print("📋 SONRAKI ADIMLAR:")
print()
print("1. 'all_trading_pairs.json' dosyasını incele")
print("2. Parite listesini gözden geçir ve istenmeyen coinleri çıkar")
print("3. config/trading_pairs.py dosyasını güncelle")
print("4. Multi-instance Collector stratejisi belirle")
print("5. Test et!")
print()
print("=" * 100)
