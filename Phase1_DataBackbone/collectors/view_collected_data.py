"""
Toplanan Veriyi Görüntüleme Scripti
SQLite veritabanındaki veriyi analiz eder ve gösterir
"""

import sqlite3
import sys
from pathlib import Path

# Proje root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def view_database_stats(db_path="data_output/binance_data.db"):
    """Veritabanı istatistiklerini göster"""
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ Veritabanı bulunamadı: {db_path}")
        print("\nÖnce veri toplayıcısını çalıştırın:")
        print("  python Phase1_DataBackbone\\collectors\\standalone_binance_collector.py")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("📊 ClaudeCodeCoin - Toplanan Veri Analizi")
    print("=" * 70)

    # Toplam kayıt sayısı
    cursor.execute("SELECT COUNT(*) FROM klines")
    total_count = cursor.fetchone()[0]
    print(f"\n📈 Toplam Kayıt: {total_count} mum")

    if total_count == 0:
        print("\n⚠️  Henüz veri toplanmamış!")
        print("Veri toplamak için collector'ı çalıştırın.")
        conn.close()
        return

    # Coin bazında istatistikler
    print("\n📊 Coin Bazında İstatistikler:")
    print("-" * 70)
    cursor.execute("""
        SELECT
            symbol,
            COUNT(*) as count,
            MIN(datetime) as first_candle,
            MAX(datetime) as last_candle,
            AVG(volume) as avg_volume
        FROM klines
        GROUP BY symbol
        ORDER BY count DESC
    """)

    results = cursor.fetchall()
    for symbol, count, first, last, avg_vol in results:
        print(f"  {symbol:10s} | Mum: {count:6d} | İlk: {first[:16]} | Son: {last[:16]} | Avg Vol: {avg_vol:,.2f}")

    # Son 10 kayıt
    print("\n📋 Son 10 Kayıt:")
    print("-" * 70)
    cursor.execute("""
        SELECT datetime, symbol, open, high, low, close, volume
        FROM klines
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    results = cursor.fetchall()
    for dt, symbol, o, h, l, c, v in results:
        print(f"  {dt[:19]} | {symbol:10s} | O: {o:9.2f} H: {h:9.2f} L: {l:9.2f} C: {c:9.2f} | Vol: {v:12,.2f}")

    # Fiyat analizi
    print("\n💰 Fiyat Analizi (Son Mum):")
    print("-" * 70)
    cursor.execute("""
        SELECT DISTINCT symbol FROM klines
    """)
    symbols = [row[0] for row in cursor.fetchall()]

    for symbol in symbols:
        cursor.execute("""
            SELECT open, high, low, close, volume
            FROM klines
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (symbol,))

        result = cursor.fetchone()
        if result:
            o, h, l, c, v = result
            change = ((c - o) / o * 100) if o > 0 else 0
            change_emoji = "🟢" if change >= 0 else "🔴"

            print(f"  {change_emoji} {symbol:10s} | Fiyat: ${c:11,.2f} | Değişim: {change:+6.2f}% | Hacim: {v:15,.2f}")

    # Veritabanı boyutu
    db_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"\n💾 Veritabanı Boyutu: {db_size_mb:.2f} MB")
    print(f"📁 Konum: {db_path.absolute()}")

    print("\n" + "=" * 70)

    conn.close()


def export_to_csv_summary(db_path="data_output/binance_data.db", output_file="data_summary.csv"):
    """Özet raporu CSV olarak dışa aktar"""
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ Veritabanı bulunamadı: {db_path}")
        return

    conn = sqlite3.connect(db_path)

    import pandas as pd

    # Tüm veriyi pandas'a al
    df = pd.read_sql_query("SELECT * FROM klines ORDER BY timestamp", conn)

    if df.empty:
        print("⚠️  Veri yok!")
        conn.close()
        return

    # Datetime'ı düzelt
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Özet istatistikler
    summary = df.groupby("symbol").agg({
        "close": ["min", "max", "mean", "last"],
        "volume": ["sum", "mean"],
        "timestamp": "count"
    }).reset_index()

    # CSV'ye kaydet
    summary.to_csv(output_file, index=False)

    print(f"\n✅ Özet rapor kaydedildi: {output_file}")
    print(summary)

    conn.close()


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description="Toplanan veriyi görüntüle")
    parser.add_argument(
        "--db",
        default="data_output/binance_data.db",
        help="SQLite veritabanı yolu",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="CSV özet raporu oluştur",
    )

    args = parser.parse_args()

    # İstatistikleri göster
    view_database_stats(args.db)

    # CSV export iste
    if args.export:
        try:
            export_to_csv_summary(args.db)
        except ImportError:
            print("\n⚠️  Pandas kurulu değil. CSV export için:")
            print("  pip install pandas")


if __name__ == "__main__":
    main()
