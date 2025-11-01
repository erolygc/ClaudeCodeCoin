"""
Real-time Indicator Calculation Engine
Calculates technical indicators from stored kline data
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .basic_indicators import calculate_all_indicators
except ImportError:
    from basic_indicators import calculate_all_indicators


class IndicatorEngine:
    """
    Real-time indicator calculation engine
    """

    def __init__(self, db_path: str = "data_output/binance_data.db"):
        """
        Initialize indicator engine

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._init_indicator_table()

    def _init_indicator_table(self):
        """Create indicators table if not exists"""
        if not self.db_path.exists():
            print(f"⚠️  Database not found: {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                datetime TEXT,
                symbol TEXT,
                exchange TEXT,
                interval TEXT,

                -- Moving Averages
                sma_20 REAL,
                sma_50 REAL,
                sma_200 REAL,
                ema_12 REAL,
                ema_26 REAL,

                -- RSI
                rsi_14 REAL,

                -- MACD
                macd_line REAL,
                macd_signal REAL,
                macd_histogram REAL,

                -- Bollinger Bands
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,

                -- ATR
                atr_14 REAL,

                -- Stochastic
                stoch_k REAL,
                stoch_d REAL,

                -- OBV
                obv REAL,

                calculated_at TEXT
            )
        """)

        # Create index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_indicators_symbol_time
            ON indicators(symbol, exchange, timestamp DESC)
        """)

        conn.commit()
        conn.close()

        print(f"✅ Indicator table initialized: {self.db_path}")

    def fetch_kline_history(
        self,
        symbol: str,
        exchange: str = "binance",
        limit: int = 200
    ) -> Dict[str, List[float]]:
        """
        Fetch recent kline history for indicator calculation

        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            exchange: Exchange name
            limit: Number of candles to fetch

        Returns:
            Dict with close, high, low, volume lists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, open, high, low, close, volume
            FROM klines
            WHERE symbol = ? AND exchange = ?
            ORDER BY timestamp ASC
            LIMIT ?
        """, (symbol, exchange, limit))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {}

        return {
            'timestamps': [row[0] for row in rows],
            'open': [row[1] for row in rows],
            'high': [row[2] for row in rows],
            'low': [row[3] for row in rows],
            'close': [row[4] for row in rows],
            'volume': [row[5] for row in rows]
        }

    def calculate_indicators(
        self,
        symbol: str,
        exchange: str = "binance",
        interval: str = "1m"
    ) -> Optional[Dict[str, any]]:
        """
        Calculate all indicators for a symbol

        Args:
            symbol: Trading symbol
            exchange: Exchange name
            interval: Timeframe

        Returns:
            Dict with all indicator values
        """
        # Fetch history
        history = self.fetch_kline_history(symbol, exchange, limit=200)

        if not history or len(history.get('close', [])) < 20:
            print(f"⚠️  Insufficient data for {symbol} on {exchange}")
            return None

        # Calculate indicators
        indicators = calculate_all_indicators(
            prices=history['close'],
            high=history['high'],
            low=history['low'],
            volume=history['volume']
        )

        # Add metadata
        indicators['symbol'] = symbol
        indicators['exchange'] = exchange
        indicators['interval'] = interval
        indicators['timestamp'] = history['timestamps'][-1]
        indicators['datetime'] = datetime.fromtimestamp(
            history['timestamps'][-1] / 1000
        ).isoformat()
        indicators['calculated_at'] = datetime.utcnow().isoformat()

        return indicators

    def save_indicators(self, indicators: Dict[str, any]) -> bool:
        """
        Save calculated indicators to database

        Args:
            indicators: Dict with indicator values

        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Extract nested dict values
            macd = indicators.get('macd', {}) or {}
            bb = indicators.get('bb_20', {}) or {}
            stoch = indicators.get('stochastic_14', {}) or {}

            cursor.execute("""
                INSERT INTO indicators (
                    timestamp, datetime, symbol, exchange, interval,
                    sma_20, sma_50, sma_200, ema_12, ema_26,
                    rsi_14,
                    macd_line, macd_signal, macd_histogram,
                    bb_upper, bb_middle, bb_lower,
                    atr_14, stoch_k, stoch_d, obv,
                    calculated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                indicators.get('timestamp'),
                indicators.get('datetime'),
                indicators.get('symbol'),
                indicators.get('exchange'),
                indicators.get('interval'),
                indicators.get('sma_20'),
                indicators.get('sma_50'),
                indicators.get('sma_200'),
                indicators.get('ema_12'),
                indicators.get('ema_26'),
                indicators.get('rsi_14'),
                macd.get('macd') if isinstance(macd, dict) else None,
                macd.get('signal') if isinstance(macd, dict) else None,
                macd.get('histogram') if isinstance(macd, dict) else None,
                bb.get('upper') if isinstance(bb, dict) else None,
                bb.get('middle') if isinstance(bb, dict) else None,
                bb.get('lower') if isinstance(bb, dict) else None,
                indicators.get('atr_14'),
                stoch.get('k') if isinstance(stoch, dict) else None,
                stoch.get('d') if isinstance(stoch, dict) else None,
                indicators.get('obv'),
                indicators.get('calculated_at')
            ))

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ Error saving indicators: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            conn.close()

    def calculate_and_save(
        self,
        symbol: str,
        exchange: str = "binance",
        interval: str = "1m"
    ) -> bool:
        """
        Calculate and save indicators in one go

        Args:
            symbol: Trading symbol
            exchange: Exchange name
            interval: Timeframe

        Returns:
            True if successful
        """
        indicators = self.calculate_indicators(symbol, exchange, interval)

        if indicators is None:
            return False

        return self.save_indicators(indicators)

    def calculate_all_symbols(self, exchange: Optional[str] = None) -> Dict[str, bool]:
        """
        Calculate indicators for all symbols in database

        Args:
            exchange: Filter by exchange (optional)

        Returns:
            Dict with symbol: success status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if exchange:
            cursor.execute("""
                SELECT DISTINCT symbol, exchange
                FROM klines
                WHERE exchange = ?
            """, (exchange,))
        else:
            cursor.execute("""
                SELECT DISTINCT symbol, exchange
                FROM klines
            """)

        symbols = cursor.fetchall()
        conn.close()

        results = {}

        for symbol, exch in symbols:
            print(f"📊 Calculating indicators for {symbol} on {exch}...")
            success = self.calculate_and_save(symbol, exch)
            results[f"{exch}:{symbol}"] = success

        return results

    def get_latest_indicators(
        self,
        symbol: str,
        exchange: str = "binance"
    ) -> Optional[Dict[str, any]]:
        """
        Get latest calculated indicators for a symbol

        Args:
            symbol: Trading symbol
            exchange: Exchange name

        Returns:
            Dict with latest indicator values
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM indicators
            WHERE symbol = ? AND exchange = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (symbol, exchange))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Get column names
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(indicators)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        # Create dict
        indicators = dict(zip(columns, row))

        return indicators


if __name__ == "__main__":
    print("=" * 70)
    print("📊 ClaudeCodeCoin - Indicator Engine Test")
    print("=" * 70)
    print()

    engine = IndicatorEngine()

    # Calculate for all symbols
    print("🔄 Calculating indicators for all symbols...")
    results = engine.calculate_all_symbols()

    print()
    print("=" * 70)
    print("📊 RESULTS:")
    print("=" * 70)

    for key, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {key}")

    print()
    print("=" * 70)
