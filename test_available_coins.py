"""
Test: Hangi coinler için fiyat verisi var?
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Veritabanı yolu
db_path = Path("data_output/binance_data.db")

if not db_path.exists():
    print(f"❌ Veritabanı bulunamadı: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Son 30 dakikada veri olan coinleri bul
thirty_mins_ago = (datetime.now() - timedelta(minutes=30)).isoformat()

print("="*70)
print("📊 SON 30 DAKİKADA VERİ TOPLANAN COİNLER")
print("="*70)
print()

# Gate.io coinleri
cursor.execute("""
    SELECT DISTINCT symbol, COUNT(*) as count, MAX(datetime) as last_update
    FROM klines
    WHERE exchange = 'gate.io' AND datetime >= ?
    GROUP BY symbol
    ORDER BY symbol
""", (thirty_mins_ago,))

gateio_coins = cursor.fetchall()

print(f"🔵 Gate.io ({len(gateio_coins)} coin):")
for symbol, count, last_update in gateio_coins:
    print(f"   ✅ {symbol:20s} - {count:4d} kayıt - Son: {last_update}")

print()

# Binance coinleri
cursor.execute("""
    SELECT DISTINCT symbol, COUNT(*) as count, MAX(datetime) as last_update
    FROM klines
    WHERE exchange = 'binance' AND datetime >= ?
    GROUP BY symbol
    ORDER BY symbol
""", (thirty_mins_ago,))

binance_coins = cursor.fetchall()

print(f"🟡 Binance ({len(binance_coins)} coin):")
for symbol, count, last_update in binance_coins:
    print(f"   ✅ {symbol:20s} - {count:4d} kayıt - Son: {last_update}")

conn.close()

print()
print("="*70)
print(f"📈 TOPLAM: {len(gateio_coins) + len(binance_coins)} farklı coin")
print("="*70)

# Alert'lerde olan ama veritabanında olmayan coinleri kontrol et
import json

alert_file = Path("pump_alerts") / f"pump_alerts_{datetime.now().strftime('%Y%m%d')}.json"
if alert_file.exists():
    with open(alert_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            alerts = data
        else:
            alerts = data.get('alerts', [])

    # Son 10 dakikadaki alert'ler
    ten_mins_ago = datetime.now() - timedelta(minutes=10)
    recent_alerts = []
    for alert in alerts:
        alert_time = datetime.fromisoformat(alert['timestamp'])
        if alert_time >= ten_mins_ago:
            recent_alerts.append(alert)

    if recent_alerts:
        print()
        print("🚨 SON 10 DAKİKADAKİ ALERT'LER:")
        print("="*70)

        available_coins = {symbol for symbol, _, _ in gateio_coins + binance_coins}

        for alert in recent_alerts:
            symbol = alert['symbol']
            # Format dönüşümü (BTC_USDT vs BTCUSDT)
            symbol_underscore = symbol if '_' in symbol else symbol.replace('USDT', '_USDT')
            symbol_no_underscore = symbol.replace('_', '')

            has_data = symbol in available_coins or symbol_underscore in available_coins or symbol_no_underscore in available_coins

            status = "✅ VERİ VAR" if has_data else "❌ VERİ YOK"
            print(f"{status:15s} {symbol:20s} - Confidence: {alert['confidence']:.1f}% - Volume: {alert.get('volume_change_pct', 0):.0f}%")
