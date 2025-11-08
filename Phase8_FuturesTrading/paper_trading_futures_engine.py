"""
Paper Trading Futures Engine
Monitors hybrid signals and executes paper trades

Features:
- $10,000 initial balance
- $100 per position
- Real-time signal monitoring
- Position management
- Performance tracking
"""

import sys
import os
import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import logging

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import paper_trading_config as config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(config.LOG_DIR) / config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Paper trading position"""
    id: str
    symbol: str
    direction: str  # LONG/SHORT
    entry_price: float
    quantity: float
    position_size: float
    stop_loss: float
    take_profit: float
    opened_at: str
    signal_confidence: float
    status: str  # OPEN/CLOSED
    closed_at: Optional[str] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    fees: float = 0.0
    reason: Optional[str] = None  # SL/TP/MANUAL


@dataclass
class AccountState:
    """Account state"""
    balance: float
    equity: float
    unrealized_pnl: float
    realized_pnl: float
    open_positions: int
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_fees: float
    max_balance: float
    max_drawdown: float
    daily_pnl: float
    daily_trades: int


class PaperTradingEngine:
    """
    Paper Trading Engine for Futures

    Watches for hybrid signals and executes paper trades
    """

    def __init__(self):
        self.balance = config.INITIAL_BALANCE
        self.initial_balance = config.INITIAL_BALANCE
        self.equity = config.INITIAL_BALANCE
        self.max_balance = config.INITIAL_BALANCE

        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []

        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_fees = 0.0

        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()

        self.processed_signals = set()
        self.running = False

        # Create directories
        Path(config.LOG_DIR).mkdir(exist_ok=True)
        Path(config.SIGNAL_DIR).mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info("="*80)
        logger.info("PAPER TRADING FUTURES ENGINE")
        logger.info("="*80)
        logger.info(f"Initial Balance: ${self.balance:,.2f}")
        logger.info(f"Position Size: ${config.POSITION_SIZE}")
        logger.info(f"Max Positions: {config.MAX_OPEN_POSITIONS}")
        logger.info(f"Min Confidence: {config.MIN_SIGNAL_CONFIDENCE}%")
        logger.info("="*80)

    def _init_database(self):
        """Initialize performance database"""
        db_path = Path(config.PERFORMANCE_DB)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                direction TEXT,
                entry_price REAL,
                quantity REAL,
                position_size REAL,
                stop_loss REAL,
                take_profit REAL,
                opened_at TEXT,
                signal_confidence REAL,
                status TEXT,
                closed_at TEXT,
                exit_price REAL,
                pnl REAL,
                pnl_percent REAL,
                fees REAL,
                reason TEXT
            )
        """)

        # Account snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_snapshots (
                timestamp TEXT PRIMARY KEY,
                balance REAL,
                equity REAL,
                unrealized_pnl REAL,
                realized_pnl REAL,
                open_positions INTEGER,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                total_fees REAL,
                max_drawdown REAL
            )
        """)

        conn.commit()
        conn.close()

    def _check_daily_reset(self):
        """Reset daily counters"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            logger.info(f"Daily reset - Previous day PnL: ${self.daily_pnl:,.2f}, Trades: {self.daily_trades}")
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset_date = today

    def _check_daily_limits(self) -> bool:
        """Check if daily limits exceeded"""
        self._check_daily_reset()

        if abs(self.daily_pnl) >= config.MAX_DAILY_LOSS:
            logger.warning(f"Daily loss limit reached: ${self.daily_pnl:,.2f}")
            return False

        if self.daily_trades >= config.MAX_DAILY_TRADES:
            logger.warning(f"Daily trade limit reached: {self.daily_trades}")
            return False

        return True

    def get_account_state(self) -> AccountState:
        """Get current account state"""
        unrealized_pnl = sum(
            self._calculate_unrealized_pnl(pos)
            for pos in self.positions.values()
        )

        realized_pnl = self.balance - self.initial_balance

        self.equity = self.balance + unrealized_pnl

        win_rate = (
            self.winning_trades / self.total_trades * 100
            if self.total_trades > 0 else 0
        )

        max_drawdown = (
            (self.max_balance - self.equity) / self.max_balance * 100
            if self.max_balance > 0 else 0
        )

        if self.equity > self.max_balance:
            self.max_balance = self.equity

        return AccountState(
            balance=self.balance,
            equity=self.equity,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=realized_pnl,
            open_positions=len(self.positions),
            total_trades=self.total_trades,
            winning_trades=self.winning_trades,
            losing_trades=self.losing_trades,
            win_rate=win_rate,
            total_fees=self.total_fees,
            max_balance=self.max_balance,
            max_drawdown=max_drawdown,
            daily_pnl=self.daily_pnl,
            daily_trades=self.daily_trades
        )

    def _calculate_unrealized_pnl(self, position: Position) -> float:
        """Calculate unrealized PnL (placeholder - needs real price)"""
        # In real implementation, fetch current price from exchange
        # For now, return 0
        return 0.0

    def _scan_for_signals(self) -> List[Dict]:
        """Scan signal directory for new signals"""
        signal_dir = Path(config.SIGNAL_DIR)

        if not signal_dir.exists():
            return []

        signals = []

        for signal_file in signal_dir.glob("hybrid_*.json"):
            signal_id = signal_file.stem

            if signal_id in self.processed_signals:
                continue

            try:
                with open(signal_file, 'r') as f:
                    signal = json.load(f)

                # Check if signal is recent (within 5 minutes)
                signal_time = datetime.fromisoformat(signal['timestamp'])
                if datetime.now() - signal_time > timedelta(minutes=5):
                    self.processed_signals.add(signal_id)
                    continue

                signals.append(signal)
                self.processed_signals.add(signal_id)

            except Exception as e:
                logger.error(f"Error reading signal {signal_file}: {e}")

        return signals

    def _should_trade_signal(self, signal: Dict) -> bool:
        """Check if signal meets trading criteria"""
        # Check confidence
        if signal['final_confidence'] < config.MIN_SIGNAL_CONFIDENCE:
            logger.debug(f"Signal confidence too low: {signal['final_confidence']:.1f}%")
            return False

        # Check if already have position in this symbol
        if signal['symbol'] in self.positions:
            logger.debug(f"Already have open position in {signal['symbol']}")
            return False

        # Check max positions
        if len(self.positions) >= config.MAX_OPEN_POSITIONS:
            logger.debug(f"Max positions reached: {len(self.positions)}")
            return False

        # Check daily limits
        if not self._check_daily_limits():
            return False

        # Check sufficient balance
        if self.balance < config.POSITION_SIZE:
            logger.warning(f"Insufficient balance: ${self.balance:.2f}")
            return False

        return True

    def open_position(self, signal: Dict) -> Optional[Position]:
        """Open a new position based on signal"""
        if not self._should_trade_signal(signal):
            return None

        symbol = signal['symbol']
        direction = signal['direction']
        entry_price = signal['entry_price']

        # Calculate quantity
        quantity = config.POSITION_SIZE / entry_price

        # Calculate fees
        fee = config.POSITION_SIZE * config.TAKER_FEE
        self.balance -= fee
        self.total_fees += fee

        # Use signal levels or default
        if config.USE_SIGNAL_LEVELS:
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit']
        else:
            if direction == 'LONG':
                stop_loss = entry_price * (1 - config.STOP_LOSS_PERCENT)
                take_profit = entry_price * (1 + config.TAKE_PROFIT_PERCENT)
            else:
                stop_loss = entry_price * (1 + config.STOP_LOSS_PERCENT)
                take_profit = entry_price * (1 - config.TAKE_PROFIT_PERCENT)

        # Create position
        position = Position(
            id=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            quantity=quantity,
            position_size=config.POSITION_SIZE,
            stop_loss=stop_loss,
            take_profit=take_profit,
            opened_at=datetime.now().isoformat(),
            signal_confidence=signal['final_confidence'],
            status='OPEN',
            fees=fee
        )

        self.positions[symbol] = position
        self.total_trades += 1
        self.daily_trades += 1

        # Save to database
        self._save_position(position)

        logger.info(f"")
        logger.info(f"🔵 POSITION OPENED")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Direction: {direction}")
        logger.info(f"   Entry: ${entry_price:.4f}")
        logger.info(f"   Size: ${config.POSITION_SIZE}")
        logger.info(f"   Quantity: {quantity:.4f}")
        logger.info(f"   Stop Loss: ${stop_loss:.4f}")
        logger.info(f"   Take Profit: ${take_profit:.4f}")
        logger.info(f"   Confidence: {signal['final_confidence']:.1f}%")
        logger.info(f"   Fee: ${fee:.2f}")

        return position

    def close_position(self, symbol: str, exit_price: float, reason: str):
        """Close an open position"""
        if symbol not in self.positions:
            return

        position = self.positions[symbol]

        # Calculate PnL
        if position.direction == 'LONG':
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity

        # Subtract exit fee
        exit_fee = position.position_size * config.TAKER_FEE
        pnl -= exit_fee
        self.total_fees += exit_fee

        # Update position
        position.closed_at = datetime.now().isoformat()
        position.exit_price = exit_price
        position.pnl = pnl
        position.pnl_percent = (pnl / position.position_size) * 100
        position.status = 'CLOSED'
        position.reason = reason
        position.fees += exit_fee

        # Update account
        self.balance += position.position_size + pnl
        self.daily_pnl += pnl

        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        # Move to closed positions
        self.closed_positions.append(position)
        del self.positions[symbol]

        # Save to database
        self._save_position(position)

        logger.info(f"")
        logger.info(f"{'🟢' if pnl > 0 else '🔴'} POSITION CLOSED")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Entry: ${position.entry_price:.4f}")
        logger.info(f"   Exit: ${exit_price:.4f}")
        logger.info(f"   PnL: ${pnl:,.2f} ({position.pnl_percent:+.2f}%)")
        logger.info(f"   Reason: {reason}")
        logger.info(f"   Total Fees: ${position.fees:.2f}")

    def _save_position(self, position: Position):
        """Save position to database"""
        conn = sqlite3.connect(config.PERFORMANCE_DB)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO positions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            position.id,
            position.symbol,
            position.direction,
            position.entry_price,
            position.quantity,
            position.position_size,
            position.stop_loss,
            position.take_profit,
            position.opened_at,
            position.signal_confidence,
            position.status,
            position.closed_at,
            position.exit_price,
            position.pnl,
            position.pnl_percent,
            position.fees,
            position.reason
        ))

        conn.commit()
        conn.close()

    def _save_account_snapshot(self):
        """Save account snapshot"""
        state = self.get_account_state()

        conn = sqlite3.connect(config.PERFORMANCE_DB)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO account_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            datetime.now().isoformat(),
            state.balance,
            state.equity,
            state.unrealized_pnl,
            state.realized_pnl,
            state.open_positions,
            state.total_trades,
            state.winning_trades,
            state.losing_trades,
            state.win_rate,
            state.total_fees,
            state.max_drawdown
        ))

        conn.commit()
        conn.close()

    def print_stats(self):
        """Print current statistics"""
        state = self.get_account_state()

        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"ACCOUNT STATISTICS")
        logger.info(f"{'='*80}")
        logger.info(f"Balance: ${state.balance:,.2f}")
        logger.info(f"Equity: ${state.equity:,.2f}")
        logger.info(f"Unrealized PnL: ${state.unrealized_pnl:+,.2f}")
        logger.info(f"Realized PnL: ${state.realized_pnl:+,.2f} ({state.realized_pnl/self.initial_balance*100:+.2f}%)")
        logger.info(f"")
        logger.info(f"Open Positions: {state.open_positions}/{config.MAX_OPEN_POSITIONS}")
        logger.info(f"Total Trades: {state.total_trades}")
        logger.info(f"Winning: {state.winning_trades} | Losing: {state.losing_trades}")
        logger.info(f"Win Rate: {state.win_rate:.1f}%")
        logger.info(f"Total Fees: ${state.total_fees:,.2f}")
        logger.info(f"")
        logger.info(f"Max Balance: ${state.max_balance:,.2f}")
        logger.info(f"Max Drawdown: {state.max_drawdown:.2f}%")
        logger.info(f"")
        logger.info(f"Today's PnL: ${state.daily_pnl:+,.2f}")
        logger.info(f"Today's Trades: {state.daily_trades}")
        logger.info(f"{'='*80}")

    def run(self):
        """Main engine loop"""
        logger.info("\n🚀 Starting Paper Trading Engine...")
        logger.info("Press Ctrl+C to stop\n")

        self.running = True
        last_stats_time = time.time()

        while self.running:
            try:
                # Scan for new signals
                signals = self._scan_for_signals()

                for signal in signals:
                    position = self.open_position(signal)

                # Check open positions (in real implementation, check SL/TP)
                # For now, just monitoring

                # Print stats periodically
                if config.SHOW_REALTIME_STATS:
                    if time.time() - last_stats_time >= config.STATS_UPDATE_INTERVAL:
                        self.print_stats()
                        self._save_account_snapshot()
                        last_stats_time = time.time()

                # Sleep
                time.sleep(config.SIGNAL_CHECK_INTERVAL)

            except KeyboardInterrupt:
                logger.info("\n⚠️ Shutdown signal received...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(10)

        logger.info("\n✅ Paper Trading Engine stopped")
        self.print_stats()


def main():
    engine = PaperTradingEngine()
    engine.run()


if __name__ == "__main__":
    main()
