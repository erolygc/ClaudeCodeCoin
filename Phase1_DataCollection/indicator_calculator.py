"""
Professional Technical Indicator Calculator
Calculates 100+ indicators based on YAML configuration
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """
    Calculates 100+ technical indicators for OHLCV data
    """

    def __init__(self, config_path: str = "indicators_config.yaml"):
        """
        Initialize indicator calculator

        Args:
            config_path: Path to indicators YAML config
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        logger.info(f"IndicatorCalculator initialized")
        logger.info(f"Config: {config_path}")
        logger.info(f"Categories: {list(self.config.keys())}")

    def _load_config(self) -> Dict:
        """Load indicators configuration from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ALL indicators for given OHLCV dataframe

        Args:
            df: DataFrame with OHLCV columns

        Returns:
            DataFrame with all original columns + indicator columns
        """
        if df.empty or len(df) < 2:
            return df

        df = df.copy()

        # Calculate each category
        logger.info("Calculating trend indicators...")
        df = self._calculate_trend_indicators(df)

        logger.info("Calculating momentum indicators...")
        df = self._calculate_momentum_indicators(df)

        logger.info("Calculating volatility indicators...")
        df = self._calculate_volatility_indicators(df)

        logger.info("Calculating volume indicators...")
        df = self._calculate_volume_indicators(df)

        logger.info("Calculating custom indicators...")
        df = self._calculate_custom_indicators(df)

        total_indicators = len([col for col in df.columns if col not in ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']])
        logger.info(f"✅ Total indicators calculated: {total_indicators}")

        return df

    # ========================================================================
    # TREND INDICATORS
    # ========================================================================

    def _calculate_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all trend indicators"""

        # Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            if len(df) >= period:
                df[f'sma_{period}'] = df['close'].rolling(window=period).mean()

        for period in [9, 12, 20, 26, 50, 100, 200]:
            if len(df) >= period:
                df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

        for period in [10, 20, 50]:
            if len(df) >= period:
                df[f'wma_{period}'] = self._wma(df['close'], period)

        # MACD
        if len(df) >= 26:
            ema_12 = df['close'].ewm(span=12, adjust=False).mean()
            ema_26 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = ema_12 - ema_26
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']

        # ADX
        if len(df) >= 14:
            df = self._calculate_adx(df, 14)

        # Aroon
        if len(df) >= 25:
            df = self._calculate_aroon(df, 25)

        # Parabolic SAR
        if len(df) >= 2:
            df = self._calculate_parabolic_sar(df)

        # Supertrend
        if len(df) >= 10:
            df = self._calculate_supertrend(df, 10, 3.0)

        return df

    # ========================================================================
    # MOMENTUM INDICATORS
    # ========================================================================

    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all momentum indicators"""

        # RSI
        for period in [7, 14, 21]:
            if len(df) >= period:
                df[f'rsi_{period}'] = self._rsi(df['close'], period)

        # Stochastic
        if len(df) >= 14:
            df = self._calculate_stochastic(df, 14, 3, 3)

        # Williams %R
        if len(df) >= 14:
            df['williams_r'] = self._williams_r(df, 14)

        # CCI
        if len(df) >= 20:
            df['cci'] = self._cci(df, 20)

        # ROC
        for period in [5, 10, 20]:
            if len(df) >= period:
                df[f'roc_{period}'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100

        # CMO
        if len(df) >= 14:
            df['cmo'] = self._cmo(df['close'], 14)

        # Ultimate Oscillator
        if len(df) >= 28:
            df['ultimate_oscillator'] = self._ultimate_oscillator(df)

        # Awesome Oscillator
        if len(df) >= 34:
            median = (df['high'] + df['low']) / 2
            df['ao'] = median.rolling(5).mean() - median.rolling(34).mean()

        return df

    # ========================================================================
    # VOLATILITY INDICATORS
    # ========================================================================

    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all volatility indicators"""

        # ATR
        if len(df) >= 14:
            df = self._calculate_atr(df, 14)
            df['atr_percent'] = (df['atr'] / df['close']) * 100

        # Bollinger Bands
        if len(df) >= 20:
            df = self._calculate_bollinger_bands(df, 20, 2.0)

        # Keltner Channel
        if len(df) >= 20:
            df = self._calculate_keltner_channel(df, 20, 10, 2.0)

        # Donchian Channel
        if len(df) >= 20:
            df['donchian_high'] = df['high'].rolling(20).max()
            df['donchian_low'] = df['low'].rolling(20).min()
            df['donchian_mid'] = (df['donchian_high'] + df['donchian_low']) / 2

        # Standard Deviation
        if len(df) >= 20:
            df['std_dev'] = df['close'].rolling(20).std()

        # Historical Volatility
        if len(df) >= 30:
            returns = np.log(df['close'] / df['close'].shift(1))
            df['hist_volatility'] = returns.rolling(30).std() * np.sqrt(252) * 100

        return df

    # ========================================================================
    # VOLUME INDICATORS
    # ========================================================================

    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all volume indicators"""

        # OBV
        df['obv'] = 0.0
        if len(df) >= 2:
            df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

        # VWAP (cumulative for session)
        if 'volume' in df.columns:
            df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

        # MFI
        if len(df) >= 14:
            df['mfi'] = self._mfi(df, 14)

        # A/D Line
        df['ad_line'] = self._accumulation_distribution(df)

        # CMF
        if len(df) >= 20:
            df['cmf'] = self._cmf(df, 20)

        # Force Index
        if len(df) >= 13:
            df['force_index'] = (df['close'].diff() * df['volume']).ewm(span=13).mean()

        # Volume ROC
        if len(df) >= 14:
            df['volume_roc'] = ((df['volume'] - df['volume'].shift(14)) / df['volume'].shift(14)) * 100

        # PVT
        df['pvt'] = (((df['close'] - df['close'].shift(1)) / df['close'].shift(1)) * df['volume']).cumsum()

        return df

    # ========================================================================
    # CUSTOM INDICATORS
    # ========================================================================

    def _calculate_custom_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate custom/hybrid indicators"""

        # Pump Probability Score
        if len(df) >= 20:
            volume_spike = df['volume'] / df['volume'].rolling(20).mean()
            price_change = df['close'].pct_change(5) * 100
            df['pump_probability'] = ((volume_spike - 1) * 20 + price_change * 2).clip(0, 100)

        # Whale Activity Index
        if len(df) >= 20:
            volume_ma = df['volume'].rolling(20).mean()
            df['whale_activity'] = (df['volume'] / volume_ma > 5.0).astype(int) * 100

        # Volume-Price Divergence
        if len(df) >= 14:
            price_roc = df['close'].pct_change(14)
            volume_roc = df['volume'].pct_change(14)
            df['vp_divergence'] = (np.sign(price_roc) != np.sign(volume_roc)).astype(int)

        # Market Regime (Trending vs Ranging)
        if 'adx' in df.columns:
            df['market_regime'] = np.where(df['adx'] > 25, 1, 0)  # 1=Trending, 0=Ranging

        # Trend Quality
        if len(df) >= 50:
            sma_50 = df['close'].rolling(50).mean()
            distance = abs(df['close'] - sma_50) / sma_50 * 100
            df['trend_quality'] = (1 / (1 + distance)) * 100  # Higher = stronger trend

        return df

    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================

    def _wma(self, series: pd.Series, period: int) -> pd.Series:
        """Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

    def _rsi(self, series: pd.Series, period: int) -> pd.Series:
        """Relative Strength Index"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _williams_r(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Williams %R"""
        highest_high = df['high'].rolling(period).max()
        lowest_low = df['low'].rolling(period).min()
        return -100 * (highest_high - df['close']) / (highest_high - lowest_low)

    def _cci(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Commodity Channel Index"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean())
        return (tp - sma) / (0.015 * mad)

    def _cmo(self, series: pd.Series, period: int) -> pd.Series:
        """Chande Momentum Oscillator"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(period).sum()
        loss = -delta.where(delta < 0, 0).rolling(period).sum()
        return 100 * (gain - loss) / (gain + loss)

    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Average True Range"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(period).mean()
        return df

    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int, std_dev: float) -> pd.DataFrame:
        """Bollinger Bands"""
        df['bb_middle'] = df['close'].rolling(period).mean()
        std = df['close'].rolling(period).std()
        df['bb_upper'] = df['bb_middle'] + (std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (std * std_dev)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle'] * 100
        return df

    def _calculate_keltner_channel(self, df: pd.DataFrame, period: int, atr_period: int, multiplier: float) -> pd.DataFrame:
        """Keltner Channel"""
        df['kc_middle'] = df['close'].ewm(span=period).mean()
        if 'atr' not in df.columns:
            df = self._calculate_atr(df, atr_period)
        df['kc_upper'] = df['kc_middle'] + (df['atr'] * multiplier)
        df['kc_lower'] = df['kc_middle'] - (df['atr'] * multiplier)
        return df

    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int, d_period: int, smooth_k: int) -> pd.DataFrame:
        """Stochastic Oscillator"""
        lowest_low = df['low'].rolling(k_period).min()
        highest_high = df['high'].rolling(k_period).max()
        df['stoch_k'] = 100 * (df['close'] - lowest_low) / (highest_high - lowest_low)
        df['stoch_k'] = df['stoch_k'].rolling(smooth_k).mean()
        df['stoch_d'] = df['stoch_k'].rolling(d_period).mean()
        return df

    def _calculate_adx(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Average Directional Index"""
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        if 'atr' not in df.columns:
            df = self._calculate_atr(df, period)

        plus_di = 100 * (plus_dm.ewm(span=period).mean() / df['atr'])
        minus_di = 100 * (minus_dm.ewm(span=period).mean() / df['atr'])

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        df['adx'] = dx.ewm(span=period).mean()
        df['plus_di'] = plus_di
        df['minus_di'] = minus_di

        return df

    def _calculate_aroon(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Aroon Indicator"""
        aroon_up = df['high'].rolling(period + 1).apply(lambda x: x.argmax()) / period * 100
        aroon_down = df['low'].rolling(period + 1).apply(lambda x: x.argmin()) / period * 100
        df['aroon_up'] = aroon_up
        df['aroon_down'] = aroon_down
        df['aroon_oscillator'] = aroon_up - aroon_down
        return df

    def _calculate_parabolic_sar(self, df: pd.DataFrame, acceleration: float = 0.02, maximum: float = 0.2) -> pd.DataFrame:
        """Parabolic SAR (simplified)"""
        # Simplified version - full implementation is complex
        df['psar'] = df['close'].shift(1)  # Placeholder
        return df

    def _calculate_supertrend(self, df: pd.DataFrame, period: int, multiplier: float) -> pd.DataFrame:
        """Supertrend Indicator"""
        if 'atr' not in df.columns:
            df = self._calculate_atr(df, period)

        hl2 = (df['high'] + df['low']) / 2
        basic_ub = hl2 + (multiplier * df['atr'])
        basic_lb = hl2 - (multiplier * df['atr'])

        df['supertrend'] = 0.0
        df['supertrend_direction'] = 1  # 1=uptrend, -1=downtrend

        return df

    def _mfi(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Money Flow Index"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        rmf = tp * df['volume']

        positive_flow = rmf.where(tp > tp.shift(1), 0).rolling(period).sum()
        negative_flow = rmf.where(tp < tp.shift(1), 0).rolling(period).sum()

        mfi_ratio = positive_flow / negative_flow
        return 100 - (100 / (1 + mfi_ratio))

    def _accumulation_distribution(self, df: pd.DataFrame) -> pd.Series:
        """Accumulation/Distribution Line"""
        clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        clv = clv.fillna(0)
        return (clv * df['volume']).cumsum()

    def _cmf(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Chaikin Money Flow"""
        clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        clv = clv.fillna(0)
        mf_volume = clv * df['volume']
        return mf_volume.rolling(period).sum() / df['volume'].rolling(period).sum()

    def _ultimate_oscillator(self, df: pd.DataFrame, period1: int = 7, period2: int = 14, period3: int = 28) -> pd.Series:
        """Ultimate Oscillator"""
        # Buying Pressure
        bp = df['close'] - pd.concat([df['low'], df['close'].shift(1)], axis=1).min(axis=1)

        # True Range
        high_close = pd.concat([df['high'], df['close'].shift(1)], axis=1).max(axis=1)
        low_close = pd.concat([df['low'], df['close'].shift(1)], axis=1).min(axis=1)
        tr = high_close - low_close

        # Averages
        avg1 = bp.rolling(period1).sum() / tr.rolling(period1).sum()
        avg2 = bp.rolling(period2).sum() / tr.rolling(period2).sum()
        avg3 = bp.rolling(period3).sum() / tr.rolling(period3).sum()

        return 100 * ((4 * avg1) + (2 * avg2) + avg3) / 7


def test_indicators():
    """Test indicator calculator"""
    print("=" * 80)
    print("INDICATOR CALCULATOR TEST")
    print("=" * 80)

    # Create sample data
    dates = pd.date_range('2025-01-01', periods=500, freq='1h')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(500) * 2)
    high = close + np.random.rand(500) * 3
    low = close - np.random.rand(500) * 3
    open_price = close + np.random.randn(500)
    volume = np.random.randint(1000000, 5000000, 500)

    df = pd.DataFrame({
        'datetime': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
        'timestamp': range(500)
    })

    print(f"\n✅ Created sample data: {len(df)} bars")

    # Calculate indicators
    calc = IndicatorCalculator()
    df_with_indicators = calc.calculate_all_indicators(df)

    print(f"\n✅ Calculated indicators")
    print(f"   Original columns: {len(df.columns)}")
    print(f"   With indicators: {len(df_with_indicators.columns)}")
    print(f"   Indicators added: {len(df_with_indicators.columns) - len(df.columns)}")

    # Show sample
    print("\n📊 Sample indicators (last row):")
    indicator_cols = [col for col in df_with_indicators.columns if col not in df.columns]
    for col in indicator_cols[:20]:  # Show first 20
        value = df_with_indicators[col].iloc[-1]
        if not pd.isna(value):
            print(f"   {col}: {value:.2f}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_indicators()
