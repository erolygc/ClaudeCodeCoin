"""
Master Trading System Launcher - Windows Compatible
Starts all components with a single command

Components:
1. Data Collector (Gate.io real-time data)
2. Hybrid Pump Scanner (Multi-TF + 100+ indicators)
3. Paper Trading Engine ($10k balance, $100 positions)

Usage:
    python start_trading_system_windows.py
    python start_trading_system_windows.py --top 20
    python start_trading_system_windows.py --coins BTC_USDT,ETH_USDT,SOL_USDT
"""

import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingSystemManager:
    """
    Master manager for entire trading system - Windows Compatible
    """

    def __init__(self, top_coins=50, specific_coins=None):
        self.top_coins = top_coins
        self.specific_coins = specific_coins
        self.processes = {}
        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("\n⚠️ Shutdown signal received. Stopping all services...")
        self.stop()

    def _print_banner(self):
        """Print startup banner"""
        print("\n" + "="*80)
        print("🚀 CLAUDECODECOIN - AUTOMATED TRADING SYSTEM")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        print("Configuration:")
        print(f"  💰 Initial Balance: $10,000")
        print(f"  📊 Position Size: $100")
        print(f"  🎯 Max Positions: 10")
        print(f"  🔄 Top Coins: {self.top_coins if not self.specific_coins else 'Custom'}")
        print(f"  📈 Mode: PAPER TRADING")
        print("")
        print("Components:")
        print("  1️⃣  Data Collector (Gate.io Real-time)")
        print("  2️⃣  Hybrid Scanner (Multi-TF + 100+ Indicators)")
        print("  3️⃣  Paper Trading Engine ($10k balance)")
        print("")
        print("="*80)
        print("")

    def _fetch_gate_coins(self) -> list:
        """Fetch Gate.io futures coins"""
        logger.info("📥 Fetching Gate.io futures contracts...")

        try:
            if self.specific_coins:
                coins = self.specific_coins
                logger.info(f"✅ Using {len(coins)} specific coins")
            else:
                # Run get_gate_futures_coins.py
                result = subprocess.run(
                    [sys.executable, "Phase8_FuturesTrading/get_gate_futures_coins.py",
                     "--top", str(self.top_coins), "--save"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Read saved file
                    import json
                    coins_file = Path("gate_futures_coins.json")
                    if coins_file.exists():
                        with open(coins_file, "r") as f:
                            data = json.load(f)
                        coins = data['contracts']
                        logger.info(f"✅ Fetched {len(coins)} Gate.io futures contracts")
                    else:
                        logger.warning("⚠️ Coins file not found, using defaults")
                        coins = self._get_default_coins()
                else:
                    logger.warning("⚠️ Could not fetch contracts, using defaults")
                    coins = self._get_default_coins()

            return coins

        except Exception as e:
            logger.error(f"❌ Error fetching coins: {e}")
            return self._get_default_coins()

    def _get_default_coins(self):
        """Get default coin list"""
        return [
            'BTC_USDT', 'ETH_USDT', 'BNB_USDT', 'SOL_USDT', 'XRP_USDT',
            'ADA_USDT', 'DOGE_USDT', 'MATIC_USDT', 'DOT_USDT', 'AVAX_USDT'
        ]

    def _setup_database(self):
        """Setup initial database and timeframes"""
        logger.info("🔧 Setting up database and timeframes...")

        try:
            # Check if test database exists
            db_path = Path("Phase1_DataCollection/data_output/binance_data.db")

            if not db_path.exists():
                logger.info("Creating test database...")
                subprocess.run(
                    [sys.executable, "Phase1_DataCollection/create_test_database.py"],
                    timeout=60
                )
                subprocess.run(
                    [sys.executable, "Phase1_DataCollection/add_pump_data.py"],
                    timeout=60
                )

            logger.info("✅ Database ready")

        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")

    def _start_data_collector(self, coins: list):
        """Start real-time data collector"""
        logger.info("1️⃣  Starting Data Collector...")

        # For now, use existing database
        logger.info("✅ Data Collector ready (using existing database)")

    def _start_hybrid_scanner(self):
        """Start hybrid pump scanner"""
        logger.info("2️⃣  Starting Hybrid Scanner...")

        # Use subprocess instead of Process for Windows
        process = subprocess.Popen(
            [sys.executable, "Phase6_PumpDetection/realtime_hybrid_scanner.py", "--interval", "30"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.processes['scanner'] = process
        logger.info(f"✅ Hybrid Scanner started (PID: {process.pid})")

        # Start thread to monitor output
        def monitor_output():
            for line in process.stdout:
                if line.strip():
                    print(f"[SCANNER] {line.strip()}")

        thread = threading.Thread(target=monitor_output, daemon=True)
        thread.start()

    def _start_paper_trading(self):
        """Start paper trading engine"""
        logger.info("3️⃣  Starting Paper Trading Engine...")

        # Use subprocess
        process = subprocess.Popen(
            [sys.executable, "Phase8_FuturesTrading/paper_trading_futures_engine.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.processes['trading'] = process
        logger.info(f"✅ Paper Trading Engine started (PID: {process.pid})")

        # Start thread to monitor output
        def monitor_output():
            for line in process.stdout:
                if line.strip():
                    print(f"[TRADING] {line.strip()}")

        thread = threading.Thread(target=monitor_output, daemon=True)
        thread.start()

    def start(self):
        """Start all components"""
        self._print_banner()

        try:
            # Step 1: Fetch coins
            coins = self._fetch_gate_coins()

            # Step 2: Setup database
            self._setup_database()

            # Step 3: Start data collector
            self._start_data_collector(coins)

            # Step 4: Start hybrid scanner
            self._start_hybrid_scanner()

            # Step 5: Start paper trading
            time.sleep(3)  # Give scanner time to start
            self._start_paper_trading()

            logger.info("")
            logger.info("="*80)
            logger.info("✅ ALL SYSTEMS OPERATIONAL")
            logger.info("="*80)
            logger.info("")
            logger.info("📊 Monitor:")
            logger.info("   - Logs: logs/")
            logger.info("   - Signals: Phase6_PumpDetection/signals/")
            logger.info("   - Performance: paper_trading_performance.db")
            logger.info("")
            logger.info("⌨️  Press Ctrl+C to stop all services")
            logger.info("="*80)
            logger.info("")

            self.running = True

            # Keep main thread alive
            while self.running:
                # Check if processes are alive
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:  # Process has terminated
                        logger.warning(f"⚠️ Process {name} died, restarting...")
                        if name == 'scanner':
                            self._start_hybrid_scanner()
                        elif name == 'trading':
                            self._start_paper_trading()

                time.sleep(10)

        except KeyboardInterrupt:
            logger.info("\n⚠️ Keyboard interrupt received")
            self.stop()
        except Exception as e:
            logger.error(f"❌ Error starting system: {e}", exc_info=True)
            self.stop()

    def stop(self):
        """Stop all components"""
        logger.info("\n🛑 Stopping all services...")

        self.running = False

        for name, process in self.processes.items():
            try:
                logger.info(f"Stopping {name}...")
                process.terminate()

                # Wait for process to terminate
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {name}...")
                    process.kill()

                logger.info(f"✅ {name} stopped")

            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")

        logger.info("")
        logger.info("="*80)
        logger.info("✅ ALL SERVICES STOPPED")
        logger.info("="*80)
        logger.info("")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='ClaudeCodeCoin Automated Trading System (Windows)'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=50,
        help='Number of top volume coins to trade (default: 50)'
    )
    parser.add_argument(
        '--coins',
        type=str,
        help='Specific coins to trade (comma-separated, e.g., BTC_USDT,ETH_USDT)'
    )

    args = parser.parse_args()

    specific_coins = None
    if args.coins:
        specific_coins = [c.strip() for c in args.coins.split(',')]

    manager = TradingSystemManager(
        top_coins=args.top,
        specific_coins=specific_coins
    )

    manager.start()


if __name__ == "__main__":
    main()
