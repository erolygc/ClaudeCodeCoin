"""
Data Collectors Module
Collects data from various sources: exchanges, social media, on-chain data
"""

from .binance_collector import BinanceKlineCollector

__all__ = ["BinanceKlineCollector"]
