"""
Backtesting Engine
Test trading strategies on historical data
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import math

# Import indicators
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../Phase1_DataBackbone'))

try:
    from indicators.basic_indicators import calculate_all_indicators
except ImportError:
    print("⚠️  Warning: Could not import indicators, using mock data")
    calculate_all_indicators = None


class Backtester:
    """
    Backtest trading strategies on historical data
    """

    def __init__(
        self,
        db_path: str = None,
        initial_capital: float = 10000.0,
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0005   # 0.05%
    ):
        """
        Initialize backtester

        Args:
            db_path: Path to SQLite database
            initial_capital: Starting capital
            commission: Commission per trade (0.001 = 0.1%)
            slippage: Slippage per trade (0.0005 = 0.05%)
        """
        # Auto-detect project root and database path
        if db_path is None:
            # Try to find project root
            current = Path(__file__).parent
            for _ in range(5):  # Go up max 5 levels
                test_path = current / "data_output" / "binance_data.db"
                if test_path.exists():
                    db_path = str(test_path)
                    break
                current = current.parent

            # Fallback to relative path
            if db_path is None:
                db_path = "../../data_output/binance_data.db"

        self.db_path = Path(db_path)
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        self.capital = initial_capital
        self.position = 0  # 0 = flat, >0 = long quantity
        self.entry_price = 0
        self.trades = []
        self.equity_curve = []

    def load_data(
        self,
        symbol: str,
        exchange: str = "binance",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Load historical data from database

        Args:
            symbol: Trading symbol
            exchange: Exchange name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of OHLCV bars
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT timestamp, datetime, open, high, low, close, volume
            FROM klines
            WHERE symbol = ? AND exchange = ?
        """
        params = [symbol, exchange]

        if start_date:
            query += " AND datetime >= ?"
            params.append(start_date)

        if end_date:
            query += " AND datetime <= ?"
            params.append(end_date)

        query += " ORDER BY timestamp ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        bars = []
        for row in rows:
            bars.append({
                'timestamp': row[0],
                'datetime': row[1],
                'open': row[2],
                'high': row[3],
                'low': row[4],
                'close': row[5],
                'volume': row[6]
            })

        return bars

    def calculate_indicators(self, bars: List[Dict]) -> List[Dict]:
        """
        Calculate indicators for all bars

        Args:
            bars: List of OHLCV bars

        Returns:
            List of bars with indicators
        """
        if calculate_all_indicators is None:
            # Return bars as-is if indicators not available
            return bars

        # Extract price arrays
        closes = [b['close'] for b in bars]
        highs = [b['high'] for b in bars]
        lows = [b['low'] for b in bars]
        volumes = [b['volume'] for b in bars]

        # Calculate indicators for each bar
        for i, bar in enumerate(bars):
            # Use data up to current bar
            indicators = calculate_all_indicators(
                prices=closes[:i+1],
                high=highs[:i+1],
                low=lows[:i+1],
                volume=volumes[:i+1]
            )

            # Add indicators to bar
            bar.update(indicators)

        return bars

    def execute_trade(self, signal: str, price: float, timestamp: int):
        """
        Execute a trade

        Args:
            signal: 'buy' or 'sell'
            price: Execution price
            timestamp: Trade timestamp
        """
        if signal == 'buy' and self.position == 0:
            # Apply slippage
            exec_price = price * (1 + self.slippage)

            # Calculate position size (use all capital)
            quantity = (self.capital * 0.95) / exec_price  # Use 95% of capital
            cost = quantity * exec_price
            commission_cost = cost * self.commission

            if cost + commission_cost <= self.capital:
                self.position = quantity
                self.entry_price = exec_price
                self.capital -= (cost + commission_cost)

                self.trades.append({
                    'timestamp': timestamp,
                    'side': 'buy',
                    'price': exec_price,
                    'quantity': quantity,
                    'cost': cost,
                    'commission': commission_cost,
                    'capital': self.capital
                })

        elif signal == 'sell' and self.position > 0:
            # Apply slippage
            exec_price = price * (1 - self.slippage)

            # Sell entire position
            proceeds = self.position * exec_price
            commission_cost = proceeds * self.commission
            pnl = proceeds - (self.position * self.entry_price)

            self.capital += (proceeds - commission_cost)

            self.trades.append({
                'timestamp': timestamp,
                'side': 'sell',
                'price': exec_price,
                'quantity': self.position,
                'proceeds': proceeds,
                'commission': commission_cost,
                'pnl': pnl,
                'capital': self.capital
            })

            self.position = 0
            self.entry_price = 0

    def run(
        self,
        strategy,
        symbol: str,
        exchange: str = "binance",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Run backtest

        Args:
            strategy: Strategy instance
            symbol: Trading symbol
            exchange: Exchange name
            start_date: Start date
            end_date: End date

        Returns:
            Backtest results dict
        """
        print(f"🔄 Loading data: {symbol} on {exchange}...")
        bars = self.load_data(symbol, exchange, start_date, end_date)

        if len(bars) < 50:
            return {'error': f'Insufficient data: {len(bars)} bars'}

        print(f"✅ Loaded {len(bars)} bars")
        print(f"📊 Calculating indicators...")

        bars = self.calculate_indicators(bars)

        print(f"🎯 Running backtest with {strategy.name}...")

        # Reset state
        self.capital = self.initial_capital
        self.position = 0
        self.entry_price = 0
        self.trades = []
        self.equity_curve = []

        # Run strategy on each bar
        for bar in bars:
            # Update equity curve
            equity = self.capital
            if self.position > 0:
                equity += self.position * bar['close']
            self.equity_curve.append({
                'timestamp': bar['timestamp'],
                'equity': equity
            })

            # Get signal from strategy
            signal = strategy.on_bar(bar)

            # Execute trade
            if signal:
                self.execute_trade(signal, bar['close'], bar['timestamp'])
                strategy.position = 1 if signal == 'buy' else 0

        # Close any open position
        if self.position > 0:
            last_bar = bars[-1]
            self.execute_trade('sell', last_bar['close'], last_bar['timestamp'])

        # Calculate metrics
        metrics = self.calculate_metrics()

        print(f"\n✅ Backtest complete!")
        print(f"   Total Trades: {len(self.trades) // 2}")
        print(f"   Final Equity: ${metrics['final_equity']:.2f}")
        print(f"   Total Return: {metrics['total_return']:.2%}")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")

        return metrics

    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {'error': 'No trades executed'}

        # Separate buy/sell trades
        buy_trades = [t for t in self.trades if t['side'] == 'buy']
        sell_trades = [t for t in self.trades if t['side'] == 'sell']

        total_pnl = sum(t.get('pnl', 0) for t in sell_trades)
        final_equity = self.capital

        wins = [t['pnl'] for t in sell_trades if t.get('pnl', 0) > 0]
        losses = [t['pnl'] for t in sell_trades if t.get('pnl', 0) < 0]

        win_rate = len(wins) / len(sell_trades) if sell_trades else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Sharpe ratio
        returns = [t.get('pnl', 0) / self.initial_capital for t in sell_trades]
        avg_return = sum(returns) / len(returns) if returns else 0
        std_dev = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns)) if len(returns) > 1 else 0
        sharpe_ratio = (avg_return / std_dev * math.sqrt(252)) if std_dev > 0 else 0

        # Max drawdown
        peak = self.initial_capital
        max_dd = 0

        for point in self.equity_curve:
            equity = point['equity']
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd

        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_pnl': total_pnl,
            'total_return': (final_equity - self.initial_capital) / self.initial_capital,
            'total_trades': len(sell_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }


if __name__ == "__main__":
    from strategy import RSI_Strategy, MACD_Strategy, BollingerBands_Strategy

    # Initialize backtester
    backtester = Backtester(initial_capital=10000)

    # Test RSI strategy
    strategy = RSI_Strategy(rsi_buy=30, rsi_sell=70)

    results = backtester.run(
        strategy=strategy,
        symbol='BTCUSDT',
        exchange='binance'
    )

    if 'error' not in results:
        print("\n" + "="*70)
        print(f"📊 BACKTEST RESULTS - {strategy.name}")
        print("="*70)
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Equity: ${results['final_equity']:,.2f}")
        print(f"Total Return: {results['total_return']:.2%}")
        print(f"Total Trades: {results['total_trades']}")
        print(f"Win Rate: {results['win_rate']:.1%}")
        print(f"Avg Win: ${results['avg_win']:.2f}")
        print(f"Avg Loss: ${results['avg_loss']:.2f}")
        print(f"Profit Factor: {results['profit_factor']:.2f}")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {results['max_drawdown']:.1%}")
        print("="*70)
    else:
        print(f"❌ Error: {results['error']}")
