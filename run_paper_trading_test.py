"""
Paper Trading - Test Modu
Birkaç iterasyon çalıştır ve sonuçları göster
"""
import sys
from pathlib import Path
import time

# Paths
sys.path.insert(0, str(Path(__file__).parent / "Phase7_PaperTrading"))

# Config'i test için düzenle (daha düşük threshold)
from Phase7_PaperTrading import config
config.MIN_CONFIDENCE_TO_TRADE = 50.0  # Test için düşürüldü
config.MIN_VOLUME_SPIKE = 100.0  # Test için düşürüldü

from Phase7_PaperTrading.paper_trading_engine import PaperTradingEngine

def main():
    print()
    print("=" * 80)
    print("PAPER TRADING ENGINE - TEST MODE")
    print("=" * 80)
    print("⚠️  TEST MODE: Lower thresholds for demonstration")
    print(f"   Min Confidence: {config.MIN_CONFIDENCE_TO_TRADE}% (Production: 70%)")
    print(f"   Min Volume Spike: {config.MIN_VOLUME_SPIKE}% (Production: 800%)")
    print("=" * 80)
    print()

    # Engine'i başlat
    engine = PaperTradingEngine()

    print("Running 5 iterations (30 seconds each)...\n")

    # 5 iterasyon çalıştır
    for i in range(1, 6):
        print(f"\n{'='*80}")
        print(f"ITERATION #{i}")
        print('='*80)

        # 1. Alert'leri kontrol et ve pozisyon aç
        engine.process_alerts()

        # 2. Açık pozisyonları güncelle
        engine.update_open_positions()

        # 3. Durum raporu
        engine.print_status()

        if i < 5:
            print(f"\n⏳ Waiting 10 seconds before next iteration...\n")
            time.sleep(10)

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print()

    # Final rapor
    summary = engine.position_manager.get_portfolio_summary()

    print("📊 FINAL RESULTS:")
    print("-" * 80)
    print(f"Starting Balance:  ${config.INITIAL_BALANCE:.2f}")
    print(f"Current Balance:   ${summary['balance']:.2f}")
    print(f"Total P&L:         ${summary['total_pnl']:.2f} ({summary['total_pnl_percent']:+.2f}%)")
    print(f"Total Trades:      {summary['total_trades']}")
    print(f"Open Positions:    {summary['open_positions']}")

    if summary['total_trades'] > 0:
        print(f"\nWin Rate:          {summary['win_rate']:.1f}%")
        print(f"Winning Trades:    {summary['winning_trades']}")
        print(f"Losing Trades:     {summary['losing_trades']}")
        print(f"Average Win:       ${summary['avg_win']:.2f}")
        print(f"Average Loss:      ${summary['avg_loss']:.2f}")

    print("-" * 80)
    print()

    # Trades database'den oku
    try:
        import sqlite3
        db_path = Path("data_output/paper_trades.db")

        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM positions WHERE status = 'CLOSED'")
            closed = cursor.fetchone()[0]

            if closed > 0:
                print("📜 CLOSED POSITIONS:")
                print("-" * 80)

                cursor.execute("""
                    SELECT symbol, entry_price, exit_price, pnl, close_reason, confidence
                    FROM positions
                    WHERE status = 'CLOSED'
                    ORDER BY entry_time DESC
                    LIMIT 10
                """)

                for row in cursor.fetchall():
                    symbol, entry, exit, pnl, reason, conf = row
                    pnl_pct = ((exit - entry) / entry) * 100 if entry else 0
                    print(f"{symbol:12s} Entry: ${entry:8.4f} Exit: ${exit:8.4f} "
                          f"P&L: ${pnl:+8.2f} ({pnl_pct:+6.2f}%) "
                          f"Reason: {reason} (Conf: {conf:.0f}%)")

            conn.close()

    except Exception as e:
        print(f"Note: {e}")

    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
