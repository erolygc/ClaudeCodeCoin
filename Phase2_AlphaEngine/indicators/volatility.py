"""
Volatility Indicators
Measure price volatility and identify potential breakouts
"""

from typing import List, Dict, Optional
import math


def keltner_channels(
    high: List[float],
    low: List[float],
    close: List[float],
    period: int = 20,
    multiplier: float = 2.0
) -> Optional[Dict[str, float]]:
    """Keltner Channels - Volatility-based bands"""
    if len(close) < period:
        return None

    # EMA of close
    ema = sum(close[-period:]) / period

    # ATR calculation
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

    return {
        'upper': ema + (multiplier * atr),
        'middle': ema,
        'lower': ema - (multiplier * atr),
        'atr': atr
    }


def donchian_channels(
    high: List[float],
    low: List[float],
    period: int = 20
) -> Optional[Dict[str, float]]:
    """Donchian Channels - Highest high and lowest low"""
    if len(high) < period or len(low) < period:
        return None

    upper = max(high[-period:])
    lower = min(low[-period:])
    middle = (upper + lower) / 2

    return {
        'upper': upper,
        'middle': middle,
        'lower': lower
    }


def chandelier_exit(
    high: List[float],
    low: List[float],
    close: List[float],
    period: int = 22,
    multiplier: float = 3.0
) -> Optional[Dict[str, float]]:
    """Chandelier Exit - ATR-based stop loss"""
    if len(high) < period + 1:
        return None

    highest_high = max(high[-period:])
    lowest_low = min(low[-period:])

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

    long_stop = highest_high - (multiplier * atr)
    short_stop = lowest_low + (multiplier * atr)

    return {
        'long_stop': long_stop,
        'short_stop': short_stop,
        'atr': atr
    }


def ulcer_index(prices: List[float], period: int = 14) -> Optional[float]:
    """Ulcer Index - Downside volatility measure"""
    if len(prices) < period:
        return None

    squared_drawdowns = []

    for i in range(len(prices) - period, len(prices)):
        highest_since = max(prices[i-period:i+1])
        drawdown = ((prices[i] - highest_since) / highest_since) * 100
        squared_drawdowns.append(drawdown ** 2)

    mean_squared = sum(squared_drawdowns) / len(squared_drawdowns)
    ulcer = math.sqrt(mean_squared)

    return ulcer
