"""
SYSTEM STATUS CHECK - Tüm sistem bileşenlerini kontrol et

Bu script:
1. Config'deki beklenen coin listesini gösterir
2. Database'de hangi coinler için veri var kontrol eder
3. Pump Scanner'ın hangi coinleri izlediğini gösterir
4. Paper Trading'in durumunu kontrol eder
5. Sistemi aktif hale getirmek için gereken adımları listeler
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys
import json

# Config'den coin listesini al
sys.path.insert(0, 'config')
from trading_pairs import get_all_symbols

print("=" * 100)
print("🔍 CLAUDECODECOIN SYSTEM STATUS CHECK")
print("=" * 100)
print()

# ============================================================================
# 1. CONFIG - Beklenen Coin Listesi
# ============================================================================
print("📋 1. CONFIG - BEKLENEN COİN LİSTESİ")
print("-" * 100)

expected_symbols = get_all_symbols()
binance_expected = set(expected_symbols['binance'])
gateio_expected = set([s.replace('_', '') if '_' in s else s for s in expected_symbols['gateio']])

print(f"   Binance:  {len(binance_expected):3d} coin bekleniyor")
print(f"   Gate.io:  {len(gateio_expected):3d} coin bekleniyor")
print(f"   TOPLAM:   {len(binance_expected) + len(gateio_expected):3d} coin")
print()

# ============================================================================
# 2. DATABASE - Mevcut Veri Durumu
# ============================================================================
print("💾 2. DATABASE - MEVCUT VERİ DURUMU")
print("-" * 100)

db_file = Path("data_output/binance_data.db")

if not db_file.exists():
    print("   ❌ DATABASE BULUNAMADI!")
    print()
    print("   🔧 ÇÖZÜM: START_ALL_SYSTEMS_MULTI_COIN.bat çalıştır")
    exit(1)

conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Toplam kayıt sayısı
cursor.execute("SELECT COUNT(*) FROM klines")
total_records = cursor.fetchone()[0]

# Zaman aralığı
cursor.execute("SELECT MIN(datetime), MAX(datetime) FROM klines")
min_dt, max_dt = cursor.fetchone()

# Exchange başına coin sayısı
cursor.execute("""
    SELECT exchange, COUNT(DISTINCT symbol) as coin_count
    FROM klines
    GROUP BY exchange
""")

binance_collected = 0
gateio_collected = 0

for exchange, count in cursor.fetchall():
    if exchange == 'binance':
        binance_collected = count
    elif exchange == 'gate.io':
        gateio_collected = count

print(f"   Toplam kayıt: {total_records:,}")
print(f"   İlk kayıt:    {min_dt}")
print(f"   Son kayıt:    {max_dt}")
print()
print(f"   Binance:  {binance_collected:3d} coin (beklenen: {len(binance_expected)})")
print(f"   Gate.io:  {gateio_collected:3d} coin (beklenen: {len(gateio_expected)})")
print(f"   TOPLAM:   {binance_collected + gateio_collected:3d} coin (beklenen: {len(binance_expected) + len(gateio_expected)})")
print()

# ============================================================================
# 3. COLLECTORS - Son 30 Dakika Aktivitesi
# ============================================================================
print("📡 3. COLLECTORS - SON 30 DAKİKA AKTİVİTESİ")
print("-" * 100)

thirty_mins_ago = (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

cursor.execute("""
    SELECT exchange, COUNT(DISTINCT symbol) as active_coins
    FROM klines
    WHERE datetime >= ?
    GROUP BY exchange
""", (thirty_mins_ago,))

active_binance = 0
active_gateio = 0

for exchange, count in cursor.fetchall():
    if exchange == 'binance':
        active_binance = count
    elif exchange == 'gate.io':
        active_gateio = count

if active_binance + active_gateio == 0:
    print("   ❌ SON 30 DAKİKADA VERİ TOPLANMAMIŞ!")
    print()
    print("   🔧 ÇÖZÜM:")
    print("      1. Collectors pencerelerinin açık ve çalıştığından emin ol")
    print("      2. Eğer kapalıysa START_ALL_SYSTEMS_MULTI_COIN.bat çalıştır")
    conn.close()
    exit(1)

print(f"   Binance:  {active_binance:3d} coin aktif")
print(f"   Gate.io:  {active_gateio:3d} coin aktif")
print(f"   TOPLAM:   {active_binance + active_gateio:3d} coin aktif")
print()

# ============================================================================
# 4. COIN LİSTESİ KARŞILAŞTIRMASI
# ============================================================================
print("🔄 4. COİN LİSTESİ KARŞILAŞTIRMASI")
print("-" * 100)

# Database'deki coinleri al
cursor.execute("SELECT DISTINCT symbol, exchange FROM klines")
db_coins_raw = cursor.fetchall()

db_binance = set()
db_gateio = set()

for symbol, exchange in db_coins_raw:
    if exchange == 'binance':
        db_binance.add(symbol)
    elif exchange == 'gate.io':
        # Gate.io database'de underscore'suz saklanıyor
        db_gateio.add(symbol)

# Eksik coinleri hesapla
missing_binance = binance_expected - db_binance
missing_gateio = gateio_expected - db_gateio

print(f"   Binance:")
if len(missing_binance) == 0:
    print(f"      ✅ Tüm {len(binance_expected)} coin database'de var")
else:
    print(f"      ⚠️  {len(missing_binance)} coin EKSİK (beklenen: {len(binance_expected)}, mevcut: {len(db_binance)})")
    if len(missing_binance) <= 20:
        print(f"      Eksik coinler: {', '.join(sorted(missing_binance))}")
    else:
        sample = list(sorted(missing_binance))[:10]
        print(f"      Örnek eksikler: {', '.join(sample)} ... (+{len(missing_binance)-10} daha)")

print()
print(f"   Gate.io:")
if len(missing_gateio) == 0:
    print(f"      ✅ Tüm {len(gateio_expected)} coin database'de var")
else:
    print(f"      ⚠️  {len(missing_gateio)} coin EKSİK (beklenen: {len(gateio_expected)}, mevcut: {len(db_gateio)})")
    if len(missing_gateio) <= 20:
        print(f"      Eksik coinler: {', '.join(sorted(missing_gateio))}")
    else:
        sample = list(sorted(missing_gateio))[:10]
        print(f"      Örnek eksikler: {', '.join(sample)} ... (+{len(missing_gateio)-10} daha)")

print()

conn.close()

# ============================================================================
# 5. PUMP SCANNER - Alert Durumu
# ============================================================================
print("🚨 5. PUMP SCANNER - ALERT DURUMU")
print("-" * 100)

alert_file = Path("pump_alerts") / f"pump_alerts_{datetime.now().strftime('%Y%m%d')}.json"

if not alert_file.exists():
    print("   ⚠️  Bugün için alert dosyası bulunamadı")
    print(f"   Dosya: {alert_file}")
    print()
    print("   🔧 ÇÖZÜM: Pump Scanner'ın çalıştığından emin ol")
else:
    with open(alert_file, 'r', encoding='utf-8') as f:
        alerts = json.load(f)

    total_alerts = len(alerts)

    # Son 10 dakika içindeki alertler
    ten_mins_ago = datetime.now() - timedelta(minutes=10)
    recent_alerts = [
        alert for alert in alerts
        if datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00')) > ten_mins_ago
    ]

    print(f"   Toplam alert:      {total_alerts}")
    print(f"   Son 10 dakika:     {len(recent_alerts)}")

    if len(recent_alerts) > 0:
        print()
        print("   Son alertler:")
        for alert in recent_alerts[-5:]:
            symbol = alert['symbol']
            confidence = alert.get('confidence', 0)
            volume_change = alert.get('volume_change_pct', 0)
            timestamp = alert['timestamp'][:16]
            print(f"      {timestamp} | {symbol:15s} | Güven: {confidence:3.0f}% | Volume: +{volume_change:.0f}%")

    print()

# ============================================================================
# 6. PAPER TRADING - Pozisyon Durumu
# ============================================================================
print("💰 6. PAPER TRADING - POZİSYON DURUMU")
print("-" * 100)

paper_state_file = Path("Phase7_PaperTrading/paper_trading_state.json")

if not paper_state_file.exists():
    print("   ℹ️  Paper trading state dosyası yok (yeni başlangıç)")
    print("   Başlangıç bakiyesi: $10,000")
    print("   Açık pozisyon: 0")
else:
    with open(paper_state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    balance = state.get('balance', 10000)
    positions = state.get('positions', [])
    trade_history = state.get('trade_history', [])

    print(f"   Bakiye:           ${balance:,.2f}")
    print(f"   Açık pozisyon:    {len(positions)}")
    print(f"   Toplam işlem:     {len(trade_history)}")

    if positions:
        print()
        print("   Açık pozisyonlar:")
        for pos in positions:
            symbol = pos['symbol']
            entry_price = pos['entry_price']
            current_price = pos.get('current_price', entry_price)
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            print(f"      {symbol:15s} | Giriş: ${entry_price:.6f} | Şu an: ${current_price:.6f} | PnL: {pnl_pct:+.2f}%")

print()

# ============================================================================
# 7. SYSTEM DIAGNOSIS & RECOMMENDATIONS
# ============================================================================
print("=" * 100)
print("📊 SİSTEM TANISI VE ÖNERİLER")
print("=" * 100)
print()

total_expected = len(binance_expected) + len(gateio_expected)
total_collected = binance_collected + gateio_collected
total_missing = len(missing_binance) + len(missing_gateio)

# Diagnosis
issues = []
if total_collected < total_expected:
    issues.append("coin_list_mismatch")
if active_binance + active_gateio == 0:
    issues.append("collectors_not_running")
if not alert_file.exists():
    issues.append("pump_scanner_not_running")

if len(issues) == 0:
    print("✅ TÜM SİSTEM BİLEŞENLERİ ÇALIŞIYOR!")
    print()
    print("Sistem durumu:")
    print(f"   • {total_collected}/{total_expected} coin için veri toplanıyor")
    print(f"   • Son 30 dakikada {active_binance + active_gateio} coin aktif")
    print(f"   • Pump Scanner çalışıyor")
    print(f"   • Paper Trading hazır")
    print()
    print("Eğer hala pozisyon açılmıyorsa:")
    print("   1. Son 10 dakikada pump sinyali olup olmadığını kontrol et")
    print("   2. Pump Scanner'ın threshold ayarlarını kontrol et")
    print("   3. Paper Trading log dosyasını kontrol et")
else:
    print("⚠️  SİSTEM AKTİVASYONU GEREKLİ")
    print()

    if "coin_list_mismatch" in issues:
        print(f"❌ SORUN: Collectors {total_missing} coin için veri toplamıyor")
        print()
        print(f"   Config'de {total_expected} coin var")
        print(f"   Database'de {total_collected} coin var")
        print(f"   Fark: {total_missing} coin EKSİK")
        print()
        print("   Bu yüzden Pump Scanner sinyalleri Paper Trading'e ulaşmıyor!")
        print()

    print("🔧 ÇÖZÜM ADIMLARI:")
    print()
    print("   1. TÜM COLLECTOR PENCERELERİNİ KAPAT")
    print("      • Binance Collector")
    print("      • Gate.io Collector")
    print()
    print("   2. YENİ COİN LİSTESİ İLE YENİDEN BAŞLAT")
    print("      • START_ALL_SYSTEMS_MULTI_COIN.bat çalıştır")
    print()
    print("   3. VERİFY EDİN:")
    print("      • Binance Collector: 171 coin yüklendiğini kontrol et")
    print("      • Gate.io Collector: 161 coin yüklendiğini kontrol et")
    print()
    print("   4. VERİ BİRİKİMİNİ BEKLE (15-30 dakika)")
    print("      • Yeni coinler için fiyat verisi toplanacak")
    print("      • Bu scripti tekrar çalıştırarak ilerlemeyi izle")
    print()
    print("   5. PAPER TRADING OTOMATİK OLARAK BAŞLAYACAK")
    print("      • Fiyat verisi olan coinler için pozisyon açılacak")
    print("      • Dashboard'da pozisyonları görebilirsin")
    print()

print("=" * 100)
print("Script tamamlandı. Sorular için log'lara bak.")
print("=" * 100)
