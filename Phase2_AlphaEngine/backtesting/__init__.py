"""
ClaudeCodeCoin - Backtesting Framework
Test trading strategies on historical data
"""

from .backtester import Backtester
from .strategy import Strategy

__all__ = ["Backtester", "Strategy"]
