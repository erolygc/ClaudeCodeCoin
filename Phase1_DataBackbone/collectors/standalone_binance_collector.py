"""
Standalone Binance Collector - Docker Olmadan Çalışan Versiyon
Kafka ve TimescaleDB yerine CSV ve SQLite kullanır
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import websocket

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class StandaloneBinanceCollector:
    """
    Docker olmadan çalışan Binance veri toplayıcı
    - WebSocket ile gerçek veri toplar
    - CSV dosyasına kaydeder
    - SQLite veritabanına yazar
    """

    def __init__(self, symbols=None, interval="1m", output_dir="data_output"):
        """
        Args:
            symbols: Coin listesi (örn: ['BTCUSDT', 'ETHUSDT'])
            interval: Zaman aralığı (1m, 5m, 15m, 1h)
            output_dir: Veri kayıt klasörü
        """
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.symbols = [s.upper() for s in self.symbols]
        self.interval = interval
        self.output_dir = Path(output_dir)

        # Klasörleri oluştur
        self.output_dir.mkdir(exist_ok=True)
        self.csv_dir = self.output_dir / "csv"
        self.csv_dir.mkdir(exist_ok=True)

        # SQLite database
        self.db_path = self.output_dir / "binance_data.db"
        self._init_database()

        # WebSocket URL
        self.ws_url = self._build_ws_url()

        # İstatistikler
        self.messages_received = 0
        self.messages_saved = 0
        self.errors = 0
        self.start_time = None
        self.is_running = False
        self.ws = None

    def _init_database(self):
        """SQLite veritabanını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS klines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                datetime TEXT,
                symbol TEXT,
                interval TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                number_of_trades INTEGER,
                collected_at TEXT
            )
        """)

        # Index oluştur
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_time
            ON klines(symbol, timestamp DESC)
        """)

        conn.commit()
        conn.close()

        print(f"✅ SQLite database oluşturuldu: {self.db_path}")

    def _build_ws_url(self):
        """Binance WebSocket URL oluştur"""
        base_url = "wss://stream.binance.com:9443/stream"
        streams = [f"{symbol.lower()}@kline_{self.interval}" for symbol in self.symbols]
        streams_param = "/".join(streams)
        url = f"{base_url}?streams={streams_param}"
        return url

    def _save_to_csv(self, data):
        """Veriyi CSV dosyasına kaydet"""
        symbol = data["symbol"]
        csv_file = self.csv_dir / f"{symbol}_{self.interval}.csv"

        # CSV header
        headers = [
            "timestamp",
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "number_of_trades",
            "collected_at",
        ]

        # Dosya yoksa header yaz
        write_header = not csv_file.exists()

        with open(csv_file, "a", encoding="utf-8") as f:
            if write_header:
                f.write(",".join(headers) + "\n")

            # Veri satırı
            line = f"{data['timestamp']},{data['datetime']},{data['open']},{data['high']},{data['low']},{data['close']},{data['volume']},{data['number_of_trades']},{data['collected_at']}\n"
            f.write(line)

    def _save_to_sqlite(self, data):
        """Veriyi SQLite'a kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO klines (
                timestamp, datetime, symbol, interval,
                open, high, low, close, volume,
                number_of_trades, collected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["timestamp"],
                data["datetime"],
                data["symbol"],
                data["interval"],
                data["open"],
                data["high"],
                data["low"],
                data["close"],
                data["volume"],
                data["number_of_trades"],
                data["collected_at"],
            ),
        )

        conn.commit()
        conn.close()

    def _on_message(self, ws, message):
        """WebSocket mesajını işle"""
        try:
            self.messages_received += 1
            raw_data = json.loads(message)

            if "data" in raw_data:
                kline_data = raw_data["data"]
                stream_name = raw_data["stream"]
                symbol = stream_name.split("@")[0].upper()

                k = kline_data["k"]

                # Veriyi hazırla
                data = {
                    "timestamp": k["t"],
                    "datetime": datetime.fromtimestamp(k["t"] / 1000).isoformat(),
                    "symbol": symbol,
                    "interval": k["i"],
                    "open": float(k["o"]),
                    "high": float(k["h"]),
                    "low": float(k["l"]),
                    "close": float(k["c"]),
                    "volume": float(k["v"]),
                    "number_of_trades": k["n"],
                    "collected_at": datetime.utcnow().isoformat(),
                    "is_closed": k["x"],
                }

                # Sadece kapanan mumları kaydet
                if k["x"]:
                    # CSV'ye kaydet
                    self._save_to_csv(data)

                    # SQLite'a kaydet
                    self._save_to_sqlite(data)

                    self.messages_saved += 1

                    print(
                        f"📊 {symbol} {self.interval} | "
                        f"O: {data['open']:.2f} H: {data['high']:.2f} "
                        f"L: {data['low']:.2f} C: {data['close']:.2f} | "
                        f"V: {data['volume']:.2f} | "
                        f"💾 Saved (Total: {self.messages_saved})"
                    )

                    # Her 10 mumda istatistik göster
                    if self.messages_saved % 10 == 0:
                        self._print_stats()

        except Exception as e:
            self.errors += 1
            print(f"❌ Hata: {e}")

    def _on_error(self, ws, error):
        """WebSocket hatası"""
        print(f"❌ WebSocket Hatası: {error}")
        self.errors += 1

    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket kapandı"""
        print(f"⚠️  WebSocket bağlantısı kapandı: {close_status_code}")
        self.is_running = False

    def _on_open(self, ws):
        """WebSocket açıldı"""
        print(f"🚀 WebSocket bağlantısı açıldı!")
        print(f"📡 Dinlenen coinler: {', '.join(self.symbols)}")
        print(f"⏱️  Zaman aralığı: {self.interval}")
        print(f"💾 Veri klasörü: {self.output_dir.absolute()}")
        print(f"📊 Database: {self.db_path.name}")
        print("=" * 70)
        print("🔄 Veri toplamaya başlandı... (Durdurmak için Ctrl+C)")
        print("=" * 70)
        self.is_running = True
        import time

        self.start_time = time.time()

    def _print_stats(self):
        """İstatistikleri göster"""
        import time

        if self.start_time:
            elapsed = time.time() - self.start_time
            rate = self.messages_saved / elapsed if elapsed > 0 else 0

            print("\n" + "=" * 70)
            print("📊 İSTATİSTİKLER")
            print("=" * 70)
            print(f"⏱️  Süre: {elapsed:.1f} saniye")
            print(f"📥 Alınan mesaj: {self.messages_received}")
            print(f"💾 Kaydedilen mum: {self.messages_saved}")
            print(f"❌ Hata: {self.errors}")
            print(f"⚡ Hız: {rate:.2f} mum/saniye")
            print("=" * 70 + "\n")

    def start(self):
        """Veri toplamayı başlat"""
        print("\n" + "=" * 70)
        print("🚀 ClaudeCodeCoin - Standalone Binance Collector")
        print("=" * 70)
        print("Docker olmadan çalışan versiyon")
        print("Veri: CSV + SQLite")
        print("=" * 70 + "\n")

        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open,
            )

            self.ws.run_forever(ping_interval=20, ping_timeout=10)

        except KeyboardInterrupt:
            print("\n\n⏸️  Kullanıcı tarafından durduruldu...")
            self.stop()
        except Exception as e:
            print(f"\n❌ Fatal hata: {e}")
            self.stop()

    def stop(self):
        """Toplayıcıyı durdur"""
        print("\n" + "=" * 70)
        print("🛑 Toplayıcı durduruluyor...")
        print("=" * 70)

        self.is_running = False

        if self.ws:
            self.ws.close()

        self._print_stats()

        # Dosya konumlarını göster
        print("\n📁 Kaydedilen Dosyalar:")
        print(f"   CSV Klasörü: {self.csv_dir.absolute()}")
        print(f"   SQLite DB: {self.db_path.absolute()}")

        # CSV dosyalarını listele
        csv_files = list(self.csv_dir.glob("*.csv"))
        if csv_files:
            print(f"\n📊 CSV Dosyaları ({len(csv_files)} adet):")
            for f in csv_files:
                size_kb = f.stat().st_size / 1024
                print(f"   - {f.name} ({size_kb:.2f} KB)")

        # SQLite istatistikleri
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), symbol FROM klines GROUP BY symbol")
        results = cursor.fetchall()
        conn.close()

        if results:
            print(f"\n📈 Veritabanı İstatistikleri:")
            for count, symbol in results:
                print(f"   - {symbol}: {count} mum")

        print("\n✅ Toplayıcı başarıyla durduruldu!")
        print("=" * 70 + "\n")


def main():
    """Ana fonksiyon"""
    # Ayarlar
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    interval = "1m"  # 1 dakika
    output_dir = "data_output"

    # Toplayıcıyı başlat
    collector = StandaloneBinanceCollector(
        symbols=symbols, interval=interval, output_dir=output_dir
    )

    try:
        collector.start()
    except KeyboardInterrupt:
        print("\n⏸️  Kullanıcı tarafından durduruldu")
    finally:
        collector.stop()


if __name__ == "__main__":
    main()
