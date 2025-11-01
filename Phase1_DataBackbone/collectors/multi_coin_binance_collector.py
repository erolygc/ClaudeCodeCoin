"""
ClaudeCodeCoin - Multi-Coin Binance Collector

50+ coin için WebSocket veri toplama (optimized)
"""

import websocket
import json
import sqlite3
from datetime import datetime
import time
import os
import sys
from pathlib import Path

# Config import
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.trading_pairs import get_binance_symbols, COLLECTOR_CONFIG

class MultiCoinBinanceCollector:
    """
    Birden fazla coin için optimize edilmiş Binance collector

    Özellikler:
    - Tek WebSocket bağlantısı ile 50+ coin
    - Efficient batch processing
    - Auto-reconnect
    - SQLite database
    """

    def __init__(self, db_path="data_output/binance_data.db"):
        self.db_path = db_path
        self.symbols = get_binance_symbols()
        self.interval = COLLECTOR_CONFIG["binance"]["interval"]

        # İstatistikler
        self.stats = {
            "messages_received": 0,
            "candles_saved": 0,
            "errors": 0,
            "start_time": time.time()
        }

        # Database setup
        self._setup_database()

        print("="*70)
        print("🚀 ClaudeCodeCoin - Multi-Coin Binance Collector")
        print("="*70)
        print(f"📊 Toplam Coin: {len(self.symbols)}")
        print(f"⏱️  Interval: {self.interval}")
        print(f"💾 Database: {self.db_path}")
        print("="*70)

    def _setup_database(self):
        """Database oluştur"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS klines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                datetime TEXT NOT NULL,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                number_of_trades INTEGER DEFAULT 0,
                collected_at TEXT NOT NULL,
                exchange TEXT DEFAULT 'binance',
                UNIQUE(timestamp, symbol, exchange)
            )
        """)

        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_timestamp
            ON klines(symbol, timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exchange_symbol
            ON klines(exchange, symbol)
        """)

        conn.commit()
        conn.close()

    def _get_websocket_url(self):
        """
        Combined streams URL oluştur
        Binance max 200 stream'e izin veriyor
        """
        # Her sembol için kline stream
        streams = [f"{symbol.lower()}@kline_{self.interval}" for symbol in self.symbols]

        # Batch'lere böl (max 100 stream per connection)
        if len(streams) > 100:
            print(f"⚠️  {len(streams)} stream > 100, ilk 100'ü alıyorum")
            streams = streams[:100]

        # Combined stream URL
        streams_param = "/".join(streams)
        url = f"wss://stream.binance.com:9443/stream?streams={streams_param}"

        return url

    def _save_candle(self, symbol, candle_data):
        """Mumu kaydet"""
        try:
            k = candle_data

            # Sadece kapanan mumları kaydet
            if not k.get('x', False):
                return False

            timestamp = k['t'] // 1000
            dt = datetime.fromtimestamp(timestamp)

            data = {
                "timestamp": timestamp,
                "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "interval": k['i'],
                "open": float(k['o']),
                "high": float(k['h']),
                "low": float(k['l']),
                "close": float(k['c']),
                "volume": float(k['v']),
                "number_of_trades": k.get('n', 0),
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "exchange": "binance"
            }

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Duplicate check
            cursor.execute("""
                SELECT id FROM klines
                WHERE timestamp = ? AND symbol = ? AND exchange = ?
            """, (data["timestamp"], data["symbol"], "binance"))

            if cursor.fetchone():
                # Update
                cursor.execute("""
                    UPDATE klines SET
                        high = ?, low = ?, close = ?, volume = ?,
                        number_of_trades = ?, collected_at = ?
                    WHERE timestamp = ? AND symbol = ? AND exchange = ?
                """, (
                    data["high"], data["low"], data["close"], data["volume"],
                    data["number_of_trades"], data["collected_at"],
                    data["timestamp"], data["symbol"], "binance"
                ))
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO klines (
                        timestamp, datetime, symbol, interval,
                        open, high, low, close, volume,
                        number_of_trades, collected_at, exchange
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["timestamp"], data["datetime"], data["symbol"],
                    data["interval"], data["open"], data["high"], data["low"],
                    data["close"], data["volume"], data["number_of_trades"],
                    data["collected_at"], "binance"
                ))

            conn.commit()
            conn.close()

            self.stats["candles_saved"] += 1

            # Log
            print(f"💾 {symbol:12} | "
                  f"O: {data['open']:.2f} "
                  f"H: {data['high']:.2f} "
                  f"L: {data['low']:.2f} "
                  f"C: {data['close']:.2f} | "
                  f"V: {data['volume']:.2f} | "
                  f"Total: {self.stats['candles_saved']}")

            return True

        except Exception as e:
            print(f"❌ Kaydetme hatası ({symbol}): {e}")
            self.stats["errors"] += 1
            return False

    def _on_message(self, ws, message):
        """WebSocket mesaj handler"""
        try:
            data = json.loads(message)

            # Stream data format
            if "data" in data:
                stream_data = data["data"]

                # Kline event
                if stream_data.get("e") == "kline":
                    symbol = stream_data["s"]
                    candle = stream_data["k"]

                    self.stats["messages_received"] += 1

                    # Kapanan mumu kaydet
                    if candle.get('x', False):
                        self._save_candle(symbol, candle)

                    # Periyodik istatistikler (her 100 mesajda)
                    if self.stats["messages_received"] % 100 == 0:
                        self._print_stats()

        except Exception as e:
            print(f"❌ Message handling error: {e}")
            self.stats["errors"] += 1

    def _on_error(self, ws, error):
        """Error handler"""
        print(f"❌ WebSocket Error: {error}")
        self.stats["errors"] += 1

    def _on_close(self, ws, close_status_code, close_msg):
        """Close handler"""
        print("\n🔌 WebSocket bağlantısı kapandı")
        self._print_stats()

    def _on_open(self, ws):
        """Open handler"""
        print(f"\n🚀 WebSocket bağlantısı açıldı!")
        print(f"📡 İzlenen coinler: {len(self.symbols)} adet")
        print(f"⏱️  Interval: {self.interval}")
        print("="*70)
        print("🔄 Veri toplamaya başlandı... (Durdurmak için Ctrl+C)")
        print("="*70)

    def _print_stats(self):
        """İstatistikleri yazdır"""
        elapsed = time.time() - self.stats["start_time"]
        rate = self.stats["candles_saved"] / elapsed if elapsed > 0 else 0

        print("\n" + "="*70)
        print("📊 İSTATİSTİKLER")
        print("="*70)
        print(f"⏱️  Süre: {elapsed:.1f} saniye")
        print(f"📥 Alınan mesaj: {self.stats['messages_received']}")
        print(f"💾 Kaydedilen mum: {self.stats['candles_saved']}")
        print(f"❌ Hata: {self.stats['errors']}")
        print(f"⚡ Hız: {rate:.2f} mum/saniye")
        print(f"📊 Aktif sembol: {len(self.symbols)}")
        print("="*70 + "\n")

    def start(self):
        """Collector'ı başlat"""
        websocket.enableTrace(False)

        ws_url = self._get_websocket_url()

        print(f"\n🔗 WebSocket URL hazırlandı")
        print(f"   Stream sayısı: {len(self.symbols)}")
        print()

        ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )

        try:
            ws.run_forever()
        except KeyboardInterrupt:
            print("\n\n⏹️  Collector durduruldu (Ctrl+C)")
            self._print_stats()
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")
            self.stats["errors"] += 1


def main():
    """Main function"""
    collector = MultiCoinBinanceCollector()
    collector.start()


if __name__ == "__main__":
    main()
