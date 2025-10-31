"""
Volume Indicators
Volume-based technical indicators
"""

from typing import List, Dict, Optional


def vwap(high: List[float], low: List[float], close: List[float], volume: List[float]) -> Optional[float]:
    """Volume Weighted Average Price"""
    if not volume or len(volume) == 0:
        return None

    typical_prices = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
    vwap_value = sum(tp * v for tp, v in zip(typical_prices, volume)) / sum(volume)

    return vwap_value


def accumulation_distribution(
    high: List[float],
    low: List[float],
    close: List[float],
    volume: List[float]
) -> Optional[float]:
    """Accumulation/Distribution Line"""
    if len(close) < 2:
        return None

    ad_line = 0

    for i in range(len(close)):
        h = high[i]
        l = low[i]
        c = close[i]
        v = volume[i]

        if h == l:
            money_flow_multiplier = 0
        else:
            money_flow_multiplier = ((c - l) - (h - c)) / (h - l)

        money_flow_volume = money_flow_multiplier * v
        ad_line += money_flow_volume

    return ad_line


def chaikin_mf(
    high: List[float],
    low: List[float],
    close: List[float],
    volume: List[float],
    period: int = 20
) -> Optional[float]:
    """Chaikin Money Flow"""
    if len(close) < period:
        return None

    money_flow_volumes = []

    for i in range(len(close)):
        h = high[i]
        l = low[i]
        c = close[i]
        v = volume[i]

        if h == l:
            mfm = 0
        else:
            mfm = ((c - l) - (h - c)) / (h - l)

        money_flow_volumes.append(mfm * v)

    cmf = sum(money_flow_volumes[-period:]) / sum(volume[-period:])
    return cmf


def ease_of_movement(
    high: List[float],
    low: List[float],
    volume: List[float],
    period: int = 14
) -> Optional[float]:
    """Ease of Movement - Relates price change to volume"""
    if len(high) < period + 1:
        return None

    em_values = []

    for i in range(1, len(high)):
        distance = ((high[i] + low[i]) / 2) - ((high[i-1] + low[i-1]) / 2)
        box_ratio = (volume[i] / 1000000) / (high[i] - low[i]) if (high[i] - low[i]) > 0 else 0

        em = distance / box_ratio if box_ratio > 0 else 0
        em_values.append(em)

    if len(em_values) < period:
        return None

    # Simple moving average of EM
    ease_of_movement_value = sum(em_values[-period:]) / period
    return ease_of_movement_value


def force_index(close: List[float], volume: List[float], period: int = 13) -> Optional[float]:
    """Force Index - Combines price and volume"""
    if len(close) < period + 1:
        return None

    force_values = []

    for i in range(1, len(close)):
        force = (close[i] - close[i-1]) * volume[i]
        force_values.append(force)

    if len(force_values) < period:
        return None

    # EMA of force
    multiplier = 2 / (period + 1)
    ema = sum(force_values[:period]) / period

    for force in force_values[period:]:
        ema = (force * multiplier) + (ema * (1 - multiplier))

    return ema
