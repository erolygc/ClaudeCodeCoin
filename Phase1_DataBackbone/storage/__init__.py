"""
Storage module for ClaudeCodeCoin
Handles database connections and data persistence
"""

from .database import TimescaleDBConnection

__all__ = ["TimescaleDBConnection"]
