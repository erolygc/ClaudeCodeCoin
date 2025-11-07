"""
Futures Position Manager
Manages real futures positions with margin, liquidation tracking, and risk controls
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal
import logging

from gateio_futures_api import GateIOFuturesAPI
import config_futures as config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class FuturesPosition:
    """Futures Position Data Class"""
    id: Optional[int]
    symbol: str
    contract: str  # Gate.io contract name (e.g., BTC_USDT)
    settle: str  # Settlement currency (usdt)
    entry_price: float
    current_price: float
    position_size: float  # Position size in USD
    quantity: int  # Actual contract quantity
    leverage: int
    margin_used: float
    side: str  # 'long' or 'short'

    # P&L tracking
    unrealized_pnl: float
    unrealized_pnl_percent: float
    realized_pnl: float = 0.0

    # Risk metrics
    liquidation_price: float = 0.0
    liquidation_distance_percent: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0

    # Order tracking
    order_id: Optional[str] = None
    status: str = "OPEN"  # OPEN, CLOSED, LIQUIDATED

    # Timestamps
    entry_time: str = ""
    exit_time: Optional[str] = None

    # Signal info
    confidence: float = 0.0
    signal_type: str = ""

    # Fees
    entry_fee: float = 0.0
    exit_fee: float = 0.0
    funding_fees: float = 0.0


class FuturesPositionManager:
    """Manages futures positions with real API integration"""

    def __init__(self, api_key: str = "", api_secret: str = "",
                 testnet: bool = True, paper_mode: bool = True):
        """
        Initialize Futures Position Manager

        Args:
            api_key: Gate.io API key
            api_secret: Gate.io API secret
            testnet: Use testnet (default: True for safety)
            paper_mode: Run in paper trading mode (no real orders)
        """
        self.paper_mode = paper_mode
        self.testnet = testnet

        # Initialize API if not in paper mode
        if not paper_mode and api_key and api_secret:
            self.api = GateIOFuturesAPI(api_key, api_secret, testnet)
            logger.info("Initialized REAL futures trading mode")
        else:
            self.api = None
            logger.info("Initialized PAPER futures trading mode")

        # Account state
        self.balance = config.INITIAL_BALANCE
        self.initial_balance = config.INITIAL_BALANCE
        self.margin_used = 0.0
        self.unrealized_pnl = 0.0

        # Position tracking
        self.open_positions: Dict[str, FuturesPosition] = {}
        self.closed_positions: List[FuturesPosition] = []

        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0

        # Safety controls
        self.circuit_breaker_active = False
        self.circuit_breaker_until = None
        self.consecutive_losses = 0
        self.daily_loss = 0.0

        # Database
        self.db_path = config.TRADES_DB
        self._init_database()

        # Load existing positions
        self._load_positions()

    def _init_database(self):
        """Initialize database for futures positions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS futures_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                contract TEXT NOT NULL,
                settle TEXT NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                position_size REAL NOT NULL,
                quantity INTEGER NOT NULL,
                leverage INTEGER NOT NULL,
                margin_used REAL NOT NULL,
                side TEXT NOT NULL,
                unrealized_pnl REAL DEFAULT 0,
                unrealized_pnl_percent REAL DEFAULT 0,
                realized_pnl REAL DEFAULT 0,
                liquidation_price REAL DEFAULT 0,
                liquidation_distance_percent REAL DEFAULT 0,
                stop_loss REAL DEFAULT 0,
                take_profit REAL DEFAULT 0,
                order_id TEXT,
                status TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                confidence REAL DEFAULT 0,
                signal_type TEXT,
                entry_fee REAL DEFAULT 0,
                exit_fee REAL DEFAULT 0,
                funding_fees REAL DEFAULT 0
            )
        """)

        # Account balance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                balance REAL NOT NULL,
                margin_used REAL NOT NULL,
                unrealized_pnl REAL NOT NULL,
                total_pnl REAL NOT NULL,
                open_positions INTEGER NOT NULL,
                equity REAL NOT NULL
            )
        """)

        conn.commit()
        conn.close()

        logger.info(f"Database initialized: {self.db_path}")

    def _load_positions(self):
        """Load open positions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM futures_positions
            WHERE status = 'OPEN'
        """)

        for row in cursor.fetchall():
            pos = FuturesPosition(
                id=row[0], symbol=row[1], contract=row[2], settle=row[3],
                entry_price=row[4], current_price=row[5], position_size=row[6],
                quantity=row[7], leverage=row[8], margin_used=row[9],
                side=row[10], unrealized_pnl=row[11], unrealized_pnl_percent=row[12],
                realized_pnl=row[13], liquidation_price=row[14],
                liquidation_distance_percent=row[15], stop_loss=row[16],
                take_profit=row[17], order_id=row[18], status=row[19],
                entry_time=row[20], exit_time=row[21], confidence=row[22],
                signal_type=row[23], entry_fee=row[24], exit_fee=row[25],
                funding_fees=row[26]
            )
            self.open_positions[pos.symbol] = pos
            self.margin_used += pos.margin_used

        conn.close()
        logger.info(f"Loaded {len(self.open_positions)} open positions")

    def can_open_position(self, position_value: float) -> Tuple[bool, str]:
        """
        Check if we can open a new position

        Args:
            position_value: Position size in USD

        Returns:
            Tuple of (can_open, reason)
        """
        # Check circuit breaker
        if self.circuit_breaker_active:
            if datetime.now() < self.circuit_breaker_until:
                return False, "Circuit breaker active - cooling down"
            else:
                self.circuit_breaker_active = False

        # Check position limit
        if len(self.open_positions) >= config.MAX_OPEN_POSITIONS:
            return False, f"Maximum {config.MAX_OPEN_POSITIONS} positions limit reached"

        # Check margin availability
        required_margin = position_value / config.DEFAULT_LEVERAGE
        free_margin = self.balance - self.margin_used

        if required_margin > free_margin:
            return False, f"Insufficient margin (need ${required_margin:.2f}, have ${free_margin:.2f})"

        # Check total margin usage
        if (self.margin_used + required_margin) > config.MAX_TOTAL_MARGIN:
            return False, f"Total margin limit exceeded (max ${config.MAX_TOTAL_MARGIN:.2f})"

        # Check emergency stop conditions
        if self.daily_loss >= config.EMERGENCY_STOP_CONDITIONS['max_loss_per_day']:
            self._activate_circuit_breaker("Max daily loss reached")
            return False, "Max daily loss reached - circuit breaker activated"

        if self.consecutive_losses >= config.EMERGENCY_STOP_CONDITIONS['max_consecutive_losses']:
            self._activate_circuit_breaker("Max consecutive losses")
            return False, "Max consecutive losses - circuit breaker activated"

        if self.balance < config.EMERGENCY_STOP_CONDITIONS['min_balance']:
            return False, f"Balance below minimum (${config.EMERGENCY_STOP_CONDITIONS['min_balance']})"

        return True, "OK"

    def open_position(self, symbol: str, entry_price: float, confidence: float,
                     signal_type: str = "", position_size_usd: Optional[float] = None) -> Optional[FuturesPosition]:
        """
        Open a new futures position

        Args:
            symbol: Trading symbol (e.g., BTC_USDT)
            entry_price: Entry price
            confidence: Signal confidence (0-100)
            signal_type: Type of signal
            position_size_usd: Position size in USD (default from config)

        Returns:
            FuturesPosition object or None if failed
        """
        # Determine position size
        if position_size_usd is None:
            position_size_usd = config.POSITION_SIZE_USD

        # Apply position size multiplier based on confidence
        conf_level = self._get_confidence_level(confidence)
        multiplier = config.POSITION_SIZE_MULTIPLIER.get(conf_level, 1.0)
        position_size_usd *= multiplier

        # Check if we can open
        can_open, reason = self.can_open_position(position_size_usd)
        if not can_open:
            logger.warning(f"Cannot open position for {symbol}: {reason}")
            return None

        # Calculate margin and quantity
        leverage = config.DEFAULT_LEVERAGE
        margin = position_size_usd / leverage

        # Gate.io contract quantity (simplified - actual calculation depends on contract specs)
        # For perpetual USDT contracts, 1 contract = $1
        quantity = int(position_size_usd)

        # Calculate stop loss and take profit
        stop_loss_pct = config.STOP_LOSS_PERCENT
        take_profit_pct = config.TAKE_PROFIT_PERCENT.get(conf_level, 12.0)

        stop_loss = entry_price * (1 - stop_loss_pct / 100)
        take_profit = entry_price * (1 + take_profit_pct / 100)

        # Calculate liquidation price
        liquidation_price = self._calculate_liquidation_price(
            entry_price, leverage, "long"
        )
        liq_distance = ((entry_price - liquidation_price) / entry_price) * 100

        # Calculate entry fee
        entry_fee = position_size_usd * (config.TAKER_FEE / 100)

        # Create position object
        position = FuturesPosition(
            id=None,
            symbol=symbol,
            contract=symbol,  # Assuming symbol == contract for Gate.io
            settle="usdt",
            entry_price=entry_price,
            current_price=entry_price,
            position_size=position_size_usd,
            quantity=quantity,
            leverage=leverage,
            margin_used=margin,
            side="long",
            unrealized_pnl=0.0,
            unrealized_pnl_percent=0.0,
            liquidation_price=liquidation_price,
            liquidation_distance_percent=liq_distance,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status="OPEN",
            entry_time=datetime.now().isoformat(),
            confidence=confidence,
            signal_type=signal_type,
            entry_fee=entry_fee
        )

        # Execute order if not in paper mode
        if not self.paper_mode and self.api:
            try:
                # Set leverage for contract
                self.api.set_leverage_for_contract("usdt", symbol, leverage)

                # Place order
                order = self.api.place_order(
                    settle="usdt",
                    contract=symbol,
                    size=quantity,
                    price=None,  # Market order
                    tif="ioc"
                )

                position.order_id = order.get('id')
                logger.info(f"[REAL] Order placed: {symbol} @ ${entry_price:.4f}, Order ID: {position.order_id}")

            except Exception as e:
                logger.error(f"Failed to place real order: {e}")
                return None
        else:
            logger.info(f"[PAPER] Position opened: {symbol} @ ${entry_price:.4f}")

        # Update account state
        self.margin_used += margin
        self.open_positions[symbol] = position
        self.total_trades += 1

        # Save to database
        self._save_position(position)
        self._save_account_state()

        logger.info(f"Position opened: {symbol} | Size: ${position_size_usd:.2f} | "
                   f"Leverage: {leverage}x | Margin: ${margin:.2f} | "
                   f"SL: ${stop_loss:.4f} | TP: ${take_profit:.4f} | "
                   f"Liq: ${liquidation_price:.4f} ({liq_distance:.1f}%)")

        return position

    def update_positions(self, current_prices: Dict[str, float]):
        """
        Update all open positions with current prices

        Args:
            current_prices: Dictionary of {symbol: current_price}
        """
        for symbol, position in list(self.open_positions.items()):
            if symbol in current_prices:
                current_price = current_prices[symbol]
                self._update_position_price(position, current_price)

                # Check if position should be closed
                if self._should_close_position(position):
                    reason = self._get_close_reason(position)
                    self.close_position(symbol, current_price, reason)

    def _update_position_price(self, position: FuturesPosition, current_price: float):
        """Update position with current price and calculate P&L"""
        position.current_price = current_price

        # Calculate unrealized P&L
        price_change = current_price - position.entry_price
        price_change_pct = (price_change / position.entry_price) * 100

        # Apply leverage to P&L
        real_pnl_pct = price_change_pct * position.leverage
        unrealized_pnl = position.margin_used * (real_pnl_pct / 100)

        position.unrealized_pnl = unrealized_pnl
        position.unrealized_pnl_percent = real_pnl_pct

        # Update liquidation distance
        liq_distance = ((current_price - position.liquidation_price) / current_price) * 100
        position.liquidation_distance_percent = liq_distance

        # Update database
        self._update_position_in_db(position)

    def _should_close_position(self, position: FuturesPosition) -> bool:
        """Check if position should be closed"""
        current_price = position.current_price

        # Check stop loss
        if current_price <= position.stop_loss:
            return True

        # Check take profit
        if current_price >= position.take_profit:
            return True

        # Check liquidation distance (emergency close if too close)
        if position.liquidation_distance_percent < 10:
            logger.warning(f"Emergency close: {position.symbol} too close to liquidation!")
            return True

        # Check auto-close time
        entry_time = datetime.fromisoformat(position.entry_time)
        minutes_open = (datetime.now() - entry_time).total_seconds() / 60

        if minutes_open > config.AUTO_CLOSE_AFTER_MINUTES:
            return True

        return False

    def _get_close_reason(self, position: FuturesPosition) -> str:
        """Get reason for closing position"""
        current_price = position.current_price

        if current_price <= position.stop_loss:
            return "STOP_LOSS"
        elif current_price >= position.take_profit:
            return "TAKE_PROFIT"
        elif position.liquidation_distance_percent < 10:
            return "LIQUIDATION_RISK"
        else:
            return "AUTO_CLOSE"

    def close_position(self, symbol: str, exit_price: float, reason: str = "MANUAL") -> Optional[FuturesPosition]:
        """
        Close an open position

        Args:
            symbol: Trading symbol
            exit_price: Exit price
            reason: Reason for closing

        Returns:
            Closed position or None
        """
        if symbol not in self.open_positions:
            logger.warning(f"Position not found: {symbol}")
            return None

        position = self.open_positions[symbol]

        # Execute close order if not in paper mode
        if not self.paper_mode and self.api:
            try:
                order = self.api.close_position(
                    settle="usdt",
                    contract=symbol,
                    position_size=position.quantity
                )
                logger.info(f"[REAL] Position closed: {symbol} @ ${exit_price:.4f}")
            except Exception as e:
                logger.error(f"Failed to close real position: {e}")
                # Continue with paper close for tracking
        else:
            logger.info(f"[PAPER] Position closed: {symbol} @ ${exit_price:.4f}")

        # Calculate final P&L
        price_change = exit_price - position.entry_price
        price_change_pct = (price_change / position.entry_price) * 100
        real_pnl_pct = price_change_pct * position.leverage
        realized_pnl = position.margin_used * (real_pnl_pct / 100)

        # Calculate exit fee
        exit_fee = position.position_size * (config.TAKER_FEE / 100)

        # Net P&L after fees
        net_pnl = realized_pnl - position.entry_fee - exit_fee

        # Update position
        position.current_price = exit_price
        position.realized_pnl = net_pnl
        position.exit_fee = exit_fee
        position.status = "CLOSED"
        position.exit_time = datetime.now().isoformat()

        # Update account
        self.balance += net_pnl
        self.margin_used -= position.margin_used
        self.total_pnl += net_pnl

        if net_pnl > 0:
            self.winning_trades += 1
            self.consecutive_losses = 0
        else:
            self.losing_trades += 1
            self.consecutive_losses += 1
            self.daily_loss += abs(net_pnl)

        # Log trade
        logger.info(f"Position closed: {symbol} | Reason: {reason} | "
                   f"P&L: ${net_pnl:.2f} ({real_pnl_pct:.2f}%) | "
                   f"Balance: ${self.balance:.2f}")

        # Move to closed positions
        del self.open_positions[symbol]
        self.closed_positions.append(position)

        # Update database
        self._update_position_in_db(position)
        self._save_account_state()

        return position

    def _calculate_liquidation_price(self, entry_price: float, leverage: int,
                                    side: str = "long") -> float:
        """Calculate liquidation price"""
        buffer = config.LIQUIDATION_BUFFER

        if side == "long":
            liq_price = entry_price * (1 - (1/leverage) + buffer)
        else:
            liq_price = entry_price * (1 + (1/leverage) - buffer)

        return liq_price

    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level string"""
        if confidence >= 80:
            return 'CRITICAL'
        elif confidence >= 65:
            return 'HIGH'
        elif confidence >= 50:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _activate_circuit_breaker(self, reason: str):
        """Activate circuit breaker"""
        from datetime import timedelta

        self.circuit_breaker_active = True
        self.circuit_breaker_until = datetime.now() + timedelta(
            minutes=config.CIRCUIT_BREAKER_COOLDOWN_MINUTES
        )

        logger.warning(f"CIRCUIT BREAKER ACTIVATED: {reason}")
        logger.warning(f"Trading paused until {self.circuit_breaker_until}")

    def _save_position(self, position: FuturesPosition):
        """Save position to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO futures_positions VALUES (
                NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            position.symbol, position.contract, position.settle, position.entry_price,
            position.current_price, position.position_size, position.quantity,
            position.leverage, position.margin_used, position.side,
            position.unrealized_pnl, position.unrealized_pnl_percent, position.realized_pnl,
            position.liquidation_price, position.liquidation_distance_percent,
            position.stop_loss, position.take_profit, position.order_id,
            position.status, position.entry_time, position.exit_time,
            position.confidence, position.signal_type, position.entry_fee,
            position.exit_fee, position.funding_fees
        ))

        position.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def _update_position_in_db(self, position: FuturesPosition):
        """Update position in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE futures_positions SET
                current_price = ?, unrealized_pnl = ?, unrealized_pnl_percent = ?,
                realized_pnl = ?, liquidation_distance_percent = ?,
                status = ?, exit_time = ?, exit_fee = ?, funding_fees = ?
            WHERE id = ?
        """, (
            position.current_price, position.unrealized_pnl, position.unrealized_pnl_percent,
            position.realized_pnl, position.liquidation_distance_percent,
            position.status, position.exit_time, position.exit_fee, position.funding_fees,
            position.id
        ))

        conn.commit()
        conn.close()

    def _save_account_state(self):
        """Save account state snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate total unrealized PnL
        total_unrealized = sum(p.unrealized_pnl for p in self.open_positions.values())
        equity = self.balance + total_unrealized

        cursor.execute("""
            INSERT INTO account_state VALUES (
                NULL, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            datetime.now().isoformat(), self.balance, self.margin_used,
            total_unrealized, self.total_pnl, len(self.open_positions), equity
        ))

        conn.commit()
        conn.close()

    def get_account_summary(self) -> Dict:
        """Get account summary"""
        total_unrealized = sum(p.unrealized_pnl for p in self.open_positions.values())
        free_margin = self.balance - self.margin_used
        equity = self.balance + total_unrealized
        margin_usage_pct = (self.margin_used / self.balance) * 100 if self.balance > 0 else 0

        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0

        return {
            'balance': self.balance,
            'equity': equity,
            'margin_used': self.margin_used,
            'free_margin': free_margin,
            'margin_usage_percent': margin_usage_pct,
            'unrealized_pnl': total_unrealized,
            'total_pnl': self.total_pnl,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'open_positions': len(self.open_positions),
            'circuit_breaker_active': self.circuit_breaker_active
        }


if __name__ == "__main__":
    # Test in paper mode
    manager = FuturesPositionManager(paper_mode=True)

    print("Futures Position Manager - Paper Mode")
    print("=" * 80)

    # Test opening position
    pos = manager.open_position(
        symbol="BTC_USDT",
        entry_price=50000.0,
        confidence=65.0,
        signal_type="coordinated_buying"
    )

    if pos:
        print(f"\nPosition opened successfully!")
        print(f"Symbol: {pos.symbol}")
        print(f"Size: ${pos.position_size:.2f}")
        print(f"Margin: ${pos.margin_used:.2f}")
        print(f"Leverage: {pos.leverage}x")
        print(f"Liquidation: ${pos.liquidation_price:.2f} ({pos.liquidation_distance_percent:.1f}%)")

        # Test update
        manager.update_positions({"BTC_USDT": 51000.0})
        print(f"\nPrice updated to $51,000")
        print(f"Unrealized P&L: ${pos.unrealized_pnl:.2f} ({pos.unrealized_pnl_percent:.2f}%)")

    # Show summary
    summary = manager.get_account_summary()
    print("\n" + "=" * 80)
    print("ACCOUNT SUMMARY:")
    print(f"Balance: ${summary['balance']:.2f}")
    print(f"Equity: ${summary['equity']:.2f}")
    print(f"Margin Used: ${summary['margin_used']:.2f} ({summary['margin_usage_percent']:.1f}%)")
    print(f"Unrealized P&L: ${summary['unrealized_pnl']:.2f}")
    print(f"Open Positions: {summary['open_positions']}")
