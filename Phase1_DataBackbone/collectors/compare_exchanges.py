"""
Multi-Exchange Karşılaştırma Aracı
Binance ve Gate.io verilerini karşılaştırır
"""

import sqlite3
import sys
from pathlib import Path

# Proje root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def compare_exchanges(db_path="data_output/binance_data.db"):
    """Exchange'leri karşılaştır"""
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ Veritabanı bulunamadı: {db_path}")
        print("\nÖnce veri toplayıcıları çalıştırın:")
        print("  Binance: START_COLLECTOR.bat")
        print("  Gate.io: START_GATEIO_COLLECTOR.bat")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("📊 ClaudeCodeCoin - Multi-Exchange Karşılaştırma")
    print("=" * 80)

    # Toplam istatistikler
    cursor.execute("""
        SELECT
            COALESCE(exchange, 'binance') as exchange,
            COUNT(*) as total_candles,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN(datetime) as first_candle,
            MAX(datetime) as last_candle
        FROM klines
        GROUP BY COALESCE(exchange, 'binance')
        ORDER BY exchange
    """)

    results = cursor.fetchall()

    print("\n📈 Exchange Bazında Genel İstatistikler:")
    print("-" * 80)
    print(f"{'Exchange':<15} {'Toplam Mum':<15} {'Coin Sayısı':<15} {'İlk':<20} {'Son':<20}")
    print("-" * 80)

    for exchange, total, symbols, first, last in results:
        print(f"{exchange:<15} {total:<15} {symbols:<15} {first[:19]:<20} {last[:19]:<20}")

    # Symbol bazında karşılaştırma
    print("\n💰 Coin Bazında Karşılaştırma:")
    print("-" * 80)

    # Ortak coinleri bul
    cursor.execute("""
        SELECT DISTINCT
            REPLACE(symbol, '_', '') as normalized_symbol
        FROM klines
        WHERE COALESCE(exchange, 'binance') = 'binance'

        INTERSECT

        SELECT DISTINCT
            REPLACE(symbol, '_', '') as normalized_symbol
        FROM klines
        WHERE exchange = 'gate.io'
    """)

    common_symbols = [row[0] for row in cursor.fetchall()]

    if not common_symbols:
        print("⚠️  Henüz ortak coin verisi yok!")
        print("   Her iki exchange'den de aynı coinleri toplayın.")
    else:
        print(f"✅ {len(common_symbols)} ortak coin bulundu: {', '.join(common_symbols)}")
        print()

        for symbol in common_symbols:
            print(f"\n🔍 {symbol} Detaylı Karşılaştırma:")
            print("-" * 80)

            # Binance data
            cursor.execute("""
                SELECT
                    COUNT(*) as candles,
                    AVG(close) as avg_price,
                    MIN(close) as min_price,
                    MAX(close) as max_price,
                    SUM(volume) as total_volume
                FROM klines
                WHERE REPLACE(symbol, '_', '') = ?
                  AND COALESCE(exchange, 'binance') = 'binance'
            """, (symbol,))

            binance_data = cursor.fetchone()

            # Gate.io data
            cursor.execute("""
                SELECT
                    COUNT(*) as candles,
                    AVG(close) as avg_price,
                    MIN(close) as min_price,
                    MAX(close) as max_price,
                    SUM(volume) as total_volume
                FROM klines
                WHERE REPLACE(symbol, '_', '') = ?
                  AND exchange = 'gate.io'
            """, (symbol,))

            gateio_data = cursor.fetchone()

            print(f"{'Metric':<20} {'Binance':<25} {'Gate.io':<25} {'Fark':<15}")
            print("-" * 80)

            if binance_data and binance_data[0] > 0 and gateio_data and gateio_data[0] > 0:
                # Mum sayısı
                print(f"{'Mum Sayısı':<20} {binance_data[0]:<25} {gateio_data[0]:<25} {abs(binance_data[0] - gateio_data[0]):<15}")

                # Ortalama fiyat
                binance_avg = binance_data[1]
                gateio_avg = gateio_data[1]
                price_diff = ((gateio_avg - binance_avg) / binance_avg * 100) if binance_avg else 0

                print(f"{'Ort. Fiyat':<20} ${binance_avg:>23,.2f} ${gateio_avg:>23,.2f} {price_diff:>+14.4f}%")

                # Min fiyat
                print(f"{'Min Fiyat':<20} ${binance_data[2]:>23,.2f} ${gateio_data[2]:>23,.2f}")

                # Max fiyat
                print(f"{'Max Fiyat':<20} ${binance_data[3]:>23,.2f} ${gateio_data[3]:>23,.2f}")

                # Toplam hacim
                vol_diff = ((gateio_data[4] - binance_data[4]) / binance_data[4] * 100) if binance_data[4] else 0
                print(f"{'Toplam Hacim':<20} {binance_data[4]:>23,.2f} {gateio_data[4]:>23,.2f} {vol_diff:>+14.2f}%")

                # Fiyat farkı analizi
                if abs(price_diff) > 0.01:
                    print(f"\n⚠️  Arbitraj Fırsatı? Fiyat farkı: {price_diff:+.4f}%")
                    if price_diff > 0:
                        print(f"   Gate.io daha pahalı - Binance'ten al, Gate.io'da sat?")
                    else:
                        print(f"   Binance daha pahalı - Gate.io'dan al, Binance'de sat?")
            else:
                print(f"⚠️  Yeterli veri yok")

    # Son fiyatlar karşılaştırması
    print("\n\n💵 Son Fiyatlar Karşılaştırması:")
    print("-" * 80)
    print(f"{'Symbol':<15} {'Binance':<20} {'Gate.io':<20} {'Fark %':<15}")
    print("-" * 80)

    cursor.execute("""
        SELECT DISTINCT REPLACE(symbol, '_', '') as normalized_symbol
        FROM klines
        LIMIT 10
    """)

    all_symbols = [row[0] for row in cursor.fetchall()]

    for symbol in all_symbols:
        # Binance son fiyat
        cursor.execute("""
            SELECT close
            FROM klines
            WHERE REPLACE(symbol, '_', '') = ?
              AND COALESCE(exchange, 'binance') = 'binance'
            ORDER BY timestamp DESC
            LIMIT 1
        """, (symbol,))

        binance_result = cursor.fetchone()
        binance_price = binance_result[0] if binance_result else None

        # Gate.io son fiyat
        cursor.execute("""
            SELECT close
            FROM klines
            WHERE REPLACE(symbol, '_', '') = ?
              AND exchange = 'gate.io'
            ORDER BY timestamp DESC
            LIMIT 1
        """, (symbol,))

        gateio_result = cursor.fetchone()
        gateio_price = gateio_result[0] if gateio_result else None

        if binance_price and gateio_price:
            diff = ((gateio_price - binance_price) / binance_price * 100)
            emoji = "🟢" if diff >= 0 else "🔴"
            print(f"{emoji} {symbol:<12} ${binance_price:>18,.2f} ${gateio_price:>18,.2f} {diff:>+14.4f}%")
        elif binance_price:
            print(f"   {symbol:<12} ${binance_price:>18,.2f} {'N/A':<20} {'N/A':<15}")
        elif gateio_price:
            print(f"   {symbol:<12} {'N/A':<20} ${gateio_price:>18,.2f} {'N/A':<15}")

    print("\n" + "=" * 80)
    print("\n💡 İpucu:")
    print("   - Fiyat farkları arbitraj fırsatı olabilir!")
    print("   - Ancak komisyon, slippage ve transfer sürelerini hesaba katın")
    print("   - Risk yönetimi çok önemli!")
    print("\n" + "=" * 80)

    conn.close()


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description="Exchange'leri karşılaştır")
    parser.add_argument(
        "--db",
        default="data_output/binance_data.db",
        help="SQLite veritabanı yolu",
    )

    args = parser.parse_args()

    compare_exchanges(args.db)


if __name__ == "__main__":
    main()
