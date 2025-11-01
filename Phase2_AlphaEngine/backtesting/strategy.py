"""
Strategy Base Class
Define trading strategies for backtesting
"""

from typing import Dict, List, Optional
from datetime import datetime


class Strategy:
    """
    Base class for trading strategies
    """

    def __init__(self, name: str = "BaseStrategy"):
        """
        Initialize strategy

        Args:
            name: Strategy name
        """
        self.name = name
        self.position = 0  # 0 = flat, 1 = long, -1 = short
        self.entry_price = 0
        self.trades = []

    def on_bar(self, bar: Dict) -> Optional[str]:
        """
        Called on each new bar

        Args:
            bar: OHLCV bar data with indicators

        Returns:
            'buy', 'sell', or None
        """
        raise NotImplementedError("Strategy must implement on_bar()")

    def should_buy(self, bar: Dict) -> bool:
        """Check if should buy"""
        return False

    def should_sell(self, bar: Dict) -> bool:
        """Check if should sell"""
        return False


class RSI_Strategy(Strategy):
    """
    Simple RSI strategy
    Buy when RSI < 30, Sell when RSI > 70
    """

    def __init__(self, rsi_buy=30, rsi_sell=70):
        super().__init__("RSI_Strategy")
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell

    def on_bar(self, bar: Dict) -> Optional[str]:
        """Execute strategy logic"""
        rsi = bar.get('rsi_14')

        if rsi is None:
            return None

        # Buy signal
        if self.position == 0 and rsi < self.rsi_buy:
            return 'buy'

        # Sell signal
        if self.position == 1 and rsi > self.rsi_sell:
            return 'sell'

        return None


class MACD_Strategy(Strategy):
    """
    MACD crossover strategy
    """

    def __init__(self):
        super().__init__("MACD_Strategy")
        self.prev_macd = None
        self.prev_signal = None

    def on_bar(self, bar: Dict) -> Optional[str]:
        """Execute strategy logic"""
        macd_data = bar.get('macd')

        if macd_data is None or not isinstance(macd_data, dict):
            return None

        macd = macd_data.get('macd')
        signal = macd_data.get('signal')

        if macd is None or signal is None:
            return None

        if self.prev_macd is not None:
            # Bullish crossover
            if self.position == 0 and self.prev_macd < self.prev_signal and macd > signal:
                self.prev_macd = macd
                self.prev_signal = signal
                return 'buy'

            # Bearish crossover
            if self.position == 1 and self.prev_macd > self.prev_signal and macd < signal:
                self.prev_macd = macd
                self.prev_signal = signal
                return 'sell'

        self.prev_macd = macd
        self.prev_signal = signal
        return None


class BollingerBands_Strategy(Strategy):
    """
    Bollinger Bands mean reversion strategy
    """

    def __init__(self):
        super().__init__("BB_MeanReversion")

    def on_bar(self, bar: Dict) -> Optional[str]:
        """Execute strategy logic"""
        bb = bar.get('bb_20')
        close = bar.get('close')

        if bb is None or close is None or not isinstance(bb, dict):
            return None

        lower = bb.get('lower')
        upper = bb.get('upper')

        if lower is None or upper is None:
            return None

        # Buy when price touches lower band
        if self.position == 0 and close <= lower:
            return 'buy'

        # Sell when price touches upper band
        if self.position == 1 and close >= upper:
            return 'sell'

        return None


class Momentum_Strategy(Strategy):
    """
    Multi-indicator momentum strategy
    """

    def __init__(self):
        super().__init__("Momentum_Combo")

    def on_bar(self, bar: Dict) -> Optional[str]:
        """Execute strategy logic"""
        rsi = bar.get('rsi_14')
        macd_data = bar.get('macd')

        if rsi is None or macd_data is None:
            return None

        macd = macd_data.get('macd') if isinstance(macd_data, dict) else None

        if macd is None:
            return None

        # Buy: RSI oversold + MACD positive
        if self.position == 0 and rsi < 40 and macd > 0:
            return 'buy'

        # Sell: RSI overbought + MACD negative
        if self.position == 1 and rsi > 60 and macd < 0:
            return 'sell'

        return None
