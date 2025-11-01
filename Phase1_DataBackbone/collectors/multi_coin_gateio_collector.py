"""
ClaudeCodeCoin - Multi-Coin Gate.io Collector

40+ coin için WebSocket veri toplama
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

from config.trading_pairs import get_gateio_symbols, COLLECTOR_CONFIG

class MultiCoinGateioCollector:
    """
    Birden fazla coin için Gate.io collector
    """

    def __init__(self, db_path="data_output/binance_data.db"):
        self.db_path = db_path
        self.symbols = get_gateio_symbols()
        self.interval = COLLECTOR_CONFIG["gateio"]["interval"]

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
        print("🚀 ClaudeCodeCoin - Multi-Coin Gate.io Collector")
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
                exchange TEXT DEFAULT 'gate.io',
                UNIQUE(timestamp, symbol, exchange)
            )
        """)

        conn.commit()
        conn.close()

    def _subscribe_to_symbols(self, ws):
        """Tüm sembollere subscribe ol"""
        for symbol in self.symbols:
            # Gate.io subscription format
            subscribe_message = {
                "time": int(time.time()),
                "channel": "spot.candlesticks",
                "event": "subscribe",
                "payload": [self.interval, symbol]
            }

            ws.send(json.dumps(subscribe_message))
            time.sleep(0.1)  # Rate limiting

        print(f"✅ {len(self.symbols)} sembole subscribe edildi")

    def _save_candle(self, symbol, candle_data):
        """Mumu kaydet"""
        try:
            # Gate.io format: [timestamp, volume, close, high, low, open, ...]
            timestamp_str = str(candle_data["t"])
            timestamp = int(timestamp_str)

            dt = datetime.fromtimestamp(timestamp)

            data = {
                "timestamp": timestamp,
                "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "interval": self.interval,
                "open": float(candle_data.get("o", 0)),
                "high": float(candle_data.get("h", 0)),
                "low": float(candle_data.get("l", 0)),
                "close": float(candle_data.get("c", 0)),
                "volume": float(candle_data.get("v", 0)),
                "number_of_trades": 0,
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "exchange": "gate.io"
            }

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Duplicate check
            cursor.execute("""
                SELECT id FROM klines
                WHERE timestamp = ? AND symbol = ? AND exchange = ?
            """, (data["timestamp"], data["symbol"], "gate.io"))

            if cursor.fetchone():
                # Update
                cursor.execute("""
                    UPDATE klines SET
                        high = ?, low = ?, close = ?, volume = ?,
                        collected_at = ?
                    WHERE timestamp = ? AND symbol = ? AND exchange = ?
                """, (
                    data["high"], data["low"], data["close"], data["volume"],
                    data["collected_at"],
                    data["timestamp"], data["symbol"], "gate.io"
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
                    data["collected_at"], "gate.io"
                ))

            conn.commit()
            conn.close()

            self.stats["candles_saved"] += 1

            # Log
            print(f"💾 {symbol:15} | "
                  f"O: {data['open']:.4f} "
                  f"H: {data['high']:.4f} "
                  f"L: {data['low']:.4f} "
                  f"C: {data['close']:.4f} | "
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

            self.stats["messages_received"] += 1

            # Update event
            if data.get("event") == "update" and data.get("channel") == "spot.candlesticks":
                result = data.get("result", {})

                # Symbol ve candle data
                symbol = result.get("n", "").split("_")
                if len(symbol) >= 2:
                    symbol_name = "_".join(symbol[1:])  # "1m_BTC_USDT" -> "BTC_USDT"

                    # Candle data (object format)
                    self._save_candle(symbol_name, result)

                    # Periyodik stats
                    if self.stats["candles_saved"] % 20 == 0 and self.stats["candles_saved"] > 0:
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
        print(f"📡 Subscribe ediliyor...")

        # Subscribe
        self._subscribe_to_symbols(ws)

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

        ws_url = "wss://api.gateio.ws/ws/v4/"

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
    collector = MultiCoinGateioCollector()
    collector.start()


if __name__ == "__main__":
    main()
