"""
Realtime Hybrid Pump Scanner
Continuously scans for pump signals and validates with advanced engine

Usage:
    python realtime_hybrid_scanner.py
"""

import sys
import os
import time
import signal
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase6_PumpDetection.hybrid_pump_scanner import HybridPumpScanner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/realtime_hybrid_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RealtimeHybridScanner:
    """
    Realtime Hybrid Scanner

    Runs continuous scanning loop:
    - Scans all symbols every N seconds
    - Emits hybrid signals to JSON files
    - Futures engine picks up signals automatically
    """

    def __init__(self,
                 scan_interval: int = 30,
                 hybrid_mode: bool = True,
                 pump_min_confidence: float = 60.0,
                 advanced_min_confidence: float = 65.0,
                 final_min_confidence: float = 70.0):
        """
        Initialize Realtime Hybrid Scanner

        Args:
            scan_interval: Seconds between scans
            hybrid_mode: Enable hybrid validation
            pump_min_confidence: Minimum pump confidence
            advanced_min_confidence: Minimum advanced confidence
            final_min_confidence: Minimum final confidence
        """
        self.scan_interval = scan_interval
        self.running = False

        logger.info("=" * 80)
        logger.info("🔄 REALTIME HYBRID SCANNER")
        logger.info("=" * 80)
        logger.info(f"Scan Interval: {scan_interval} seconds")
        logger.info(f"Hybrid Mode: {hybrid_mode}")
        logger.info(f"Pump Min: {pump_min_confidence}% | Advanced Min: {advanced_min_confidence}% | Final Min: {final_min_confidence}%")
        logger.info("=" * 80)

        # Initialize hybrid scanner
        self.scanner = HybridPumpScanner(
            hybrid_mode=hybrid_mode,
            pump_min_confidence=pump_min_confidence,
            advanced_min_confidence=advanced_min_confidence,
            final_min_confidence=final_min_confidence
        )

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("\n⚠️ Shutdown signal received. Stopping scanner...")
        self.running = False

    def run(self):
        """Start realtime scanning loop"""
        logger.info("\n🚀 Starting realtime hybrid scanner...")
        logger.info("Press Ctrl+C to stop\n")

        self.running = True
        scan_count = 0

        while self.running:
            scan_count += 1
            logger.info(f"\n{'=' * 80}")
            logger.info(f"SCAN #{scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'=' * 80}")

            try:
                # Run full scan
                signals = self.scanner.scan_all_symbols(exchange="gate.io")

                if signals:
                    logger.info(f"\n🎯 Generated {len(signals)} hybrid signals")
                    for signal in signals:
                        logger.info(f"   ✅ {signal['symbol']}: {signal['final_confidence']:.1f}% confidence")
                else:
                    logger.info(f"\n💤 No signals generated (no opportunities)")

            except Exception as e:
                logger.error(f"❌ Scan error: {e}")

            # Wait for next scan
            if self.running:
                logger.info(f"\n⏸️ Waiting {self.scan_interval} seconds until next scan...")
                for i in range(self.scan_interval):
                    if not self.running:
                        break
                    time.sleep(1)

        logger.info("\n✅ Realtime scanner stopped gracefully")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Realtime Hybrid Pump Scanner')
    parser.add_argument('--interval', type=int, default=30,
                       help='Scan interval in seconds (default: 30)')
    parser.add_argument('--pump-only', action='store_true',
                       help='Disable hybrid mode (pump detection only)')
    parser.add_argument('--pump-min', type=float, default=60.0,
                       help='Minimum pump confidence (default: 60.0)')
    parser.add_argument('--advanced-min', type=float, default=65.0,
                       help='Minimum advanced confidence (default: 65.0)')
    parser.add_argument('--final-min', type=float, default=70.0,
                       help='Minimum final confidence (default: 70.0)')

    args = parser.parse_args()

    # Create scanner
    scanner = RealtimeHybridScanner(
        scan_interval=args.interval,
        hybrid_mode=not args.pump_only,
        pump_min_confidence=args.pump_min,
        advanced_min_confidence=args.advanced_min,
        final_min_confidence=args.final_min
    )

    # Run
    scanner.run()


if __name__ == "__main__":
    main()
