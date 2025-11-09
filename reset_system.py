"""
ClaudeCodeCoin System Reset
============================
Sistemi sıfırlar:
- Paper trading state ($10,000 başlangıç)
- Pump alerts
- Database (opsiyonel)
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent

def reset_paper_trading():
    """Paper trading state'i sıfırla"""
    state_file = project_root / "Phase7_PaperTrading" / "paper_trading_state.json"

    if state_file.exists():
        # Backup oluştur
        backup_file = state_file.parent / f"paper_trading_state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.rename(state_file, backup_file)
        print(f"✅ Eski state yedeklendi: {backup_file.name}")

    # Yeni state oluştur
    initial_state = {
        "balance": 10000.0,
        "open_positions": {},
        "closed_trades": [],
        "total_pnl": 0.0,
        "winning_trades": 0,
        "losing_trades": 0,
        "created_at": datetime.now().isoformat()
    }

    with open(state_file, 'w') as f:
        json.dump(initial_state, f, indent=2)

    print("✅ Paper trading state sıfırlandı ($10,000)")

def clear_pump_alerts():
    """Pump alerts'i temizle"""
    alerts_dir = project_root / "pump_alerts"

    if not alerts_dir.exists():
        print("ℹ️  Pump alerts klasörü bulunamadı")
        return

    count = 0
    for alert_file in alerts_dir.glob("pump_alerts_*.json"):
        # Backup oluştur
        backup_file = alert_file.parent / f"backup_{alert_file.name}"
        os.rename(alert_file, backup_file)
        count += 1

    if count > 0:
        print(f"✅ {count} pump alert dosyası yedeklendi")
    else:
        print("ℹ️  Temizlenecek pump alert yok")

def clear_database(clear_all=False):
    """Database'i temizle"""
    db_file = project_root / "data_output" / "binance_data.db"

    if not db_file.exists():
        print("ℹ️  Database bulunamadı")
        return

    if clear_all:
        # Tüm database'i sil
        backup_file = db_file.parent / f"binance_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.rename(db_file, backup_file)
        print(f"✅ Database yedeklendi: {backup_file.name}")
        print("✅ Yeni database oluşturulacak (collector start'ta)")
    else:
        # Sadece eski verileri temizle (24 saatten eski)
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM klines")
        total_before = cursor.fetchone()[0]

        # 24 saatten eski verileri sil
        cutoff_time = datetime.now().timestamp() - (24 * 3600)
        cursor.execute("DELETE FROM klines WHERE timestamp < ?", (cutoff_time,))

        cursor.execute("SELECT COUNT(*) FROM klines")
        total_after = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        deleted = total_before - total_after
        print(f"✅ {deleted} eski kayıt silindi (24+ saat)")
        print(f"ℹ️  Kalan kayıt: {total_after}")

def main():
    print()
    print("="*70)
    print("🔄 ClaudeCodeCoin System Reset")
    print("="*70)
    print()

    # 1. Paper trading state reset
    print("1️⃣  Paper Trading State...")
    reset_paper_trading()
    print()

    # 2. Pump alerts clear
    print("2️⃣  Pump Alerts...")
    clear_pump_alerts()
    print()

    # 3. Database cleanup
    print("3️⃣  Database Cleanup...")
    response = input("Database'i temizle? (y=tümü sil, n=eski verileri sil, s=skip): ").lower()

    if response == 'y':
        clear_database(clear_all=True)
    elif response == 'n':
        clear_database(clear_all=False)
    else:
        print("ℹ️  Database dokunulmadı")

    print()
    print("="*70)
    print("✅ SİSTEM SIFIRLANDI!")
    print("="*70)
    print()
    print("📋 Sonraki adımlar:")
    print("   1. python run_live_gateio_collector.py  # Data toplayıcı")
    print("   2. python run_live_pump_scanner.py      # Pump detector")
    print("   3. python run_live_paper_trading.py     # Paper trading")
    print("   4. streamlit run dashboard.py           # Dashboard")
    print()

if __name__ == "__main__":
    main()
