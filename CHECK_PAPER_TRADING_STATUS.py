"""
CHECK PAPER TRADING STATUS - Paper Trading pozisyon durumunu kontrol et
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

print("=" * 100)
print("🔍 PAPER TRADING DURUM KONTROLU")
print("=" * 100)
print()

# 1. State dosyasını kontrol et
state_file = Path("Phase7_PaperTrading/paper_trading_state.json")

if not state_file.exists():
    print("❌ PAPER TRADING STATE DOSYASI BULUNAMADI!")
    print(f"   Dosya: {state_file}")
    print()
    print("   Bu şu anlama gelir:")
    print("   - Paper Trading hiç pozisyon açmadı")
    print("   - Ya da state dosyası silinmiş")
    print()
else:
    print("✅ State dosyası bulundu")
    print()

    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    balance = state.get('balance', 10000)
    positions = state.get('positions', [])
    trade_history = state.get('trade_history', [])

    print(f"💰 Bakiye:           ${balance:,.2f}")
    print(f"📊 Açık Pozisyon:    {len(positions)}")
    print(f"✅ Toplam İşlem:     {len(trade_history)}")
    print()

    if positions:
        print("📍 AÇIK POZİSYONLAR:")
        print("-" * 100)
        for i, pos in enumerate(positions, 1):
            symbol = pos['symbol']
            entry_price = pos['entry_price']
            quantity = pos['quantity']
            position_value = entry_price * quantity
            stop_loss = pos['stop_loss']
            take_profit = pos['take_profit']
            entry_time = pos['entry_time']

            print(f"{i}. {symbol}")
            print(f"   Entry Price:  ${entry_price:.6f}")
            print(f"   Quantity:     {quantity:.4f}")
            print(f"   Position Val: ${position_value:.2f}")
            print(f"   Stop Loss:    ${stop_loss:.6f} (-5%)")
            print(f"   Take Profit:  ${take_profit:.6f}")
            print(f"   Entry Time:   {entry_time}")
            print()
    else:
        print("❌ AÇIK POZİSYON YOK!")
        print()
        print("   Olası nedenler:")
        print("   - Paper Trading yeni başladı, henüz sinyal gelmedi")
        print("   - Tüm pozisyonlar stop loss/take profit ile kapandı")
        print("   - Fiyat verisi eksik")
        print()

    if trade_history:
        print("📊 KAPALI İŞLEMLER:")
        print("-" * 100)

        winning_trades = [t for t in trade_history if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trade_history if t.get('pnl', 0) <= 0]

        total_pnl = sum(t.get('pnl', 0) for t in trade_history)

        print(f"Toplam:     {len(trade_history)} işlem")
        print(f"Kazanan:    {len(winning_trades)} işlem (Win Rate: {len(winning_trades)/len(trade_history)*100:.1f}%)")
        print(f"Kaybeden:   {len(losing_trades)} işlem")
        print(f"Toplam P&L: ${total_pnl:.2f}")
        print()

        print("Son 5 işlem:")
        for trade in trade_history[-5:]:
            symbol = trade['symbol']
            pnl = trade.get('pnl', 0)
            pnl_pct = trade.get('pnl_percent', 0)
            exit_reason = trade.get('exit_reason', 'Unknown')

            status = "✅" if pnl > 0 else "❌"
            print(f"   {status} {symbol}: ${pnl:+.2f} ({pnl_pct:+.2f}%) - {exit_reason}")

# 2. Paper trades database'i kontrol et
print()
print("=" * 100)
print("💾 DATABASE KONTROLU")
print("=" * 100)
print()

db_file = Path("data_output/paper_trades.db")

if not db_file.exists():
    print("❌ PAPER TRADES DATABASE BULUNAMADI!")
    print(f"   Dosya: {db_file}")
    print()
    print("   Database oluşturulacak ilk pozisyon açıldığında.")
    print()
else:
    print("✅ Paper trades database bulundu")
    print()

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Tabloları kontrol et
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print(f"Tablolar: {', '.join([t[0] for t in tables])}")
    print()

    # Trades tablosu varsa
    if ('trades',) in tables:
        cursor.execute("SELECT COUNT(*) FROM trades")
        trade_count = cursor.fetchone()[0]

        print(f"Toplam kayıtlı trade: {trade_count}")

        if trade_count > 0:
            cursor.execute("""
                SELECT symbol, entry_price, exit_price, pnl, exit_reason, exit_time
                FROM trades
                ORDER BY exit_time DESC
                LIMIT 5
            """)

            print()
            print("Son 5 trade:")
            for row in cursor.fetchall():
                symbol, entry, exit, pnl, reason, time = row
                status = "✅" if pnl > 0 else "❌"
                print(f"   {status} {symbol}: Entry ${entry:.4f} → Exit ${exit:.4f} | P&L: ${pnl:+.2f} | {reason}")

    conn.close()

# 3. Öneriler
print()
print("=" * 100)
print("📋 ÖNERİLER")
print("=" * 100)
print()

if not state_file.exists() or (state_file.exists() and len(positions) == 0):
    print("⚠️  SİSTEM ÇALIŞIYOR AMA POZİSYON YOK")
    print()
    print("Kontrol edilecekler:")
    print()
    print("1. Paper Trading çalışıyor mu?")
    print("   → Paper Trading penceresinde log'ları kontrol et")
    print("   → 'İterasyon #X' mesajları görüyor musun?")
    print()
    print("2. Alert var mı?")
    print("   → dir pump_alerts")
    print("   → Bugünün dosyası var mı? Boyutu > 0?")
    print()
    print("3. Fiyat verisi var mı?")
    print("   → python CHECK_BINANCE_COLLECTOR.py")
    print("   → 160+ coin veri topluyor mu?")
    print()
    print("4. Paper Trading log'larını kontrol et:")
    print("   → Get-Content logs\\paper_trading.log -Tail 50")
    print("   → 'Fiyat verisi VAR' mesajı görüyor musun?")
    print()
else:
    print("✅ SİSTEM ÇALIŞIYOR VE POZİSYONLAR AKTİF!")
    print()
    print(f"   {len(positions)} açık pozisyon var")
    print(f"   Toplam bakiye: ${balance:,.2f}")
    print()
    print("Dashboard'u açarak pozisyonları görebilirsin:")
    print("   START_DASHBOARD.bat")
    print("   → http://localhost:5000")
    print()

print("=" * 100)
