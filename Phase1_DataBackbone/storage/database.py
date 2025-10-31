"""
Database module for TimescaleDB connection and operations
Handles connection pooling, queries, and data insertion
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool

import sys
sys.path.append(str(__file__ + "/../../.."))

from Phase1_DataBackbone.utils import Config


class TimescaleDBConnection:
    """
    Manages connection to TimescaleDB with connection pooling
    """

    _instance: Optional["TimescaleDBConnection"] = None
    _engine: Optional[Engine] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._initialize_connection()

    def _initialize_connection(self):
        """Initialize database connection with pooling"""
        config = Config()

        # Get database configuration
        db_host = config.get("database.host", "localhost")
        db_port = config.get("database.port", 5432)
        db_name = config.get("database.name", "ccc_trading")
        db_user = config.get("database.user", "ccc_user")
        db_password = config.get_secret("database_password")

        if not db_password:
            logger.error("Database password not found in secrets")
            raise ValueError("Database password not configured")

        # Build connection URL
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        # Get pool configuration
        pool_size = config.get("database.pool_size", 10)
        max_overflow = config.get("database.max_overflow", 20)
        echo = config.get("database.echo", False)

        try:
            self._engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,  # Verify connections before using
                echo=echo,
            )

            # Test connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(
                f"✅ TimescaleDB connected: {db_host}:{db_port}/{db_name} "
                f"(pool_size={pool_size}, max_overflow={max_overflow})"
            )

        except SQLAlchemyError as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise

    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine"""
        if self._engine is None:
            self._initialize_connection()
        return self._engine

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = self.engine.connect()
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error(f"Database transaction error: {e}")
            raise
        finally:
            connection.close()

    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Tuple]:
        """
        Execute a query and return results

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            List of tuples containing query results
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                return result.fetchall()
        except SQLAlchemyError as e:
            logger.error(f"Query execution error: {e}")
            raise

    def insert_kline(self, kline_data: Dict[str, Any]) -> bool:
        """
        Insert candlestick data into raw_klines table

        Args:
            kline_data: Dictionary containing OHLCV data

        Returns:
            True if successful, False otherwise
        """
        query = """
        INSERT INTO raw_klines (
            time, exchange, symbol, interval,
            open, high, low, close, volume,
            close_volume, number_of_trades,
            taker_buy_base_volume, taker_buy_quote_volume,
            collected_at
        ) VALUES (
            :time, :exchange, :symbol, :interval,
            :open, :high, :low, :close, :volume,
            :close_volume, :number_of_trades,
            :taker_buy_base_volume, :taker_buy_quote_volume,
            :collected_at
        )
        ON CONFLICT (time, exchange, symbol, interval) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            collected_at = EXCLUDED.collected_at
        """

        try:
            # Convert timestamp to datetime
            if isinstance(kline_data.get("timestamp"), int):
                time_value = datetime.fromtimestamp(kline_data["timestamp"] / 1000)
            else:
                time_value = datetime.fromisoformat(kline_data["open_time"])

            params = {
                "time": time_value,
                "exchange": kline_data["exchange"],
                "symbol": kline_data["symbol"],
                "interval": kline_data["interval"],
                "open": kline_data["open"],
                "high": kline_data["high"],
                "low": kline_data["low"],
                "close": kline_data["close"],
                "volume": kline_data["volume"],
                "close_volume": kline_data.get("close_volume"),
                "number_of_trades": kline_data.get("number_of_trades"),
                "taker_buy_base_volume": kline_data.get("taker_buy_base_volume"),
                "taker_buy_quote_volume": kline_data.get("taker_buy_quote_volume"),
                "collected_at": datetime.fromisoformat(kline_data["collected_at"]),
            }

            with self.get_connection() as conn:
                conn.execute(text(query), params)

            logger.debug(
                f"💾 Inserted kline: {kline_data['symbol']} {kline_data['interval']} @ {time_value}"
            )
            return True

        except SQLAlchemyError as e:
            logger.error(f"Failed to insert kline data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error inserting kline: {e}")
            return False

    def insert_indicator(
        self,
        time: datetime,
        exchange: str,
        symbol: str,
        interval: str,
        indicator_name: str,
        indicator_value: float,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Insert calculated indicator into indicators table

        Args:
            time: Timestamp of the indicator
            exchange: Exchange name
            symbol: Trading pair
            interval: Timeframe
            indicator_name: Name of the indicator (e.g., 'RSI', 'MACD')
            indicator_value: Calculated value
            parameters: Indicator parameters (optional)

        Returns:
            True if successful, False otherwise
        """
        query = """
        INSERT INTO indicators (
            time, exchange, symbol, interval,
            indicator_name, indicator_value, parameters,
            calculated_at
        ) VALUES (
            :time, :exchange, :symbol, :interval,
            :indicator_name, :indicator_value, :parameters,
            :calculated_at
        )
        ON CONFLICT (time, exchange, symbol, interval, indicator_name) DO UPDATE SET
            indicator_value = EXCLUDED.indicator_value,
            parameters = EXCLUDED.parameters,
            calculated_at = EXCLUDED.calculated_at
        """

        try:
            import json

            params_json = json.dumps(parameters) if parameters else None

            with self.get_connection() as conn:
                conn.execute(
                    text(query),
                    {
                        "time": time,
                        "exchange": exchange,
                        "symbol": symbol,
                        "interval": interval,
                        "indicator_name": indicator_name,
                        "indicator_value": indicator_value,
                        "parameters": params_json,
                        "calculated_at": datetime.utcnow(),
                    },
                )

            logger.debug(
                f"💾 Inserted indicator: {symbol} {indicator_name}={indicator_value}"
            )
            return True

        except SQLAlchemyError as e:
            logger.error(f"Failed to insert indicator: {e}")
            return False

    def get_latest_klines(
        self, exchange: str, symbol: str, interval: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get latest candlestick data

        Args:
            exchange: Exchange name
            symbol: Trading pair
            interval: Timeframe
            limit: Number of candles to retrieve

        Returns:
            List of dictionaries containing OHLCV data
        """
        query = """
        SELECT time, open, high, low, close, volume, number_of_trades
        FROM raw_klines
        WHERE exchange = :exchange
          AND symbol = :symbol
          AND interval = :interval
        ORDER BY time DESC
        LIMIT :limit
        """

        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    text(query),
                    {
                        "exchange": exchange,
                        "symbol": symbol,
                        "interval": interval,
                        "limit": limit,
                    },
                )

                rows = result.fetchall()
                return [
                    {
                        "time": row[0],
                        "open": row[1],
                        "high": row[2],
                        "low": row[3],
                        "close": row[4],
                        "volume": row[5],
                        "number_of_trades": row[6],
                    }
                    for row in rows
                ]

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch klines: {e}")
            return []

    def close(self):
        """Close database connection pool"""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connection pool closed")
