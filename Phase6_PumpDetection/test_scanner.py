"""
Test Hybrid Pump Scanner
Tests the complete hybrid signal generation system
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Phase6_PumpDetection.hybrid_pump_scanner import HybridPumpScanner

def main():
    print('\n' + '='*80)
    print('🔍 HYBRID PUMP SCANNER - COMPREHENSIVE TEST')
    print('='*80)

    # Initialize scanner
    scanner = HybridPumpScanner()

    # Test symbols
    test_symbols = ['BTC_USDT', 'ETH_USDT', 'SOL_USDT']

    signals_found = 0

    for symbol in test_symbols:
        print(f'\n{"="*80}')
        print(f'Testing {symbol}...')
        print(f'{"="*80}')

        signal = scanner.scan_symbol(symbol, 'gate.io')

        if signal:
            signals_found += 1
            print(f'\n✅ SIGNAL GENERATED!')
            print(f'\n   📊 Symbol: {signal["symbol"]}')
            print(f'   📈 Direction: {signal["direction"]}')
            print(f'   🎯 Final Confidence: {signal["final_confidence"]:.1f}%')
            print(f'      ├─ Pump Confidence: {signal["pump_confidence"]:.1f}%')
            print(f'      └─ Advanced Confidence: {signal["advanced_confidence"]:.1f}%')

            print(f'\n   💰 Price Levels:')
            print(f'      Entry: ${signal["entry_price"]:.2f}')
            print(f'      Stop Loss: ${signal["stop_loss"]:.2f} ({((signal["stop_loss"] - signal["entry_price"]) / signal["entry_price"] * 100):.2f}%)')
            print(f'      Take Profit: ${signal["take_profit"]:.2f} (+{((signal["take_profit"] - signal["entry_price"]) / signal["entry_price"] * 100):.2f}%)')
            print(f'      R:R Ratio: 1:{signal["risk_reward_ratio"]:.2f}')

            print(f'\n   📊 Component Scores:')
            adv_scores = signal.get('advanced_scores', {})
            print(f'      Trend: {adv_scores.get("trend", 0):.1f}/100')
            print(f'      Momentum: {adv_scores.get("momentum", 0):.1f}/100')
            print(f'      Volume: {adv_scores.get("volume", 0):.1f}/100')
            print(f'      Volatility: {adv_scores.get("volatility", 0):.1f}/100')
            print(f'      Pattern: {adv_scores.get("pattern", 0):.1f}/100')
            print(f'      Multi-TF Confluence: {adv_scores.get("multi_tf", 0):.1f}/100')

            print(f'\n   ⚖️ Risk Management:')
            print(f'      Position Size: ${signal["recommended_position_size"]:.2f}')
            print(f'      Risk Score: {signal["risk_score"]:.1f}/100')

            print(f'\n   ⏰ Timestamp: {signal["timestamp"]}')
            print(f'   📈 Timeframes: {", ".join(signal["timeframes_analyzed"])}')
            print(f'   🔢 Indicators: {signal["indicators_count"]}')

        else:
            print('\n❌ No signal generated (below threshold)')

    print(f'\n{"="*80}')
    print(f'📊 SUMMARY')
    print(f'{"="*80}')
    print(f'   Symbols Tested: {len(test_symbols)}')
    print(f'   Signals Generated: {signals_found}')
    print(f'   Success Rate: {signals_found/len(test_symbols)*100:.1f}%')
    print(f'{"="*80}\n')


if __name__ == "__main__":
    main()
