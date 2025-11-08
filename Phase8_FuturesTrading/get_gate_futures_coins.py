"""
Get Gate.io Futures Trading Pairs
Fetches all available futures contracts from Gate.io
"""
import requests
import json
from datetime import datetime

def get_gate_futures_contracts():
    """
    Fetch all futures contracts from Gate.io API

    Returns:
        list: List of contract symbols (e.g., ['BTC_USDT', 'ETH_USDT', ...])
    """
    url = "https://api.gateio.ws/api/v4/futures/usdt/contracts"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        contracts = response.json()

        # Filter active contracts
        active_contracts = [
            contract['name'] for contract in contracts
            if contract.get('in_delisting') == False
        ]

        print(f"\n{'='*80}")
        print(f"GATE.IO FUTURES CONTRACTS")
        print(f"{'='*80}")
        print(f"Total Active Contracts: {len(active_contracts)}")
        print(f"Fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        # Print first 20 contracts as sample
        print("Sample Contracts (first 20):")
        for i, symbol in enumerate(active_contracts[:20], 1):
            print(f"   {i:2d}. {symbol}")

        if len(active_contracts) > 20:
            print(f"   ... and {len(active_contracts) - 20} more")

        print(f"\n{'='*80}\n")

        return active_contracts

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching contracts from API: {e}")
        print(f"⚠️ Using fallback default list...")

        # Fallback: Top Gate.io futures contracts
        default_contracts = [
            'BTC_USDT', 'ETH_USDT', 'BNB_USDT', 'SOL_USDT', 'XRP_USDT',
            'ADA_USDT', 'DOGE_USDT', 'MATIC_USDT', 'DOT_USDT', 'AVAX_USDT',
            'LINK_USDT', 'ATOM_USDT', 'UNI_USDT', 'LTC_USDT', 'BCH_USDT',
            'NEAR_USDT', 'APT_USDT', 'ARB_USDT', 'OP_USDT', 'FTM_USDT',
            'ALGO_USDT', 'VET_USDT', 'ICP_USDT', 'FIL_USDT', 'SAND_USDT',
            'MANA_USDT', 'AAVE_USDT', 'GRT_USDT', 'ETC_USDT', 'XLM_USDT',
            'THETA_USDT', 'EOS_USDT', 'TRX_USDT', 'AXS_USDT', 'EGLD_USDT',
            'RUNE_USDT', 'ZEC_USDT', 'DASH_USDT', 'COMP_USDT', 'SNX_USDT',
            'MKR_USDT', 'SUSHI_USDT', 'YFI_USDT', 'BAT_USDT', 'ZIL_USDT',
            'ENJ_USDT', 'CHZ_USDT', 'HBAR_USDT', 'FLOW_USDT', 'ONE_USDT'
        ]

        print(f"✅ Using {len(default_contracts)} default contracts")
        return default_contracts


def save_contracts_to_file(contracts, filename='gate_futures_coins.json'):
    """Save contracts to JSON file"""
    with open(filename, 'w') as f:
        json.dump({
            'contracts': contracts,
            'count': len(contracts),
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    print(f"✅ Saved {len(contracts)} contracts to {filename}")


def get_top_volume_contracts(limit=50):
    """
    Get top contracts by 24h volume

    Args:
        limit: Number of top contracts to return

    Returns:
        list: Top contracts by volume
    """
    url = "https://api.gateio.ws/api/v4/futures/usdt/contracts"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        contracts = response.json()

        # Filter and sort by volume
        active_contracts = [
            {
                'symbol': contract['name'],
                'volume': float(contract.get('trade_size', 0))
            }
            for contract in contracts
            if contract.get('in_delisting') == False
        ]

        # Sort by volume
        sorted_contracts = sorted(
            active_contracts,
            key=lambda x: x['volume'],
            reverse=True
        )[:limit]

        symbols = [c['symbol'] for c in sorted_contracts]

        print(f"\n{'='*80}")
        print(f"TOP {limit} GATE.IO FUTURES BY VOLUME")
        print(f"{'='*80}")

        for i, contract in enumerate(sorted_contracts, 1):
            print(f"   {i:2d}. {contract['symbol']:15s} - Volume: {contract['volume']:,.0f}")

        print(f"\n{'='*80}\n")

        return symbols

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching contracts from API: {e}")
        print(f"⚠️ Using fallback default list...")

        # Fallback
        all_contracts = get_gate_futures_contracts()  # Will use fallback list
        return all_contracts[:limit]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Get Gate.io Futures Contracts')
    parser.add_argument('--top', type=int, default=0,
                       help='Get top N contracts by volume (default: all)')
    parser.add_argument('--save', action='store_true',
                       help='Save contracts to JSON file')

    args = parser.parse_args()

    if args.top > 0:
        contracts = get_top_volume_contracts(args.top)
    else:
        contracts = get_gate_futures_contracts()

    if args.save and contracts:
        save_contracts_to_file(contracts)

    print(f"✅ Found {len(contracts)} contracts")
