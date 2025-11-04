"""
ClaudeCodeCoin - Gate.io System Status Checker
Sadece Gate.io collector durumunu kontrol eder
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

# Renkli output için
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_database():
    """Gate.io veritabanı durumunu kontrol et"""
    db_path = Path("data_output/binance_data.db")

    if not db_path.exists():
        print_error("Database dosyası bulunamadı!")
        print_info("  Çözüm: START_GATEIO_ONLY.bat çalıştırın")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Gate.io verilerini kontrol et
        cursor.execute("""
            SELECT COUNT(DISTINCT symbol),
                   COUNT(*),
                   MAX(datetime) as latest_time
            FROM klines
            WHERE exchange = 'gate.io'
        """)

        result = cursor.fetchone()
        unique_symbols, total_candles, latest_time = result

        if unique_symbols == 0:
            print_warning("Database boş - henüz veri toplanmamış")
            print_info("  Collector'ı başlatın: START_GATEIO_ONLY.bat")
            return False

        print_success(f"Database bağlantısı başarılı")
        print(f"  📊 Toplam coin: {unique_symbols}")
        print(f"  📈 Toplam candlestick: {total_candles:,}")
        print(f"  🕐 Son veri: {latest_time}")

        # Son 5 dakikada veri gelmiş mi?
        if latest_time:
            latest = datetime.fromisoformat(latest_time)
            now = datetime.now()
            diff = (now - latest).total_seconds()

            if diff < 300:  # 5 dakika
                print_success(f"Collector aktif - {diff:.0f} saniye önce veri geldi")
            else:
                print_warning(f"Son veri {diff/60:.0f} dakika önce - Collector durmuş olabilir")

        # Coin başına veri sayısı
        cursor.execute("""
            SELECT symbol, COUNT(*) as candle_count
            FROM klines
            WHERE exchange = 'gate.io'
            GROUP BY symbol
            ORDER BY candle_count DESC
            LIMIT 10
        """)

        print("\n📊 En çok veri toplanan ilk 10 coin:")
        for symbol, count in cursor.fetchall():
            print(f"  {symbol}: {count} candlestick")

        conn.close()
        return True

    except Exception as e:
        print_error(f"Database hatası: {e}")
        return False

def check_logs():
    """Log dosyalarını kontrol et"""
    log_file = Path("logs/gateio_collector_1000coins.log")

    if not log_file.exists():
        print_warning("Log dosyası bulunamadı")
        print_info("  Collector henüz başlatılmamış")
        return

    try:
        # Son 10 satırı oku
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-10:] if len(lines) >= 10 else lines

        print_success(f"Log dosyası bulundu: {log_file}")
        print("\n📄 Son 10 log satırı:")
        for line in last_lines:
            print(f"  {line.rstrip()}")

    except Exception as e:
        print_error(f"Log okuma hatası: {e}")

def check_config():
    """Gate.io konfigürasyonu kontrol et"""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path('config')))
        from trading_pairs_1000coins import get_gateio_symbols

        symbols = get_gateio_symbols()
        print_success(f"Gate.io konfigürasyonu yüklendi")
        print(f"  📊 İzlenecek coin sayısı: {len(symbols)}")
        print(f"  🔹 İlk 5: {', '.join(symbols[:5])}")
        print(f"  🔹 Son 5: {', '.join(symbols[-5:])}")

    except Exception as e:
        print_error(f"Konfig hatası: {e}")

def main():
    print_header("🔍 GATE.IO SYSTEM STATUS CHECK")

    print(f"Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print_header("1️⃣  KONFIGÜRASYON")
    check_config()

    print_header("2️⃣  DATABASE (Veri Toplama)")
    check_database()

    print_header("3️⃣  LOG DOSYALARI")
    check_logs()

    print_header("📋 ÖZET")

    # Kısa özet
    db_path = Path("data_output/binance_data.db")
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM klines WHERE exchange = 'gate.io'")
        count = cursor.fetchone()[0]
        conn.close()

        if count > 0:
            print_success(f"Sistem çalışıyor - {count} coin izleniyor")
        else:
            print_warning("Database var ama veri yok - Collector'ı başlatın")
    else:
        print_warning("Sistem henüz başlatılmamış")
        print_info("  Başlatmak için: START_GATEIO_ONLY.bat")

    print(f"\n{Colors.CYAN}{'='*80}{Colors.END}\n")

if __name__ == "__main__":
    main()
