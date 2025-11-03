"""
FULL SYSTEM CHECK - Tüm sistemi kontrol et
Her bileşeni kontrol eder ve sorunları tanımlar
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, 'config')
from trading_pairs import BINANCE_SYMBOLS, GATEIO_SYMBOLS

def check_component(name, check_func):
    """Bir bileşeni kontrol et ve sonucu göster"""
    print(f"Kontrol ediliyor: {name}...", end=" ")
    try:
        result = check_func()
        if result['status'] == 'ok':
            print(f"✅ OK")
            if result.get('details'):
                print(f"   └── {result['details']}")
        elif result['status'] == 'warning':
            print(f"⚠️  WARNING")
            print(f"   └── {result['message']}")
        else:
            print(f"❌ FAILED")
            print(f"   └── {result['message']}")
        return result
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {'status': 'error', 'message': str(e)}

print("=" * 100)
print("🔍 CLAUDECODECOIN - FULL SYSTEM CHECK")
print("=" * 100)
print()
print(f"Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ====================================================================================
# 1. DATABASE CHECK
# ====================================================================================
print("=" * 100)
print("1️⃣  DATABASE (Fiyat Verisi)")
print("=" * 100)
print()

def check_database():
    db_file = Path("data_output/binance_data.db")
    if not db_file.exists():
        return {'status': 'error', 'message': 'Database bulunamadı'}

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Toplam kayıt
    cursor.execute("SELECT COUNT(*) FROM klines")
    total = cursor.fetchone()[0]

    # Son kayıt zamanı
    cursor.execute("SELECT MAX(datetime) FROM klines")
    last_update = cursor.fetchone()[0]

    # Exchange başına coin sayısı
    cursor.execute("""
        SELECT exchange, COUNT(DISTINCT symbol)
        FROM klines
        GROUP BY exchange
    """)
    exchanges = dict(cursor.fetchall())

    conn.close()

    binance_count = exchanges.get('binance', 0)
    gateio_count = exchanges.get('gate.io', 0)

    if total == 0:
        return {'status': 'error', 'message': 'Database boş'}

    return {
        'status': 'ok',
        'details': f"{total:,} kayıt, Binance: {binance_count}, Gate.io: {gateio_count}, Son: {last_update}",
        'binance_count': binance_count,
        'gateio_count': gateio_count,
        'last_update': last_update
    }

db_result = check_component("Database", check_database)

# ====================================================================================
# 2. COLLECTORS CHECK
# ====================================================================================
print()
print("=" * 100)
print("2️⃣  COLLECTORS (Veri Toplama)")
print("=" * 100)
print()

def check_collectors():
    db_file = Path("data_output/binance_data.db")
    if not db_file.exists():
        return {'status': 'error', 'message': 'Database yok'}

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Son 5 dakikada aktif coinler
    five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT exchange, COUNT(DISTINCT symbol)
        FROM klines
        WHERE datetime >= ?
        GROUP BY exchange
    """, (five_mins_ago,))

    active = dict(cursor.fetchall())
    conn.close()

    binance_active = active.get('binance', 0)
    gateio_active = active.get('gate.io', 0)

    binance_expected = len(BINANCE_SYMBOLS)
    gateio_expected = len(GATEIO_SYMBOLS)

    if binance_active == 0 and gateio_active == 0:
        return {'status': 'error', 'message': 'Son 5 dakikada veri toplanmamış - Collectors çalışmıyor!'}

    if binance_active < binance_expected * 0.5 or gateio_active < gateio_expected * 0.5:
        return {
            'status': 'warning',
            'message': f'Bazı coinler eksik: Binance {binance_active}/{binance_expected}, Gate.io {gateio_active}/{gateio_expected}'
        }

    return {
        'status': 'ok',
        'details': f'Binance: {binance_active}/{binance_expected}, Gate.io: {gateio_active}/{gateio_expected}'
    }

collectors_result = check_component("Collectors", check_collectors)

# ====================================================================================
# 3. PUMP SCANNER CHECK
# ====================================================================================
print()
print("=" * 100)
print("3️⃣  PUMP SCANNER (Sinyal Üretimi)")
print("=" * 100)
print()

def check_pump_scanner():
    today = datetime.now().strftime("%Y%m%d")
    alert_file = Path("pump_alerts") / f"pump_alerts_{today}.json"

    if not alert_file.exists():
        return {'status': 'warning', 'message': 'Bugün için alert dosyası yok'}

    with open(alert_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    alerts = data if isinstance(data, list) else data.get('alerts', [])

    if len(alerts) == 0:
        return {'status': 'warning', 'message': 'Alert yok (sinyal üretilmedi)'}

    # Son 10 dakika
    ten_mins_ago = datetime.now() - timedelta(minutes=10)
    recent = [
        a for a in alerts
        if datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) > ten_mins_ago
    ]

    return {
        'status': 'ok',
        'details': f'{len(alerts)} toplam alert, son 10 dakika: {len(recent)}'
    }

pump_result = check_component("Pump Scanner", check_pump_scanner)

# ====================================================================================
# 4. PAPER TRADING CHECK
# ====================================================================================
print()
print("=" * 100)
print("4️⃣  PAPER TRADING (Pozisyon Yönetimi)")
print("=" * 100)
print()

def check_paper_trading():
    state_file = Path("Phase7_PaperTrading/paper_trading_state.json")

    if not state_file.exists():
        return {'status': 'warning', 'message': 'State dosyası yok - Henüz pozisyon açılmadı'}

    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    balance = state.get('balance', 10000)
    positions = state.get('positions', [])
    trades = state.get('trade_history', [])

    if len(positions) == 0 and len(trades) == 0:
        return {'status': 'warning', 'message': 'Hiç pozisyon açılmamış'}

    return {
        'status': 'ok',
        'details': f'{len(positions)} açık pozisyon, {len(trades)} tamamlanmış işlem, Bakiye: ${balance:,.2f}'
    }

paper_result = check_component("Paper Trading", check_paper_trading)

# ====================================================================================
# 5. SUMMARY & DIAGNOSIS
# ====================================================================================
print()
print("=" * 100)
print("📊 ÖZET & TANI")
print("=" * 100)
print()

all_ok = all([
    db_result.get('status') == 'ok',
    collectors_result.get('status') == 'ok',
    pump_result.get('status') == 'ok',
    paper_result.get('status') == 'ok'
])

if all_ok:
    print("✅ TÜM SİSTEM ÇALIŞIYOR!")
    print()
    print("Her şey normal. Sistem pozisyon açıp kapatabilir.")
else:
    print("⚠️  SORUNLAR TESPİT EDİLDİ")
    print()

    # Tanı ve çözümler
    if db_result.get('status') == 'error':
        print("❌ DATABASE SORUNU:")
        print("   - Collectors hiç çalışmamış")
        print("   - ÇÖZÜM: START_ALL_SYSTEMS_MULTI_COIN.bat çalıştır")
        print()

    if collectors_result.get('status') in ['error', 'warning']:
        print("❌ COLLECTORS SORUNU:")
        print("   - Bazı coinler için veri toplanmıyor")
        print("   - ÇÖZÜM: Collector pencereleri çalışıyor mu kontrol et")
        print("   - ÇÖZÜM: Yeniden başlat ve coin sayısını doğrula (169 Binance, 161 Gate.io)")
        print()

    if pump_result.get('status') in ['error', 'warning']:
        print("⚠️  PUMP SCANNER SORUNU:")
        print("   - Sinyal üretilmiyor veya çok az sinyal var")
        print("   - Bu NORMAL olabilir (piyasa sakin)")
        print("   - Threshold ayarları düşürülebilir")
        print()

    if paper_result.get('status') in ['error', 'warning']:
        print("⚠️  PAPER TRADING SORUNU:")
        print("   - Pozisyon açılmıyor")
        print()
        print("   Olası nedenler:")
        print("   1. Fiyat verisi yok → Collectors'ı kontrol et")
        print("   2. Alert yok → Pump Scanner'ı kontrol et")
        print("   3. Filtreler çok sıkı → Config'i kontrol et")
        print()

print("=" * 100)
print()

# Detaylı öneriler
print("📋 SONRAKI ADIMLAR:")
print()

if paper_result.get('status') == 'warning' and collectors_result.get('status') == 'ok' and pump_result.get('status') == 'ok':
    print("Collectors ve Pump Scanner çalışıyor ama Paper Trading pozisyon açmıyor.")
    print()
    print("Kontrol et:")
    print("  1. python CHECK_PAPER_TRADING_STATUS.py")
    print("     → Detaylı pozisyon durumu")
    print()
    print("  2. python CHECK_PUMP_ALERTS.py")
    print("     → Hangi coinler için sinyal var?")
    print("     → Bu coinler için fiyat verisi var mı?")
    print()
    print("  3. Get-Content logs\\paper_trading.log -Tail 50")
    print("     → Paper Trading ne diyor?")
    print()
elif all_ok:
    print("Sistem normal çalışıyor!")
    print()
    print("Dashboard'u açarak pozisyonları izle:")
    print("  START_DASHBOARD.bat")
    print("  → http://localhost:5000")
    print()
else:
    print("Önce temel bileşenleri düzelt:")
    print("  1. Collectors'ı başlat/restart et")
    print("  2. 5 dakika bekle")
    print("  3. Bu scripti tekrar çalıştır")
    print()

print("=" * 100)
