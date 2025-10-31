"""
Basic Technical Indicators
Implements common technical analysis indicators without external dependencies
"""

import math
from typing import List, Dict, Tuple, Optional


def calculate_sma(prices: List[float], period: int) -> Optional[float]:
    """
    Simple Moving Average

    Args:
        prices: List of prices (most recent last)
        period: Number of periods

    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < period:
        return None

    return sum(prices[-period:]) / period


def calculate_ema(prices: List[float], period: int, prev_ema: Optional[float] = None) -> Optional[float]:
    """
    Exponential Moving Average

    Args:
        prices: List of prices (most recent last)
        period: Number of periods
        prev_ema: Previous EMA value (if available)

    Returns:
        EMA value or None if insufficient data
    """
    if len(prices) < 1:
        return None

    multiplier = 2 / (period + 1)

    if prev_ema is None:
        # Initialize with SMA
        if len(prices) < period:
            return None
        prev_ema = calculate_sma(prices[-period:], period)

    current_price = prices[-1]
    ema = (current_price * multiplier) + (prev_ema * (1 - multiplier))

    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Relative Strength Index

    Args:
        prices: List of prices (most recent last)
        period: RSI period (default 14)

    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if len(prices) < period + 1:
        return None

    # Calculate price changes
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]

    # Separate gains and losses
    gains = [change if change > 0 else 0 for change in changes[-period:]]
    losses = [-change if change < 0 else 0 for change in changes[-period:]]

    # Calculate average gain and loss
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    prev_emas: Optional[Dict[str, float]] = None
) -> Optional[Dict[str, float]]:
    """
    MACD (Moving Average Convergence Divergence)

    Args:
        prices: List of prices (most recent last)
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)
        prev_emas: Previous EMA values for continuation

    Returns:
        Dict with macd, signal, histogram or None if insufficient data
    """
    if len(prices) < slow_period:
        return None

    # Calculate EMAs
    if prev_emas is None:
        prev_emas = {}

    fast_ema = calculate_ema(prices, fast_period, prev_emas.get('fast_ema'))
    slow_ema = calculate_ema(prices, slow_period, prev_emas.get('slow_ema'))

    if fast_ema is None or slow_ema is None:
        return None

    macd_line = fast_ema - slow_ema

    # For signal line, we need MACD history
    # Simplified: return MACD without signal for now
    # Full implementation would need MACD history for signal EMA

    return {
        'macd': macd_line,
        'fast_ema': fast_ema,
        'slow_ema': slow_ema,
        'signal': None,  # Would need MACD history
        'histogram': None
    }


def calculate_bollinger_bands(
    prices: List[float],
    period: int = 20,
    std_dev: float = 2.0
) -> Optional[Dict[str, float]]:
    """
    Bollinger Bands

    Args:
        prices: List of prices (most recent last)
        period: Moving average period (default 20)
        std_dev: Standard deviation multiplier (default 2.0)

    Returns:
        Dict with upper, middle, lower bands or None if insufficient data
    """
    if len(prices) < period:
        return None

    # Middle band (SMA)
    middle_band = calculate_sma(prices, period)

    if middle_band is None:
        return None

    # Calculate standard deviation
    recent_prices = prices[-period:]
    variance = sum((price - middle_band) ** 2 for price in recent_prices) / period
    std = math.sqrt(variance)

    # Upper and lower bands
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)

    return {
        'upper': upper_band,
        'middle': middle_band,
        'lower': lower_band,
        'std': std
    }


def calculate_atr(
    high: List[float],
    low: List[float],
    close: List[float],
    period: int = 14
) -> Optional[float]:
    """
    Average True Range

    Args:
        high: List of high prices
        low: List of low prices
        close: List of close prices
        period: ATR period (default 14)

    Returns:
        ATR value or None if insufficient data
    """
    if len(high) < period + 1 or len(low) < period + 1 or len(close) < period + 1:
        return None

    true_ranges = []

    for i in range(1, len(close)):
        h = high[i]
        l = low[i]
        prev_close = close[i-1]

        tr = max(
            h - l,
            abs(h - prev_close),
            abs(l - prev_close)
        )
        true_ranges.append(tr)

    if len(true_ranges) < period:
        return None

    atr = sum(true_ranges[-period:]) / period
    return atr


def calculate_obv(
    close: List[float],
    volume: List[float]
) -> Optional[float]:
    """
    On-Balance Volume

    Args:
        close: List of close prices
        volume: List of volume values

    Returns:
        OBV value or None if insufficient data
    """
    if len(close) < 2 or len(volume) < 2:
        return None

    obv = 0

    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            obv += volume[i]
        elif close[i] < close[i-1]:
            obv -= volume[i]
        # If equal, OBV stays the same

    return obv


def calculate_stochastic(
    high: List[float],
    low: List[float],
    close: List[float],
    period: int = 14
) -> Optional[Dict[str, float]]:
    """
    Stochastic Oscillator

    Args:
        high: List of high prices
        low: List of low prices
        close: List of close prices
        period: Stochastic period (default 14)

    Returns:
        Dict with %K and %D or None if insufficient data
    """
    if len(high) < period or len(low) < period or len(close) < period:
        return None

    recent_high = max(high[-period:])
    recent_low = min(low[-period:])
    current_close = close[-1]

    if recent_high == recent_low:
        k_percent = 50.0
    else:
        k_percent = ((current_close - recent_low) / (recent_high - recent_low)) * 100

    return {
        'k': k_percent,
        'd': None,  # Would need %K history for %D (SMA of %K)
        'high': recent_high,
        'low': recent_low
    }


def calculate_all_indicators(
    prices: List[float],
    high: Optional[List[float]] = None,
    low: Optional[List[float]] = None,
    volume: Optional[List[float]] = None
) -> Dict[str, any]:
    """
    Calculate all basic indicators at once

    Args:
        prices: List of close prices
        high: List of high prices (optional)
        low: List of low prices (optional)
        volume: List of volume (optional)

    Returns:
        Dict with all indicator values
    """
    indicators = {}

    # Moving averages
    indicators['sma_20'] = calculate_sma(prices, 20)
    indicators['sma_50'] = calculate_sma(prices, 50)
    indicators['sma_200'] = calculate_sma(prices, 200)
    indicators['ema_12'] = calculate_ema(prices, 12)
    indicators['ema_26'] = calculate_ema(prices, 26)

    # RSI
    indicators['rsi_14'] = calculate_rsi(prices, 14)

    # MACD
    indicators['macd'] = calculate_macd(prices)

    # Bollinger Bands
    indicators['bb_20'] = calculate_bollinger_bands(prices, 20)

    # ATR (if high/low available)
    if high and low:
        indicators['atr_14'] = calculate_atr(high, low, prices, 14)
        indicators['stochastic_14'] = calculate_stochastic(high, low, prices, 14)

    # OBV (if volume available)
    if volume:
        indicators['obv'] = calculate_obv(prices, volume)

    return indicators
