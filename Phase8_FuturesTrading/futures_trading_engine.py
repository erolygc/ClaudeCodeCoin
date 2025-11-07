"""
Futures Trading Engine
Main engine that listens for pump signals and executes real futures trades
"""

import sys
import os
import time
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase8_FuturesTrading.futures_position_manager import FuturesPositionManager
from Phase8_FuturesTrading import config_futures as config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/futures_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FuturesTradingEngine:
    """
    Main Futures Trading Engine
    Monitors pump alerts and executes real/paper futures trades
    """

    def __init__(self, paper_mode: bool = True, testnet: bool = True):
        """
        Initialize Futures Trading Engine

        Args:
            paper_mode: Run in paper trading mode (default: True)
            testnet: Use testnet API (default: True)
        """
        logger.info("=" * 80)
        logger.info("CLAUDECODECOIN - FUTURES TRADING ENGINE")
        logger.info("=" * 80)

        # Load environment variables
        load_dotenv()
        api_key = os.getenv('GATEIO_API_KEY', '')
        api_secret = os.getenv('GATEIO_API_SECRET', '')

        self.paper_mode = paper_mode
        self.testnet = testnet

        # Initialize position manager
        self.position_manager = FuturesPositionManager(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
            paper_mode=paper_mode
        )

        # Alert monitoring
        self.alerts_dir = Path("../pump_alerts")
        self.processed_alerts = set()
        self.last_alert_check = 0
        self.alert_check_interval = 5  # Check every 5 seconds

        # Market data cache
        self.price_cache: Dict[str, float] = {}
        self.last_price_update = 0
        self.price_update_interval = 5

        # Database connection
        self.db_path = "../data_output/binance_data.db"

        # Statistics
        self.total_signals_received = 0
        self.total_signals_filtered = 0
        self.total_positions_opened = 0

        logger.info(f"Mode: {'PAPER TRADING' if paper_mode else 'REAL FUTURES TRADING'}")
        logger.info(f"Testnet: {testnet}")
        logger.info(f"Balance: ${config.INITIAL_BALANCE:.2f}")
        logger.info(f"Leverage: {config.MAX_LEVERAGE}x")
        logger.info(f"Position Size: ${config.POSITION_SIZE_USD:.2f}")
        logger.info(f"Max Positions: {config.MAX_OPEN_POSITIONS}")
        logger.info("=" * 80)

    def run(self):
        """Main trading loop"""
        logger.info("Futures Trading Engine started!")
        logger.info("Waiting for pump signals...")
        logger.info("")

        try:
            while True:
                # Check for new pump alerts
                self._check_pump_alerts()

                # Update open positions
                self._update_positions()

                # Log status periodically
                self._log_status()

                # Sleep
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n\nShutdown signal received...")
            self._shutdown()

    def _check_pump_alerts(self):
        """Check for new pump alerts"""
        current_time = time.time()

        if current_time - self.last_alert_check < self.alert_check_interval:
            return

        self.last_alert_check = current_time

        # Check today's alert file
        today = datetime.now().strftime('%Y%m%d')
        alert_file = self.alerts_dir / f"pump_alerts_{today}.json"

        if not alert_file.exists():
            return

        try:
            with open(alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                alerts = data if isinstance(data, list) else data.get('alerts', [])

            # Process new alerts
            for alert in alerts:
                alert_id = f"{alert['symbol']}_{alert['timestamp']}"

                if alert_id in self.processed_alerts:
                    continue

                self.processed_alerts.add(alert_id)
                self._process_alert(alert)

        except Exception as e:
            logger.error(f"Error reading alerts: {e}")

    def _process_alert(self, alert: Dict):
        """
        Process a pump alert and decide whether to trade

        Args:
            alert: Pump alert dictionary
        """
        self.total_signals_received += 1

        symbol = alert.get('symbol', 'UNKNOWN')
        confidence = alert.get('confidence', 0)
        signal_type = alert.get('signal_type', 'unknown')
        price = alert.get('current_price', 0)

        logger.info(f"\n{'='*80}")
        logger.info(f"NEW SIGNAL: {symbol}")
        logger.info(f"Confidence: {confidence:.1f}%")
        logger.info(f"Type: {signal_type}")
        logger.info(f"Price: ${price:.6f}")

        # Filter 1: Confidence threshold
        if confidence < config.MIN_CONFIDENCE_TO_TRADE:
            logger.info(f"[FILTER] Confidence too low ({confidence:.1f}% < {config.MIN_CONFIDENCE_TO_TRADE}%)")
            self.total_signals_filtered += 1
            return

        # Filter 2: Already have position
        if symbol in self.position_manager.open_positions:
            logger.info(f"[FILTER] Already have position in {symbol}")
            self.total_signals_filtered += 1
            return

        # Filter 3: Check if we can open position
        position_size = config.POSITION_SIZE_USD
        conf_level = self._get_confidence_level(confidence)
        multiplier = config.POSITION_SIZE_MULTIPLIER.get(conf_level, 1.0)
        position_size *= multiplier

        can_open, reason = self.position_manager.can_open_position(position_size)
        if not can_open:
            logger.info(f"[FILTER] Cannot open position: {reason}")
            self.total_signals_filtered += 1
            return

        # Filter 4: Get current price from database
        current_price = self._get_current_price(symbol)
        if current_price == 0:
            logger.info(f"[FILTER] Cannot get current price for {symbol}")
            self.total_signals_filtered += 1
            return

        # Filter 5: Check volume (optional)
        if config.MIN_VOLUME_SPIKE > 0:
            volume_spike = alert.get('volume_spike', 0)
            if volume_spike < config.MIN_VOLUME_SPIKE:
                logger.info(f"[FILTER] Volume spike too low ({volume_spike:.1f}% < {config.MIN_VOLUME_SPIKE}%)")
                self.total_signals_filtered += 1
                return

        # All filters passed - open position!
        logger.info(f"[SIGNAL ACCEPTED] Opening position...")

        position = self.position_manager.open_position(
            symbol=symbol,
            entry_price=current_price,
            confidence=confidence,
            signal_type=signal_type,
            position_size_usd=position_size
        )

        if position:
            self.total_positions_opened += 1
            logger.info(f"[SUCCESS] Position #{self.total_positions_opened} opened!")
            logger.info(f"Symbol: {symbol}")
            logger.info(f"Entry: ${position.entry_price:.6f}")
            logger.info(f"Size: ${position.position_size:.2f}")
            logger.info(f"Margin: ${position.margin_used:.2f}")
            logger.info(f"Leverage: {position.leverage}x")
            logger.info(f"Stop Loss: ${position.stop_loss:.6f} (-{config.STOP_LOSS_PERCENT}%)")
            logger.info(f"Take Profit: ${position.take_profit:.6f} (+{config.TAKE_PROFIT_PERCENT.get(conf_level, 12)}%)")
            logger.info(f"Liquidation: ${position.liquidation_price:.6f} ({position.liquidation_distance_percent:.1f}% away)")

            # Show account status
            summary = self.position_manager.get_account_summary()
            logger.info(f"\nAccount Status:")
            logger.info(f"  Balance: ${summary['balance']:.2f}")
            logger.info(f"  Margin Used: ${summary['margin_used']:.2f} ({summary['margin_usage_percent']:.1f}%)")
            logger.info(f"  Free Margin: ${summary['free_margin']:.2f}")
            logger.info(f"  Open Positions: {summary['open_positions']}/{config.MAX_OPEN_POSITIONS}")
        else:
            logger.error(f"[ERROR] Failed to open position")

        logger.info(f"{'='*80}\n")

    def _update_positions(self):
        """Update all open positions with current prices"""
        if not self.position_manager.open_positions:
            return

        current_time = time.time()
        if current_time - self.last_price_update < self.price_update_interval:
            return

        self.last_price_update = current_time

        # Get current prices for all open positions
        symbols = list(self.position_manager.open_positions.keys())
        current_prices = {}

        for symbol in symbols:
            price = self._get_current_price(symbol)
            if price > 0:
                current_prices[symbol] = price

        # Update positions
        if current_prices:
            self.position_manager.update_positions(current_prices)

    def _get_current_price(self, symbol: str) -> float:
        """
        Get current price from database

        Args:
            symbol: Trading symbol

        Returns:
            Current price or 0 if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT close FROM klines
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (symbol,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return float(row[0])
            else:
                return 0.0

        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return 0.0

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

    def _log_status(self):
        """Log periodic status"""
        # Log every 60 seconds
        if not hasattr(self, '_last_status_log'):
            self._last_status_log = time.time()

        current_time = time.time()
        if current_time - self._last_status_log < 60:
            return

        self._last_status_log = current_time

        summary = self.position_manager.get_account_summary()

        logger.info(f"\n{'='*80}")
        logger.info("STATUS UPDATE")
        logger.info(f"{'='*80}")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"\nAccount:")
        logger.info(f"  Balance: ${summary['balance']:.2f}")
        logger.info(f"  Equity: ${summary['equity']:.2f}")
        logger.info(f"  Unrealized P&L: ${summary['unrealized_pnl']:.2f}")
        logger.info(f"  Total P&L: ${summary['total_pnl']:.2f}")
        logger.info(f"  Margin Used: ${summary['margin_used']:.2f} ({summary['margin_usage_percent']:.1f}%)")
        logger.info(f"\nPositions:")
        logger.info(f"  Open: {summary['open_positions']}/{config.MAX_OPEN_POSITIONS}")
        logger.info(f"  Total Trades: {summary['total_trades']}")
        logger.info(f"  Win Rate: {summary['win_rate']:.1f}%")
        logger.info(f"\nSignals:")
        logger.info(f"  Received: {self.total_signals_received}")
        logger.info(f"  Filtered: {self.total_signals_filtered}")
        logger.info(f"  Positions Opened: {self.total_positions_opened}")

        if summary['circuit_breaker_active']:
            logger.warning(f"\n⚠️  CIRCUIT BREAKER ACTIVE ⚠️")

        # Show open positions
        if self.position_manager.open_positions:
            logger.info(f"\nOpen Positions:")
            for symbol, pos in self.position_manager.open_positions.items():
                logger.info(f"  {symbol}: ${pos.current_price:.6f} | "
                          f"P&L: ${pos.unrealized_pnl:.2f} ({pos.unrealized_pnl_percent:.2f}%) | "
                          f"Liq: {pos.liquidation_distance_percent:.1f}% away")

        logger.info(f"{'='*80}\n")

    def _shutdown(self):
        """Shutdown trading engine"""
        logger.info("Shutting down Futures Trading Engine...")

        # Show final summary
        summary = self.position_manager.get_account_summary()

        logger.info(f"\n{'='*80}")
        logger.info("FINAL SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Starting Balance: ${config.INITIAL_BALANCE:.2f}")
        logger.info(f"Final Balance: ${summary['balance']:.2f}")
        logger.info(f"Final Equity: ${summary['equity']:.2f}")
        logger.info(f"Total P&L: ${summary['total_pnl']:.2f} ({(summary['total_pnl']/config.INITIAL_BALANCE)*100:.2f}%)")
        logger.info(f"\nTrades:")
        logger.info(f"  Total: {summary['total_trades']}")
        logger.info(f"  Winners: {summary['winning_trades']}")
        logger.info(f"  Losers: {summary['losing_trades']}")
        logger.info(f"  Win Rate: {summary['win_rate']:.1f}%")
        logger.info(f"\nOpen Positions: {summary['open_positions']}")

        if summary['open_positions'] > 0:
            logger.warning(f"\n⚠️  WARNING: {summary['open_positions']} positions still open!")
            logger.info("These will remain open. Close them manually or restart the engine.")

        logger.info(f"{'='*80}\n")
        logger.info("Goodbye! 👋")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='ClaudeCodeCoin Futures Trading Engine')
    parser.add_argument('--real', action='store_true',
                       help='Enable REAL trading (default: paper mode)')
    parser.add_argument('--testnet', action='store_true', default=True,
                       help='Use testnet API (default: True)')
    parser.add_argument('--mainnet', action='store_true',
                       help='Use mainnet API (REAL MONEY!)')

    args = parser.parse_args()

    # Safety check
    if args.real and args.mainnet:
        print("=" * 80)
        print("⚠️  WARNING: REAL TRADING ON MAINNET ⚠️")
        print("=" * 80)
        print("You are about to trade with REAL money!")
        print(f"Initial balance: ${config.INITIAL_BALANCE:.2f}")
        print(f"Max leverage: {config.MAX_LEVERAGE}x")
        print(f"Position size: ${config.POSITION_SIZE_USD:.2f}")
        print("")
        response = input("Type 'YES I UNDERSTAND THE RISKS' to continue: ")

        if response != "YES I UNDERSTAND THE RISKS":
            print("Cancelled.")
            return

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Create engine
    engine = FuturesTradingEngine(
        paper_mode=not args.real,
        testnet=not args.mainnet
    )

    # Run
    engine.run()


if __name__ == "__main__":
    main()
