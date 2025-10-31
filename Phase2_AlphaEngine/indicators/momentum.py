"""
Momentum Indicators
Measure the speed and strength of price movements
"""

from typing import List, Dict, Optional


def williams_r(high: List[float], low: List[float], close: List[float], period: int = 14) -> Optional[float]:
    """Williams %R - Momentum oscillator (-100 to 0)"""
    if len(high) < period:
        return None

    highest_high = max(high[-period:])
    lowest_low = min(low[-period:])
    current_close = close[-1]

    if highest_high == lowest_low:
        return -50.0

    williams = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
    return williams


def cci(high: List[float], low: List[float], close: List[float], period: int = 20) -> Optional[float]:
    """Commodity Channel Index"""
    if len(high) < period:
        return None

    typical_prices = [(h + l + c) / 3 for h, l, c in zip(high[-period:], low[-period:], close[-period:])]
    sma_tp = sum(typical_prices) / period
    mean_deviation = sum(abs(tp - sma_tp) for tp in typical_prices) / period

    if mean_deviation == 0:
        return 0

    cci_value = (typical_prices[-1] - sma_tp) / (0.015 * mean_deviation)
    return cci_value


def mfi(high: List[float], low: List[float], close: List[float], volume: List[float], period: int = 14) -> Optional[float]:
    """Money Flow Index - Volume-weighted RSI"""
    if len(close) < period + 1:
        return None

    typical_prices = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
    money_flows = [tp * v for tp, v in zip(typical_prices, volume)]

    positive_flow = 0
    negative_flow = 0

    for i in range(1, len(typical_prices)):
        if typical_prices[i] > typical_prices[i-1]:
            positive_flow += money_flows[i]
        elif typical_prices[i] < typical_prices[i-1]:
            negative_flow += money_flows[i]

    if negative_flow == 0:
        return 100.0

    money_ratio = positive_flow / negative_flow
    mfi_value = 100 - (100 / (1 + money_ratio))

    return mfi_value


def roc(prices: List[float], period: int = 12) -> Optional[float]:
    """Rate of Change - Momentum indicator"""
    if len(prices) < period + 1:
        return None

    current = prices[-1]
    previous = prices[-period-1]

    if previous == 0:
        return 0

    roc_value = ((current - previous) / previous) * 100
    return roc_value


def tsi(prices: List[float], long_period: int = 25, short_period: int = 13) -> Optional[float]:
    """True Strength Index - Double smoothed momentum"""
    if len(prices) < long_period + 1:
        return None

    # Calculate price changes
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]

    if len(changes) < long_period:
        return None

    # Double smoothed momentum (simplified)
    abs_changes = [abs(c) for c in changes]

    momentum = sum(changes[-long_period:]) / long_period
    abs_momentum = sum(abs_changes[-long_period:]) / long_period

    if abs_momentum == 0:
        return 0

    tsi_value = (momentum / abs_momentum) * 100
    return tsi_value


def ultimate_oscillator(
    high: List[float],
    low: List[float],
    close: List[float],
    period1: int = 7,
    period2: int = 14,
    period3: int = 28
) -> Optional[float]:
    """Ultimate Oscillator - Multi-timeframe momentum"""
    if len(close) < period3 + 1:
        return None

    buying_pressures = []
    true_ranges = []

    for i in range(1, len(close)):
        bp = close[i] - min(low[i], close[i-1])
        tr = max(high[i], close[i-1]) - min(low[i], close[i-1])

        buying_pressures.append(bp)
        true_ranges.append(tr)

    def calc_avg(data: List[float], period: int) -> float:
        if len(data) < period:
            return 0
        return sum(data[-period:]) / period if sum(data[-period:]) > 0 else 0

    avg1 = calc_avg(buying_pressures, period1) / (calc_avg(true_ranges, period1) or 1)
    avg2 = calc_avg(buying_pressures, period2) / (calc_avg(true_ranges, period2) or 1)
    avg3 = calc_avg(buying_pressures, period3) / (calc_avg(true_ranges, period3) or 1)

    uo = ((4 * avg1) + (2 * avg2) + avg3) / (4 + 2 + 1) * 100
    return uo
