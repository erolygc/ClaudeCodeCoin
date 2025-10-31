"""
Standalone Gate.io Collector - Docker Olmadan Çalışan Versiyon
Gate.io WebSocket API ile gerçek zamanlı veri toplar
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import websocket

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class StandaloneGateioCollector:
    """
    Docker olmadan çalışan Gate.io veri toplayıcı
    - WebSocket ile gerçek veri toplar
    - CSV dosyasına kaydeder
    - SQLite veritabanına yazar (Binance ile aynı DB)
    """

    def __init__(self, symbols=None, interval="1m", output_dir="data_output"):
        """
        Args:
            symbols: Coin listesi (örn: ['BTC_USDT', 'ETH_USDT'])
            interval: Zaman aralığı (1m, 5m, 15m, 1h, 4h)
            output_dir: Veri kayıt klasörü
        """
        # Gate.io format: BTC_USDT (underscore)
        self.symbols = symbols or ["BTC_USDT", "ETH_USDT", "SOL_USDT"]
        self.symbols = [s.upper() for s in self.symbols]
        self.interval = interval
        self.output_dir = Path(output_dir)

        # Klasörleri oluştur
        self.output_dir.mkdir(exist_ok=True)
        self.csv_dir = self.output_dir / "csv"
        self.csv_dir.mkdir(exist_ok=True)

        # SQLite database (Binance ile aynı)
        self.db_path = self.output_dir / "binance_data.db"
        self._init_database()

        # WebSocket URL
        self.ws_url = "wss://api.gateio.ws/ws/v4/"

        # İstatistikler
        self.messages_received = 0
        self.messages_saved = 0
        self.errors = 0
        self.start_time = None
        self.is_running = False
        self.ws = None

        # Interval mapping (Gate.io format)
        self.interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
        }

    def _init_database(self):
        """SQLite veritabanını oluştur (zaten varsa atla)"""
        if self.db_path.exists():
            print(f"✅ Mevcut database kullanılıyor: {self.db_path}")
            return

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
                collected_at TEXT,
                exchange TEXT DEFAULT 'gate.io'
            )
        """)

        # Index oluştur
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_time
            ON klines(symbol, timestamp DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exchange_symbol
            ON klines(exchange, symbol, timestamp DESC)
        """)

        conn.commit()
        conn.close()

        print(f"✅ SQLite database oluşturuldu: {self.db_path}")

    def _save_to_csv(self, data):
        """Veriyi CSV dosyasına kaydet"""
        symbol = data["symbol"]
        csv_file = self.csv_dir / f"GATEIO_{symbol}_{self.interval}.csv"

        # CSV header
        headers = [
            "timestamp",
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "collected_at",
            "exchange",
        ]

        # Dosya yoksa header yaz
        write_header = not csv_file.exists()

        with open(csv_file, "a", encoding="utf-8") as f:
            if write_header:
                f.write(",".join(headers) + "\n")

            # Veri satırı
            line = f"{data['timestamp']},{data['datetime']},{data['open']},{data['high']},{data['low']},{data['close']},{data['volume']},{data['collected_at']},gate.io\n"
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
                number_of_trades, collected_at, exchange
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                0,  # Gate.io doesn't provide trade count in kline
                data["collected_at"],
                "gate.io",
            ),
        )

        conn.commit()
        conn.close()

    def _subscribe(self):
        """Gate.io WebSocket'e subscribe ol"""
        for symbol in self.symbols:
            # Gate.io subscription format
            subscribe_message = {
                "time": int(time.time()),
                "channel": "spot.candlesticks",
                "event": "subscribe",
                "payload": [self.interval_map[self.interval], symbol],
            }

            self.ws.send(json.dumps(subscribe_message))
            print(f"📡 Subscribed: {symbol} @ {self.interval}")

    def _on_message(self, ws, message):
        """WebSocket mesajını işle"""
        try:
            self.messages_received += 1
            data = json.loads(message)

            # Gate.io subscription confirmation
            if data.get("event") == "subscribe" and data.get("result", {}).get("status") == "success":
                print(f"✅ Subscription confirmed: {data['result']}")
                return

            # Candlestick update
            if data.get("channel") == "spot.candlesticks" and data.get("event") == "update":
                result = data.get("result", {})

                # Gate.io candlestick format:
                # result: {t: timestamp, v: volume, c: close, h: high, l: low, o: open, n: candle_name}
                # Example: {"t": "1606292580", "v": "2362.32", "c": "19128.1", "h": "19128.1", "l": "19128.1", "o": "19128.1", "n": "1m_BTC_USDT"}

                if "t" in result and "c" in result:
                    timestamp_str = str(result["t"])
                    open_price = float(result.get("o", 0))
                    high = float(result.get("h", 0))
                    low = float(result.get("l", 0))
                    close = float(result.get("c", 0))
                    volume = float(result.get("v", 0))
                    candle_name = result.get("n", "")

                    # Extract symbol from candle name (format: "1m_BTC_USDT")
                    if "_" in candle_name:
                        parts = candle_name.split("_")
                        if len(parts) >= 3:
                            symbol = f"{parts[1]}_{parts[2]}"
                        else:
                            symbol = self.symbols[0]
                    else:
                        symbol = self.symbols[0]
                else:
                    return

                # Prepare data
                kline_data = {
                    "timestamp": int(timestamp_str) * 1000,  # Convert to milliseconds
                    "datetime": datetime.fromtimestamp(int(timestamp_str)).isoformat(),
                    "symbol": symbol,
                    "interval": self.interval,
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": volume,
                    "collected_at": datetime.utcnow().isoformat(),
                }

                # Save to CSV and SQLite
                self._save_to_csv(kline_data)
                self._save_to_sqlite(kline_data)

                self.messages_saved += 1

                print(
                    f"📊 [Gate.io] {symbol} {self.interval} | "
                    f"O: {open_price:.2f} H: {high:.2f} "
                    f"L: {low:.2f} C: {close:.2f} | "
                    f"V: {volume:.2f} | "
                    f"💾 SAVED (Total: {self.messages_saved})"
                )

                # Her 10 mumda istatistik göster
                if self.messages_saved % 10 == 0:
                    self._print_stats()

        except Exception as e:
            self.errors += 1
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()

    def _on_error(self, ws, error):
        """WebSocket hatası"""
        if error:
            print(f"❌ WebSocket Hatası: {error}")
            import traceback
            traceback.print_exc()
        self.errors += 1

    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket kapandı"""
        print(f"\n⚠️  WebSocket bağlantısı kapandı!")
        print(f"   Durum Kodu: {close_status_code}")
        print(f"   Mesaj: {close_msg}")
        print(f"   Toplam alınan mesaj: {self.messages_received}")
        print(f"   Kaydedilen mum: {self.messages_saved}")
        self.is_running = False

    def _on_open(self, ws):
        """WebSocket açıldı"""
        print(f"🚀 Gate.io WebSocket bağlantısı açıldı!")
        print(f"📡 Dinlenen coinler: {', '.join(self.symbols)}")
        print(f"⏱️  Zaman aralığı: {self.interval}")
        print(f"💾 Veri klasörü: {self.output_dir.absolute()}")
        print(f"📊 Database: {self.db_path.name}")
        print("=" * 70)
        print("🔄 Veri toplamaya başlandı... (Durdurmak için Ctrl+C)")
        print("")
        print("⏳ Gate.io'dan veri alınıyor...")
        print("   - Her güncelleme anında kaydedilecek")
        print("=" * 70)
        self.is_running = True
        self.start_time = time.time()

        # Subscribe to channels
        self._subscribe()

    def _print_stats(self):
        """İstatistikleri göster"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            rate = self.messages_saved / elapsed if elapsed > 0 else 0

            print("\n" + "=" * 70)
            print("📊 İSTATİSTİKLER (Gate.io)")
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
        print("🚀 ClaudeCodeCoin - Standalone Gate.io Collector")
        print("=" * 70)
        print("Docker olmadan çalışan versiyon")
        print("Veri: CSV + SQLite (Binance ile aynı DB)")
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
        csv_files = list(self.csv_dir.glob("GATEIO_*.csv"))
        if csv_files:
            print(f"\n📊 Gate.io CSV Dosyaları ({len(csv_files)} adet):")
            for f in csv_files:
                size_kb = f.stat().st_size / 1024
                print(f"   - {f.name} ({size_kb:.2f} KB)")

        # SQLite istatistikleri
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), symbol FROM klines WHERE exchange = 'gate.io' GROUP BY symbol")
        results = cursor.fetchall()
        conn.close()

        if results:
            print(f"\n📈 Gate.io Veritabanı İstatistikleri:")
            for count, symbol in results:
                print(f"   - {symbol}: {count} mum")

        print("\n✅ Toplayıcı başarıyla durduruldu!")
        print("=" * 70 + "\n")


def main():
    """Ana fonksiyon"""
    # Ayarlar
    symbols = ["BTC_USDT", "ETH_USDT", "SOL_USDT"]
    interval = "1m"  # 1 dakika
    output_dir = "data_output"

    # Toplayıcıyı başlat
    collector = StandaloneGateioCollector(
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
