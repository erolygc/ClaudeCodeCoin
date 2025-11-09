"""
ClaudeCodeCoin - Sistem Sağlık Kontrolü
Tüm sistemin durumunu kontrol eder ve rapor oluşturur
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def check_database():
    """Veritabanı durumunu kontrol et"""
    print("\n" + "="*70)
    print("[1] VERITABANI KONTROLU")
    print("="*70)

    try:
        db_path = Path("data_output/binance_data.db")
        if not db_path.exists():
            print("[ERROR] Veritabani dosyasi bulunamadi!")
            return False

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Toplam kayıt
        cursor.execute("SELECT COUNT(*) FROM klines")
        total = cursor.fetchone()[0]
        print(f"[OK] Toplam candlestick: {total:,}")

        # Exchange bazında
        cursor.execute("SELECT exchange, COUNT(*) FROM klines GROUP BY exchange")
        for exchange, count in cursor.fetchall():
            print(f"     {exchange}: {count:,}")

        # Unique coinler
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM klines WHERE exchange='gate.io'")
        unique = cursor.fetchone()[0]
        print(f"[OK] Unique Gate.io coinler: {unique}")

        # Son 5 dakika
        five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT COUNT(*) FROM klines WHERE datetime >= ?", (five_mins_ago,))
        recent = cursor.fetchone()[0]
        print(f"[OK] Son 5 dakikadaki kayit: {recent:,}")

        if recent > 0:
            print("[STATUS] Collector AKTIF - Veri toplanıyor ✅")
        else:
            print("[WARN] Collector durdurulmuş olabilir veya veri gelmiyor")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERROR] Veritabani hatasi: {e}")
        return False

def check_pump_alerts():
    """Pump alert durumunu kontrol et"""
    print("\n" + "="*70)
    print("[2] PUMP SCANNER KONTROLU")
    print("="*70)

    try:
        alerts_dir = Path("pump_alerts")
        if not alerts_dir.exists():
            print("[WARN] pump_alerts klasoru bulunamadi")
            return False

        # Bugünkü alert dosyası
        today = datetime.now().strftime("%Y%m%d")
        alert_file = alerts_dir / f"pump_alerts_{today}.json"

        if not alert_file.exists():
            print(f"[INFO] Bugun henuz alert yok: {alert_file.name}")
            return True

        with open(alert_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            alerts = data if isinstance(data, list) else data.get('alerts', [])

        print(f"[OK] Bugunki alert sayisi: {len(alerts)}")

        # Son 10 dakikadaki alertler
        ten_mins_ago = datetime.now() - timedelta(minutes=10)
        recent_alerts = [a for a in alerts if datetime.fromisoformat(a['timestamp']) >= ten_mins_ago]

        print(f"[OK] Son 10 dakikadaki alert: {len(recent_alerts)}")

        if recent_alerts:
            print("\n[RECENT ALERTS]")
            for alert in recent_alerts[-5:]:  # Son 5 tanesini göster
                print(f"  - {alert['symbol']}: Confidence {alert['confidence']:.0f}%, Volume {alert.get('volume_change_pct', 0):.0f}%")

        return True

    except Exception as e:
        print(f"[ERROR] Alert kontrolu hatasi: {e}")
        return False

def check_paper_trading():
    """Paper trading durumunu kontrol et"""
    print("\n" + "="*70)
    print("[3] PAPER TRADING KONTROLU")
    print("="*70)

    try:
        db_path = Path("Phase7_PaperTrading/data_output/paper_trading.db")
        if not db_path.exists():
            print("[INFO] Paper trading henuz baslatilmamis")
            return True

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Açık pozisyonlar
        cursor.execute("SELECT COUNT(*) FROM positions WHERE status='OPEN'")
        open_pos = cursor.fetchone()[0]
        print(f"[OK] Acik pozisyon sayisi: {open_pos}")

        # Toplam işlemler
        cursor.execute("SELECT COUNT(*) FROM positions")
        total_trades = cursor.fetchone()[0]
        print(f"[OK] Toplam islem sayisi: {total_trades}")

        # Son bakiye
        cursor.execute("SELECT balance FROM balance_history ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            balance = result[0]
            print(f"[OK] Guncel bakiye: ${balance:.2f}")

        # Açık pozisyonların detayı
        if open_pos > 0:
            cursor.execute("""
                SELECT symbol, entry_price, quantity, confidence, entry_time
                FROM positions
                WHERE status='OPEN'
                ORDER BY entry_time DESC
            """)
            print("\n[OPEN POSITIONS]")
            for symbol, entry, qty, conf, entry_time in cursor.fetchall():
                value = entry * qty
                print(f"  - {symbol}: ${entry:.4f} x {qty:.2f} = ${value:.2f} (Conf: {conf:.0f}%)")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERROR] Paper trading kontrolu hatasi: {e}")
        return False

def check_logs():
    """Log dosyalarını kontrol et"""
    print("\n" + "="*70)
    print("[4] LOG DOSYALARI KONTROLU")
    print("="*70)

    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            print("[WARN] logs klasoru bulunamadi")
            return False

        log_files = list(logs_dir.glob("*.log"))
        print(f"[OK] Log dosyasi sayisi: {len(log_files)}")

        for log_file in log_files:
            size_mb = log_file.stat().st_size / (1024 * 1024)
            print(f"  - {log_file.name}: {size_mb:.2f} MB")

        return True

    except Exception as e:
        print(f"[ERROR] Log kontrolu hatasi: {e}")
        return False

def check_config():
    """Config dosyalarını kontrol et"""
    print("\n" + "="*70)
    print("[5] CONFIG KONTROLU")
    print("="*70)

    try:
        config_files = [
            "config/secrets.env",
            "config/gateio_1000coins.json"
        ]

        for config_file in config_files:
            path = Path(config_file)
            if path.exists():
                print(f"[OK] {config_file} mevcut")
            else:
                print(f"[WARN] {config_file} bulunamadi")

        # Gate.io coin sayısı
        gateio_config = Path("config/gateio_1000coins.json")
        if gateio_config.exists():
            with open(gateio_config, 'r') as f:
                data = json.load(f)
                symbols = data.get('symbols', [])
                print(f"[OK] Gate.io sembol sayisi: {len(symbols)}")

        return True

    except Exception as e:
        print(f"[ERROR] Config kontrolu hatasi: {e}")
        return False

def main():
    print("\n" + "="*70)
    print(" CLAUDECODECOIN - SISTEM SAGLIK KONTROLU")
    print("="*70)
    print(f" Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    results = {
        'database': check_database(),
        'pump_alerts': check_pump_alerts(),
        'paper_trading': check_paper_trading(),
        'logs': check_logs(),
        'config': check_config()
    }

    print("\n" + "="*70)
    print(" SONUC OZETI")
    print("="*70)

    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f" {status_icon} {component.upper()}: {'OK' if status else 'SORUNLU'}")

    print("="*70)

    all_ok = all(results.values())
    if all_ok:
        print("\n[SUCCESS] Tum sistemler calisiyor! ✅")
    else:
        print("\n[WARNING] Bazi sistemlerde sorun var ⚠️")

    print("\n")

if __name__ == "__main__":
    main()
