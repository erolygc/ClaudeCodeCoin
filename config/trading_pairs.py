"""
ClaudeCodeCoin - Trading Pairs Configuration

Tüm exchange'ler için izlenecek coin listesi
"""

# Binance USDT Pairs - Top Volume Coins
BINANCE_SYMBOLS = [
    # Top 10 Market Cap
    "BTCUSDT",      # Bitcoin
    "ETHUSDT",      # Ethereum
    "BNBUSDT",      # Binance Coin
    "SOLUSDT",      # Solana
    "XRPUSDT",      # Ripple
    "ADAUSDT",      # Cardano
    "DOGEUSDT",     # Dogecoin
    "MATICUSDT",    # Polygon
    "DOTUSDT",      # Polkadot
    "AVAXUSDT",     # Avalanche

    # Top 20 Volume
    "TRXUSDT",      # Tron
    "LINKUSDT",     # Chainlink
    "ATOMUSDT",     # Cosmos
    "LTCUSDT",      # Litecoin
    "UNIUSDT",      # Uniswap
    "ETCUSDT",      # Ethereum Classic
    "XLMUSDT",      # Stellar
    "FILUSDT",      # Filecoin
    "LDOUSDT",      # Lido DAO
    "NEARUSDT",     # Near Protocol

    # High Volatility / Pump Candidates
    "SHIBUSDT",     # Shiba Inu
    "PEPEUSDT",     # Pepe
    "ARBUSDT",      # Arbitrum
    "OPUSDT",       # Optimism
    "APTUSDT",      # Aptos
    "SUIUSDT",      # Sui
    "INJUSDT",      # Injective
    "TIAUSDT",      # Celestia
    "SEIUSDT",      # Sei
    "RENDERUSDT",   # Render Token

    # DeFi Tokens
    "AAVEUSDT",     # Aave
    "MKRUSDT",      # Maker
    "COMPUSDT",     # Compound
    "CRVUSDT",      # Curve
    "SNXUSDT",      # Synthetix

    # Layer 2 & Scaling
    "STXUSDT",      # Stacks
    "IMXUSDT",      # Immutable X
    "RUNEUSDT",     # THORChain

    # New Listings (High Pump Potential)
    "WLDUSDT",      # Worldcoin
    "FETUSDT",      # Fetch.ai
    "AGIXUSDT",     # SingularityNET
    "OCEANUSDT",    # Ocean Protocol
    "GRTUSDT",      # The Graph

    # Meme Coins (High Volatility)
    "FLOKIUSDT",    # Floki
    "BONKUSDT",     # Bonk

    # Gaming & Metaverse
    "SANDUSDT",     # Sandbox
    "MANAUSDT",     # Decentraland
    "AXSUSDT",      # Axie Infinity
    "GALAUSDT",     # Gala
]

# Gate.io Pairs (underscore format)
GATEIO_SYMBOLS = [
    # Top Market Cap
    "BTC_USDT",
    "ETH_USDT",
    "SOL_USDT",
    "XRP_USDT",
    "BNB_USDT",
    "ADA_USDT",
    "DOGE_USDT",
    "MATIC_USDT",
    "DOT_USDT",
    "AVAX_USDT",

    # High Volume
    "TRX_USDT",
    "LINK_USDT",
    "ATOM_USDT",
    "LTC_USDT",
    "UNI_USDT",
    "ETC_USDT",
    "XLM_USDT",
    "FIL_USDT",
    "NEAR_USDT",

    # Pump Candidates
    "SHIB_USDT",
    "PEPE_USDT",
    "ARB_USDT",
    "OP_USDT",
    "APT_USDT",
    "SUI_USDT",
    "INJ_USDT",
    "SEI_USDT",

    # DeFi
    "AAVE_USDT",
    "MKR_USDT",
    "COMP_USDT",
    "CRV_USDT",
    "SNX_USDT",

    # New & Trending
    "WLD_USDT",
    "FET_USDT",
    "GRT_USDT",

    # Meme Coins
    "FLOKI_USDT",
    "BONK_USDT",

    # Gaming
    "SAND_USDT",
    "MANA_USDT",
    "AXS_USDT",
    "GALA_USDT",
]

# Volume ve Market Cap Filtreleri
MIN_24H_VOLUME = 1_000_000  # Minimum $1M 24h volume
MIN_MARKET_CAP = 10_000_000  # Minimum $10M market cap

# Pump Detection İçin Öncelikli Coinler
# Düşük market cap = yüksek pump potansiyeli
HIGH_PUMP_POTENTIAL = [
    "PEPEUSDT", "SHIBUSDT", "FLOKIUSDT", "BONKUSDT",  # Meme coins
    "ARBUSDT", "OPUSDT", "SUIUSDT", "SEIUSDT",         # New L1/L2
    "WLDUSDT", "FETUSDT", "AGIXUSDT",                  # AI tokens
    "GALAUSDT", "SANDUSDT", "AXSUSDT",                 # Gaming
]

# Collector Ayarları
COLLECTOR_CONFIG = {
    "binance": {
        "symbols": BINANCE_SYMBOLS,
        "interval": "1m",
        "max_symbols_per_stream": 50,  # WebSocket limiti
    },
    "gateio": {
        "symbols": GATEIO_SYMBOLS,
        "interval": "1m",
        "max_symbols_per_stream": 50,
    }
}

# Pump Scanner Ayarları
PUMP_SCANNER_CONFIG = {
    "scan_interval": 60,  # 60 saniye
    "alert_cooldown": 300,  # 5 dakika
    "min_confidence": 50,  # Minimum %50 confidence
    "min_bars": 50,  # Minimum veri gereksinimi
    "priority_symbols": HIGH_PUMP_POTENTIAL,
}

def get_binance_symbols():
    """Binance sembol listesi"""
    return BINANCE_SYMBOLS

def get_gateio_symbols():
    """Gate.io sembol listesi"""
    return GATEIO_SYMBOLS

def get_all_symbols():
    """Tüm semboller"""
    return {
        "binance": BINANCE_SYMBOLS,
        "gateio": GATEIO_SYMBOLS
    }

def get_priority_symbols():
    """Yüksek pump potansiyelli coinler"""
    return HIGH_PUMP_POTENTIAL

if __name__ == "__main__":
    print("="*70)
    print("📊 ClaudeCodeCoin - Trading Pairs Configuration")
    print("="*70)
    print()
    print(f"Binance Symbols: {len(BINANCE_SYMBOLS)}")
    print(f"Gate.io Symbols: {len(GATEIO_SYMBOLS)}")
    print(f"High Pump Potential: {len(HIGH_PUMP_POTENTIAL)}")
    print()
    print("Top 10 Binance Symbols:")
    for i, symbol in enumerate(BINANCE_SYMBOLS[:10], 1):
        print(f"  {i}. {symbol}")
    print()
    print("High Pump Potential Coins:")
    for symbol in HIGH_PUMP_POTENTIAL:
        print(f"  🔥 {symbol}")
