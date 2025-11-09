"""
ClaudeCodeCoin - Real-Time System Monitor
Sistem durumunu her 30 saniyede bir günceller ve gösterir
"""

import os
import sys
import time
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

# Terminal renkleri
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def clear_screen():
    """Ekranı temizle"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Başlık yazdır"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'ClaudeCodeCoin - REAL-TIME SYSTEM MONITOR'.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")
    print(f"{Colors.WHITE}Son Güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.WHITE}Otomatik Güncelleme: Her 30 saniye{Colors.END}\n")

def check_processes():
    """Çalışan process'leri kontrol et"""
    print(f"{Colors.BOLD}{Colors.BLUE}[1] ÇALIŞAN SERVİSLER{Colors.END}")
    print(f"{Colors.BLUE}{'-'*80}{Colors.END}")

    try:
        if sys.platform == 'win32':
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            output = result.stdout.lower()

            # Python process sayısı
            python_count = output.count('python.exe')
            streamlit_running = 'streamlit' in output

            if python_count >= 2:
                print(f"{Colors.GREEN}✓ Scanner ve Trading Engine çalışıyor ({python_count} Python process){Colors.END}")
            elif python_count == 1:
                print(f"{Colors.YELLOW}⚠ Sadece 1 Python process çalışıyor{Colors.END}")
            else:
                print(f"{Colors.RED}✗ Python process bulunamadı!{Colors.END}")

            if streamlit_running:
                print(f"{Colors.GREEN}✓ Dashboard (Streamlit) çalışıyor{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠ Dashboard çalışmıyor{Colors.END}")
        else:
            # Linux için
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            output = result.stdout.lower()

            if 'scanner' in output:
                print(f"{Colors.GREEN}✓ Scanner çalışıyor{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠ Scanner çalışmıyor{Colors.END}")

            if 'trading' in output:
                print(f"{Colors.GREEN}✓ Trading Engine çalışıyor{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠ Trading Engine çalışmıyor{Colors.END}")

    except Exception as e:
        print(f"{Colors.RED}✗ Process kontrolü başarısız: {e}{Colors.END}")

def check_data():
    """Veri durumunu kontrol et"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[2] VERİ DURUMU{Colors.END}")
    print(f"{Colors.BLUE}{'-'*80}{Colors.END}")

    try:
        db_path = Path("data_output/binance_data.db")
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Son 5 dakikadaki veri
            five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("SELECT COUNT(*) FROM klines WHERE datetime >= ?", (five_mins_ago,))
            recent_count = cursor.fetchone()[0]

            # Toplam coin sayısı
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM klines")
            total_symbols = cursor.fetchone()[0]

            if recent_count > 0:
                print(f"{Colors.GREEN}✓ Son 5 dakikada {recent_count} yeni veri{Colors.END}")
                print(f"{Colors.WHITE}  Toplam {total_symbols} coin takip ediliyor{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠ Son 5 dakikada yeni veri yok{Colors.END}")
                print(f"{Colors.WHITE}  Toplam {total_symbols} coin veritabanında{Colors.END}")

            conn.close()
        else:
            print(f"{Colors.RED}✗ Veritabanı bulunamadı{Colors.END}")

    except Exception as e:
        print(f"{Colors.RED}✗ Veri kontrolü başarısız: {e}{Colors.END}")

def check_alerts():
    """Alert durumunu kontrol et"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[3] PUMP ALERTS{Colors.END}")
    print(f"{Colors.BLUE}{'-'*80}{Colors.END}")

    try:
        today = datetime.now().strftime("%Y%m%d")
        alert_file = Path("pump_alerts") / f"pump_alerts_{today}.json"

        if alert_file.exists():
            with open(alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                alerts = data if isinstance(data, list) else data.get('alerts', [])

            # Son 10 dakikadaki alert'ler
            ten_mins_ago = datetime.now() - timedelta(minutes=10)
            recent_alerts = [a for a in alerts if datetime.fromisoformat(a['timestamp']) >= ten_mins_ago]

            print(f"{Colors.GREEN}✓ Bugün {len(alerts)} toplam alert{Colors.END}")
            print(f"{Colors.WHITE}  Son 10 dakikada {len(recent_alerts)} alert{Colors.END}")

            # Son 3 alert'i göster
            if recent_alerts:
                print(f"\n{Colors.CYAN}  Son Alert'ler:{Colors.END}")
                for alert in recent_alerts[-3:]:
                    time_str = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')
                    print(f"{Colors.WHITE}    • {time_str} - {alert['symbol']}: " +
                          f"Conf {alert['confidence']:.0f}%, Vol {alert.get('volume_change_pct', 0):.0f}%{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ Bugün henüz alert yok{Colors.END}")

    except Exception as e:
        print(f"{Colors.RED}✗ Alert kontrolü başarısız: {e}{Colors.END}")

def check_positions():
    """Pozisyon durumunu kontrol et"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[4] PAPER TRADING{Colors.END}")
    print(f"{Colors.BLUE}{'-'*80}{Colors.END}")

    try:
        db_path = Path("Phase7_PaperTrading/data_output/paper_trading.db")

        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Son bakiye
            cursor.execute("SELECT balance, total_pnl FROM balance_history ORDER BY timestamp DESC LIMIT 1")
            balance_data = cursor.fetchone()

            if balance_data:
                balance, total_pnl = balance_data
                pnl_percent = (total_pnl / 10000) * 100

                color = Colors.GREEN if total_pnl >= 0 else Colors.RED
                print(f"{color}💰 Bakiye: ${balance:,.2f} | P&L: ${total_pnl:+,.2f} ({pnl_percent:+.2f}%){Colors.END}")

            # Açık pozisyonlar
            cursor.execute("SELECT COUNT(*) FROM positions WHERE status='OPEN'")
            open_count = cursor.fetchone()[0]

            if open_count > 0:
                cursor.execute("""
                    SELECT symbol, entry_price, quantity, confidence, entry_time
                    FROM positions
                    WHERE status='OPEN'
                    ORDER BY entry_time DESC
                    LIMIT 5
                """)

                print(f"\n{Colors.CYAN}  📊 Açık Pozisyonlar ({open_count}):{Colors.END}")
                for symbol, entry, qty, conf, entry_time in cursor.fetchall():
                    value = entry * qty
                    print(f"{Colors.WHITE}    • {symbol}: ${entry:.4f} x {qty:.2f} = ${value:.2f} | Conf: {conf:.0f}%{Colors.END}")
            else:
                print(f"{Colors.WHITE}  Henüz açık pozisyon yok{Colors.END}")

            # Trade istatistikleri
            cursor.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END),
                       AVG(pnl)
                FROM positions
                WHERE status='CLOSED'
            """)

            stats = cursor.fetchone()
            if stats and stats[0] > 0:
                total, wins, avg_pnl = stats
                win_rate = (wins / total * 100) if total > 0 else 0
                print(f"\n{Colors.CYAN}  📈 İstatistikler:{Colors.END}")
                print(f"{Colors.WHITE}    Toplam Trade: {total} | Win Rate: {win_rate:.1f}% | Avg P&L: ${avg_pnl:.2f}{Colors.END}")

            conn.close()
        else:
            print(f"{Colors.YELLOW}⚠ Paper trading henüz başlamadı{Colors.END}")

    except Exception as e:
        print(f"{Colors.RED}✗ Pozisyon kontrolü başarısız: {e}{Colors.END}")

def check_logs():
    """Log dosyalarını kontrol et"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[5] LOG DURUMU{Colors.END}")
    print(f"{Colors.BLUE}{'-'*80}{Colors.END}")

    try:
        logs_dir = Path("logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))

            for log_file in log_files:
                size_kb = log_file.stat().st_size / 1024
                modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                age = datetime.now() - modified

                age_str = f"{age.seconds//60} dk önce" if age.seconds < 3600 else f"{age.seconds//3600} saat önce"
                print(f"{Colors.WHITE}  • {log_file.name}: {size_kb:.1f} KB | Güncelleme: {age_str}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ Logs klasörü bulunamadı{Colors.END}")

    except Exception as e:
        print(f"{Colors.RED}✗ Log kontrolü başarısız: {e}{Colors.END}")

def print_footer():
    """Footer yazdır"""
    print(f"\n{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.YELLOW}⌨️  CTRL+C ile durdurun | Dashboard: http://localhost:8501{Colors.END}")
    print(f"{Colors.CYAN}{'='*80}{Colors.END}\n")

def main():
    """Ana döngü"""
    iteration = 0

    try:
        while True:
            iteration += 1
            clear_screen()
            print_header()

            # Tüm kontrolleri çalıştır
            check_processes()
            check_data()
            check_alerts()
            check_positions()
            check_logs()

            print_footer()

            # 30 saniye bekle
            print(f"{Colors.WHITE}Sonraki güncelleme 30 saniye sonra... (#{iteration}){Colors.END}")
            time.sleep(30)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitor durduruldu.{Colors.END}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
