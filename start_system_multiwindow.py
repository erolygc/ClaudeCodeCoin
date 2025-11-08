"""
Master Trading System Launcher - Multi-Window Version
Opens each component in a separate terminal window for easier monitoring

Usage:
    python start_system_multiwindow.py
    python start_system_multiwindow.py --top 20
    python start_system_multiwindow.py --coins BTC_USDT,ETH_USDT,SOL_USDT
"""

import sys
import time
import subprocess
import platform
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiWindowTradingSystem:
    """
    Launch trading system with each component in separate window
    """

    def __init__(self, top_coins=50, specific_coins=None):
        self.top_coins = top_coins
        self.specific_coins = specific_coins
        self.is_windows = platform.system() == 'Windows'

    def _print_banner(self):
        """Print startup banner"""
        print("\n" + "="*80)
        print("🚀 CLAUDECODECOIN - MULTI-WINDOW TRADING SYSTEM")
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
        print("="*80)
        print("")

    def _setup_database(self):
        """Setup initial database"""
        logger.info("🔧 Setting up database...")

        try:
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

    def _launch_windows_terminal(self, title: str, command: list):
        """Launch command in new Windows terminal"""
        # Use start command to open new window
        cmd = ['start', title, 'cmd', '/k'] + command

        # Run through cmd.exe
        subprocess.Popen(
            ' '.join(cmd),
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if self.is_windows else 0
        )

    def _launch_linux_terminal(self, title: str, command: list):
        """Launch command in new Linux terminal"""
        # Try different terminal emulators
        terminals = [
            ['gnome-terminal', '--title', title, '--', *command],
            ['xterm', '-title', title, '-e', *command],
            ['konsole', '--title', title, '-e', *command],
            ['xfce4-terminal', '--title', title, '--command', ' '.join(command)]
        ]

        for term_cmd in terminals:
            try:
                subprocess.Popen(term_cmd)
                return
            except FileNotFoundError:
                continue

        logger.warning("⚠️ No terminal emulator found, running in background")
        subprocess.Popen(command)

    def start(self):
        """Start all components in separate windows"""
        self._print_banner()

        try:
            # Setup database
            self._setup_database()

            print("🚀 Launching components in separate windows...")
            print("")

            # Launch Scanner
            logger.info("1️⃣  Launching Hybrid Scanner in new window...")
            if self.is_windows:
                self._launch_windows_terminal(
                    "Hybrid Scanner",
                    [sys.executable, "Phase6_PumpDetection/realtime_hybrid_scanner.py",
                     "--interval", "30"]
                )
            else:
                self._launch_linux_terminal(
                    "Hybrid Scanner",
                    [sys.executable, "Phase6_PumpDetection/realtime_hybrid_scanner.py",
                     "--interval", "30"]
                )

            time.sleep(2)

            # Launch Trading Engine
            logger.info("2️⃣  Launching Paper Trading Engine in new window...")
            if self.is_windows:
                self._launch_windows_terminal(
                    "Paper Trading Engine",
                    [sys.executable, "Phase8_FuturesTrading/paper_trading_futures_engine.py"]
                )
            else:
                self._launch_linux_terminal(
                    "Paper Trading Engine",
                    [sys.executable, "Phase8_FuturesTrading/paper_trading_futures_engine.py"]
                )

            print("")
            print("="*80)
            print("✅ ALL COMPONENTS LAUNCHED IN SEPARATE WINDOWS")
            print("="*80)
            print("")
            print("You should now see:")
            print("  1️⃣  Window: Hybrid Scanner")
            print("  2️⃣  Window: Paper Trading Engine")
            print("")
            print("📊 Monitor:")
            print("   - Logs: logs/")
            print("   - Signals: Phase6_PumpDetection/signals/")
            print("   - Performance: paper_trading_performance.db")
            print("")
            print("🛑 To stop:")
            print("   - Close each window manually")
            print("   - Or press Ctrl+C in each window")
            print("")
            print("="*80)
            print("")
            print("💡 Quick monitoring commands:")
            print("")
            if self.is_windows:
                print("   # Watch logs (PowerShell):")
                print("   .\\watch_logs.ps1 logs\\paper_trading.log")
                print("   .\\watch_logs.ps1 logs\\realtime_hybrid_scanner.log")
                print("")
                print("   # View signals:")
                print("   dir Phase6_PumpDetection\\signals\\")
                print("")
                print("   # Query performance:")
                print('   sqlite3 paper_trading_performance.db "SELECT * FROM positions LIMIT 5"')
            else:
                print("   # Watch logs:")
                print("   tail -f logs/paper_trading.log")
                print("   tail -f logs/realtime_hybrid_scanner.log")
                print("")
                print("   # View signals:")
                print("   ls Phase6_PumpDetection/signals/")
                print("")
                print("   # Query performance:")
                print('   sqlite3 paper_trading_performance.db "SELECT * FROM positions LIMIT 5"')
            print("")
            print("="*80)

        except Exception as e:
            logger.error(f"❌ Error starting system: {e}", exc_info=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='ClaudeCodeCoin Multi-Window Trading System'
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

    system = MultiWindowTradingSystem(
        top_coins=args.top,
        specific_coins=specific_coins
    )

    system.start()


if __name__ == "__main__":
    main()
