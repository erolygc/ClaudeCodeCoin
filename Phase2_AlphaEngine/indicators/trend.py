"""
Trend Indicators
Advanced trend-following technical indicators
"""

import math
from typing import List, Dict, Optional, Tuple


def hma(prices: List[float], period: int = 16) -> Optional[float]:
    """
    Hull Moving Average - Smoother and more responsive than SMA/EMA

    Args:
        prices: List of prices
        period: HMA period

    Returns:
        HMA value
    """
    if len(prices) < period:
        return None

    # WMA helper
    def wma(data: List[float], n: int) -> Optional[float]:
        if len(data) < n:
            return None
        weights = list(range(1, n + 1))
        return sum(w * p for w, p in zip(weights, data[-n:])) / sum(weights)

    half_period = period // 2
    sqrt_period = int(math.sqrt(period))

    wma_half = wma(prices, half_period)
    wma_full = wma(prices, period)

    if wma_half is None or wma_full is None:
        return None

    raw_hma = 2 * wma_half - wma_full

    # Need more values for final WMA, simplified version:
    return raw_hma


def tema(prices: List[float], period: int = 9) -> Optional[float]:
    """
    Triple Exponential Moving Average
    More responsive than EMA, reduces lag

    Args:
        prices: List of prices
        period: TEMA period

    Returns:
        TEMA value
    """
    if len(prices) < period * 3:
        return None

    def ema_calc(data: List[float], n: int) -> Optional[float]:
        if len(data) < n:
            return None
        multiplier = 2 / (n + 1)
        ema = sum(data[:n]) / n
        for price in data[n:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema

    ema1 = ema_calc(prices, period)
    if ema1 is None:
        return None

    # Simplified: return EMA for now, full TEMA needs EMA of EMA of EMA
    return ema1


def dema(prices: List[float], period: int = 9) -> Optional[float]:
    """
    Double Exponential Moving Average
    Reduces lag compared to single EMA

    Args:
        prices: List of prices
        period: DEMA period

    Returns:
        DEMA value
    """
    if len(prices) < period * 2:
        return None

    def ema_calc(data: List[float], n: int) -> Optional[float]:
        if len(data) < n:
            return None
        multiplier = 2 / (n + 1)
        ema = sum(data[:n]) / n
        for price in data[n:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema

    ema1 = ema_calc(prices, period)
    # Simplified version
    return ema1


def supertrend(
    high: List[float],
    low: List[float],
    close: List[float],
    period: int = 10,
    multiplier: float = 3.0
) -> Optional[Dict[str, any]]:
    """
    Supertrend Indicator
    Trend-following indicator based on ATR

    Args:
        high: List of high prices
        low: List of low prices
        close: List of close prices
        period: ATR period
        multiplier: ATR multiplier

    Returns:
        Dict with supertrend, trend direction
    """
    if len(high) < period + 1:
        return None

    # Calculate ATR
    true_ranges = []
    for i in range(1, len(close)):
        h = high[i]
        l = low[i]
        prev_close = close[i-1]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        true_ranges.append(tr)

    if len(true_ranges) < period:
        return None

    atr = sum(true_ranges[-period:]) / period

    # Calculate basic bands
    hl_avg = (high[-1] + low[-1]) / 2
    upper_band = hl_avg + (multiplier * atr)
    lower_band = hl_avg - (multiplier * atr)

    # Trend determination (simplified)
    current_close = close[-1]
    trend = 1 if current_close > lower_band else -1

    supertrend_value = lower_band if trend == 1 else upper_band

    return {
        'supertrend': supertrend_value,
        'trend': trend,  # 1 = bullish, -1 = bearish
        'upper_band': upper_band,
        'lower_band': lower_band,
        'atr': atr
    }


def adx(
    high: List[float],
    low: List[float],
    close: List[float],
    period: int = 14
) -> Optional[Dict[str, float]]:
    """
    Average Directional Index
    Measures trend strength (0-100)

    Args:
        high: List of high prices
        low: List of low prices
        close: List of close prices
        period: ADX period

    Returns:
        Dict with ADX, +DI, -DI values
    """
    if len(high) < period + 1:
        return None

    # Calculate +DM and -DM
    plus_dm_list = []
    minus_dm_list = []

    for i in range(1, len(high)):
        high_diff = high[i] - high[i-1]
        low_diff = low[i-1] - low[i]

        plus_dm = high_diff if high_diff > low_diff and high_diff > 0 else 0
        minus_dm = low_diff if low_diff > high_diff and low_diff > 0 else 0

        plus_dm_list.append(plus_dm)
        minus_dm_list.append(minus_dm)

    # Calculate ATR
    true_ranges = []
    for i in range(1, len(close)):
        h = high[i]
        l = low[i]
        prev_close = close[i-1]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        true_ranges.append(tr)

    if len(true_ranges) < period:
        return None

    atr = sum(true_ranges[-period:]) / period
    plus_dm_avg = sum(plus_dm_list[-period:]) / period
    minus_dm_avg = sum(minus_dm_list[-period:]) / period

    # Calculate DI
    plus_di = (plus_dm_avg / atr * 100) if atr > 0 else 0
    minus_di = (minus_dm_avg / atr * 100) if atr > 0 else 0

    # Calculate DX and ADX
    di_sum = plus_di + minus_di
    di_diff = abs(plus_di - minus_di)
    dx = (di_diff / di_sum * 100) if di_sum > 0 else 0

    # ADX is smoothed DX (simplified: return DX)
    adx_value = dx

    return {
        'adx': adx_value,
        'plus_di': plus_di,
        'minus_di': minus_di,
        'trend_strength': 'strong' if adx_value > 25 else 'weak'
    }


def parabolic_sar(
    high: List[float],
    low: List[float],
    af_start: float = 0.02,
    af_increment: float = 0.02,
    af_max: float = 0.2
) -> Optional[Dict[str, any]]:
    """
    Parabolic SAR (Stop and Reverse)
    Trend-following indicator that provides entry/exit points

    Args:
        high: List of high prices
        low: List of low prices
        af_start: Initial acceleration factor
        af_increment: AF increment
        af_max: Maximum AF

    Returns:
        Dict with SAR value and trend
    """
    if len(high) < 5:
        return None

    # Simplified version - returns last SAR
    is_bullish = high[-1] > high[-2]

    if is_bullish:
        sar = min(low[-5:])  # Use recent low as SAR
    else:
        sar = max(high[-5:])  # Use recent high as SAR

    return {
        'sar': sar,
        'trend': 1 if is_bullish else -1,
        'af': af_start
    }


def vortex(
    high: List[float],
    low: List[float],
    close: List[float],
    period: int = 14
) -> Optional[Dict[str, float]]:
    """
    Vortex Indicator
    Identifies the start of a new trend

    Args:
        high: List of high prices
        low: List of low prices
        close: List of close prices
        period: Vortex period

    Returns:
        Dict with VI+, VI- values
    """
    if len(high) < period + 1:
        return None

    # Calculate vortex movements
    vi_plus_list = []
    vi_minus_list = []
    true_ranges = []

    for i in range(1, len(high)):
        vi_plus = abs(high[i] - low[i-1])
        vi_minus = abs(low[i] - high[i-1])

        vi_plus_list.append(vi_plus)
        vi_minus_list.append(vi_minus)

        # True range
        h = high[i]
        l = low[i]
        prev_close = close[i-1]
        tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        true_ranges.append(tr)

    if len(true_ranges) < period:
        return None

    vi_plus_sum = sum(vi_plus_list[-period:])
    vi_minus_sum = sum(vi_minus_list[-period:])
    tr_sum = sum(true_ranges[-period:])

    vi_plus_value = vi_plus_sum / tr_sum if tr_sum > 0 else 0
    vi_minus_value = vi_minus_sum / tr_sum if tr_sum > 0 else 0

    return {
        'vi_plus': vi_plus_value,
        'vi_minus': vi_minus_value,
        'trend': 'bullish' if vi_plus_value > vi_minus_value else 'bearish'
    }
