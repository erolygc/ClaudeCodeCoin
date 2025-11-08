"""
Multi-Timeframe Data Aggregator
Converts 1m candles to multiple timeframes (3m, 5m, 15m, 30m, 1h, 4h, 1d)
Stores last 250 bars per timeframe in Parquet format for ultra-fast access
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimeframeAggregator:
    """
    Aggregates 1m candles into multiple timeframes
    Maintains rolling window of last 250 bars per timeframe
    """

    # Supported timeframes (in minutes)
    TIMEFRAMES = {
        '1m': 1,
        '3m': 3,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '4h': 240,
        '1d': 1440
    }

    MAX_BARS_PER_TIMEFRAME = 250  # Keep last 250 bars

    def __init__(self, db_path: str = None,
                 output_dir: str = None):
        """
        Initialize TimeframeAggregator

        Args:
            db_path: Path to source 1m data database (default: auto-detect)
            output_dir: Directory to store multi-timeframe parquet files (default: auto-detect)
        """
        # Auto-detect paths relative to this script's location
        script_dir = Path(__file__).parent

        if db_path is None:
            self.db_path = str(script_dir / "data_output" / "binance_data.db")
        else:
            self.db_path = db_path

        if output_dir is None:
            self.output_dir = script_dir / "data_multi_timeframe"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"TimeframeAggregator initialized")
        logger.info(f"Source DB: {self.db_path}")
        logger.info(f"Output Dir: {self.output_dir}")
        logger.info(f"Timeframes: {list(self.TIMEFRAMES.keys())}")

    def aggregate_candles(self, df_1m: pd.DataFrame, timeframe_minutes: int) -> pd.DataFrame:
        """
        Aggregate 1m candles to higher timeframe

        Args:
            df_1m: DataFrame with 1m OHLCV data
            timeframe_minutes: Target timeframe in minutes

        Returns:
            Aggregated DataFrame
        """
        if df_1m.empty or len(df_1m) < timeframe_minutes:
            return pd.DataFrame()

        # Ensure datetime index
        if 'datetime' not in df_1m.columns:
            return pd.DataFrame()

        df = df_1m.copy()
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)

        # Resample to target timeframe
        rule = f'{timeframe_minutes}T'  # T = minutes

        aggregated = df.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'timestamp': 'first'
        }).dropna()

        # Reset index
        aggregated.reset_index(inplace=True)

        # Keep only last 250 bars
        if len(aggregated) > self.MAX_BARS_PER_TIMEFRAME:
            aggregated = aggregated.tail(self.MAX_BARS_PER_TIMEFRAME)

        return aggregated

    def get_1m_data(self, symbol: str, exchange: str = "gate.io",
                    lookback_bars: int = 2000) -> pd.DataFrame:
        """
        Get 1m data from database

        Args:
            symbol: Trading pair (e.g., BTC_USDT)
            exchange: Exchange name
            lookback_bars: Number of 1m bars to fetch

        Returns:
            DataFrame with 1m OHLCV data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT timestamp, datetime, open, high, low, close, volume
                FROM klines
                WHERE symbol = ? AND exchange = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(symbol, exchange, lookback_bars))
            conn.close()

            if df.empty:
                return pd.DataFrame()

            # Sort ascending
            df = df.sort_values('timestamp').reset_index(drop=True)

            return df

        except Exception as e:
            logger.error(f"Error fetching 1m data for {symbol}: {e}")
            return pd.DataFrame()

    def process_symbol(self, symbol: str, exchange: str = "gate.io") -> Dict[str, int]:
        """
        Process single symbol: aggregate to all timeframes and save

        Args:
            symbol: Trading pair
            exchange: Exchange name

        Returns:
            Dictionary with timeframe -> bars count
        """
        results = {}

        # Get 1m data (fetch enough for largest timeframe)
        # For 1d with 250 bars, need 250*1440 = 360,000 1m bars
        # But we'll use a reasonable lookback (2000 bars = ~33 hours)
        df_1m = self.get_1m_data(symbol, exchange, lookback_bars=2000)

        if df_1m.empty:
            logger.warning(f"No 1m data for {symbol}")
            return results

        # Save 1m data itself
        self._save_parquet(df_1m.tail(self.MAX_BARS_PER_TIMEFRAME), symbol, '1m')
        results['1m'] = len(df_1m.tail(self.MAX_BARS_PER_TIMEFRAME))

        # Aggregate to each timeframe
        for tf_name, tf_minutes in self.TIMEFRAMES.items():
            if tf_name == '1m':  # Already saved
                continue

            df_aggregated = self.aggregate_candles(df_1m, tf_minutes)

            if not df_aggregated.empty:
                self._save_parquet(df_aggregated, symbol, tf_name)
                results[tf_name] = len(df_aggregated)
            else:
                results[tf_name] = 0

        return results

    def _save_parquet(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """
        Save DataFrame to Parquet file (overwrites existing)

        Args:
            df: DataFrame to save
            symbol: Trading pair
            timeframe: Timeframe name (e.g., '5m')
        """
        filename = f"{symbol}_{timeframe}.parquet"
        filepath = self.output_dir / filename

        try:
            df.to_parquet(filepath, engine='pyarrow', compression='snappy', index=False)
            logger.debug(f"Saved {len(df)} bars to {filename}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")

    def load_timeframe_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Load timeframe data from Parquet file

        Args:
            symbol: Trading pair
            timeframe: Timeframe name

        Returns:
            DataFrame or None if file doesn't exist
        """
        filename = f"{symbol}_{timeframe}.parquet"
        filepath = self.output_dir / filename

        if not filepath.exists():
            return None

        try:
            df = pd.read_parquet(filepath, engine='pyarrow')
            return df
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return None

    def process_all_symbols(self, exchange: str = "gate.io") -> Dict[str, Dict[str, int]]:
        """
        Process all symbols in database

        Args:
            exchange: Exchange name

        Returns:
            Dictionary with symbol -> timeframe -> bars count
        """
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT DISTINCT symbol FROM klines WHERE exchange = ?"
            symbols_df = pd.read_sql_query(query, conn, params=(exchange,))
            conn.close()

            results = {}
            total_symbols = len(symbols_df)

            logger.info(f"Processing {total_symbols} symbols...")

            for idx, symbol in enumerate(symbols_df['symbol'], 1):
                logger.info(f"[{idx}/{total_symbols}] Processing {symbol}...")
                symbol_results = self.process_symbol(symbol, exchange)
                results[symbol] = symbol_results

                # Log summary
                bars_str = ', '.join([f"{tf}:{count}" for tf, count in symbol_results.items()])
                logger.info(f"  ✅ {symbol}: {bars_str}")

            return results

        except Exception as e:
            logger.error(f"Error processing all symbols: {e}")
            return {}

    def get_available_symbols(self, timeframe: str = '1m') -> List[str]:
        """
        Get list of symbols that have data for given timeframe

        Args:
            timeframe: Timeframe name

        Returns:
            List of symbol names
        """
        pattern = f"*_{timeframe}.parquet"
        files = list(self.output_dir.glob(pattern))

        symbols = [f.stem.replace(f"_{timeframe}", "") for f in files]
        return sorted(symbols)


def test_aggregator():
    """Test multi-timeframe aggregator"""
    print("=" * 80)
    print("MULTI-TIMEFRAME DATA AGGREGATOR TEST")
    print("=" * 80)

    aggregator = TimeframeAggregator()

    # Test single symbol
    print("\n1. Testing BTC_USDT aggregation...")
    results = aggregator.process_symbol("BTC_USDT", "gate.io")

    if results:
        print(f"✅ BTC_USDT processed:")
        for tf, bars in results.items():
            print(f"   {tf}: {bars} bars")

        # Test loading
        print("\n2. Testing data loading...")
        df_5m = aggregator.load_timeframe_data("BTC_USDT", "5m")
        if df_5m is not None:
            print(f"✅ Loaded 5m data: {len(df_5m)} bars")
            print(df_5m.tail())

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_aggregator()
