"""
CHECK PUMP ALERTS - Pump Scanner alert durumunu kontrol et
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

print("=" * 100)
print("🚨 PUMP ALERTS DURUM KONTROLU")
print("=" * 100)
print()

alerts_dir = Path("pump_alerts")

if not alerts_dir.exists():
    print("❌ pump_alerts KLASÖRÜ BULUNAMADI!")
    print()
    print("   Pump Scanner çalışmıyor olabilir.")
    print()
    exit(1)

# Bugünün dosyası
today = datetime.now().strftime("%Y%m%d")
today_file = alerts_dir / f"pump_alerts_{today}.json"

print(f"📅 Bugünün tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📄 Aranan dosya: {today_file}")
print()

if not today_file.exists():
    print("❌ BUGÜNÜN ALERT DOSYASI BULUNAMADI!")
    print()
    print("   Pump Scanner:")
    print("   - Çalışmıyor olabilir")
    print("   - Ya da henüz sinyal üretmedi")
    print()
    print("Klasördeki dosyalar:")
    for file in sorted(alerts_dir.glob("pump_alerts_*.json")):
        print(f"   {file.name}")
    print()
    exit(1)

print("✅ Bugünün alert dosyası bulundu")
print()

# Dosyayı oku
with open(today_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Alert formatını kontrol et
if isinstance(data, list):
    alerts = data
else:
    alerts = data.get('alerts', [])

print(f"📊 Toplam alert sayısı: {len(alerts)}")
print()

if len(alerts) == 0:
    print("❌ ALERT YOK!")
    print()
    print("   Pump Scanner çalışıyor ama henüz sinyal üretmedi.")
    print("   - Yeterli hacim artışı yok")
    print("   - Ya da threshold'lar çok yüksek")
    print()
    exit(0)

# Son X dakikadaki alertleri say
time_windows = [5, 10, 30, 60]

for window in time_windows:
    cutoff = datetime.now() - timedelta(minutes=window)
    recent = [
        alert for alert in alerts
        if datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00')) > cutoff
    ]
    print(f"⏰ Son {window:2d} dakika: {len(recent):3d} alert")

print()

# En son 10 alert'i göster
print("📋 SON 10 ALERT:")
print("-" * 100)

sorted_alerts = sorted(alerts, key=lambda x: x['timestamp'], reverse=True)

for i, alert in enumerate(sorted_alerts[:10], 1):
    symbol = alert['symbol']
    confidence = alert.get('confidence', 0)
    volume_change = alert.get('volume_change_pct', 0)
    timestamp = alert['timestamp'][:19]
    exchange = alert.get('exchange', 'gate.io')

    if volume_change == float('inf') or volume_change == '∞':
        volume_str = "∞"
    else:
        volume_str = f"{volume_change:.0f}%"

    print(f"{i:2d}. {timestamp} | {exchange:8s} | {symbol:15s} | Conf: {confidence:3.0f}% | Vol: {volume_str}")

print()

# Exchange dağılımı
exchanges = {}
for alert in alerts:
    exchange = alert.get('exchange', 'gate.io')
    exchanges[exchange] = exchanges.get(exchange, 0) + 1

print("📊 EXCHANGE DAĞILIMI:")
for exchange, count in sorted(exchanges.items(), key=lambda x: x[1], reverse=True):
    print(f"   {exchange:10s}: {count:3d} alert")

print()

# Confidence dağılımı
high_conf = len([a for a in alerts if a.get('confidence', 0) >= 80])
med_conf = len([a for a in alerts if 50 <= a.get('confidence', 0) < 80])
low_conf = len([a for a in alerts if a.get('confidence', 0) < 50])

print("📊 CONFIDENCE DAĞILIMI:")
print(f"   Yüksek (≥80%):    {high_conf:3d} alert")
print(f"   Orta (50-80%):    {med_conf:3d} alert")
print(f"   Düşük (<50%):     {low_conf:3d} alert")

print()

# Son 10 dakikadaki alert'lerde fiyat verisi kontrolü
print("=" * 100)
print("💾 FİYAT VERİSİ KONTROLU (Son 10 dakika)")
print("=" * 100)
print()

ten_mins_ago = datetime.now() - timedelta(minutes=10)
recent_alerts = [
    alert for alert in alerts
    if datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00')) > ten_mins_ago
]

print(f"Son 10 dakikada {len(recent_alerts)} alert var")
print()

if len(recent_alerts) > 0:
    # Database'e bağlan
    import sqlite3
    db_file = Path("data_output/binance_data.db")

    if not db_file.exists():
        print("❌ DATABASE BULUNAMADI!")
        print("   Collectors çalışmıyor!")
    else:
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        # Son 10 dakikadaki alertler için fiyat verisi var mı kontrol et
        with_data = []
        without_data = []

        for alert in recent_alerts[:20]:  # İlk 20'sini kontrol et
            symbol = alert['symbol']
            exchange = alert.get('exchange', 'gate.io')

            # Symbol formatını düzenle
            if exchange == "gate.io" and "_" not in symbol:
                db_symbol = symbol.replace("USDT", "_USDT")
            elif exchange == "binance" and "_" in symbol:
                db_symbol = symbol.replace("_", "")
            else:
                db_symbol = symbol

            # Son 10 dakika içinde veri var mı?
            ten_mins_ago_str = (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                SELECT COUNT(*) FROM klines
                WHERE symbol = ? AND exchange = ? AND datetime >= ?
            """, (db_symbol, exchange, ten_mins_ago_str))

            result = cursor.fetchone()

            if result and result[0] > 0:
                with_data.append(symbol)
            else:
                without_data.append(symbol)

        conn.close()

        print(f"✅ Fiyat verisi VAR:    {len(with_data):2d} alert")
        print(f"❌ Fiyat verisi YOK:    {len(without_data):2d} alert")
        print()

        if with_data:
            print("Fiyat verisi olan coinler (işlem yapılabilir):")
            for coin in with_data[:10]:
                print(f"   ✅ {coin}")
            if len(with_data) > 10:
                print(f"   ... ve {len(with_data) - 10} tane daha")
        print()

        if without_data:
            print("Fiyat verisi olmayan coinler (atlanacak):")
            for coin in without_data[:10]:
                print(f"   ❌ {coin}")
            if len(without_data) > 10:
                print(f"   ... ve {len(without_data) - 10} tane daha")

print()
print("=" * 100)
