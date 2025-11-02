"""
ClaudeCodeCoin - Trading Pairs Configuration

Tüm exchange'ler için izlenecek coin listesi
"""

# Binance USDT Pairs - Comprehensive Coverage (100+ coins)
BINANCE_SYMBOLS = [
    # === Top 10 Market Cap ===
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

    # === Top 20 Volume ===
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
    "VETUSDT",      # VeChain
    "ALGOUSDT",     # Algorand
    "ICPUSDT",      # Internet Computer
    "HBARUSDT",     # Hedera

    # === High Volatility / Pump Candidates ===
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
    "ROSEUSDT",     # Oasis Network
    "FTMUSDT",      # Fantom
    "KAVAUSDT",     # Kava
    "QNTUSDT",      # Quant

    # === DeFi Ecosystem ===
    "AAVEUSDT",     # Aave
    "MKRUSDT",      # Maker
    "COMPUSDT",     # Compound
    "CRVUSDT",      # Curve
    "SNXUSDT",      # Synthetix
    "SUSHIUSDT",    # SushiSwap
    "1INCHUSDT",    # 1inch
    "YFIUSDT",      # Yearn Finance
    "BALUSDT",      # Balancer
    "LRCUSDT",      # Loopring
    "ENJUSDT",      # Enjin
    "CHZUSDT",      # Chiliz
    "ZILUSDT",      # Zilliqa

    # === Layer 2 & Scaling ===
    "STXUSDT",      # Stacks
    "IMXUSDT",      # Immutable X
    "RUNEUSDT",     # THORChain
    "METISUSDT",    # Metis
    "LDOUSDT",      # Lido DAO

    # === AI & Data Tokens (TRENDING!) ===
    "WLDUSDT",      # Worldcoin
    "FETUSDT",      # Fetch.ai
    "AGIXUSDT",     # SingularityNET
    "OCEANUSDT",    # Ocean Protocol
    "GRTUSDT",      # The Graph
    "ARKMUSDT",     # Arkham

    # === Meme Coins (High Volatility) ===
    "FLOKIUSDT",    # Floki
    "BONKUSDT",     # Bonk
    "WIFUSDT",      # dogwifhat
    "MEMEUSDT",     # Memecoin

    # === Gaming & Metaverse ===
    "SANDUSDT",     # Sandbox
    "MANAUSDT",     # Decentraland
    "AXSUSDT",      # Axie Infinity
    "GALAUSDT",     # Gala
    "BLURUSDT",     # Blur
    "ILVUSDT",      # Illuvium
    "MAGICUSDT",    # Magic (Treasure)
    "GMTUSDT",      # STEPN
    "APEUSDT",      # ApeCoin

    # === Privacy & Infrastructure ===
    "STORJUSDT",    # Storj
    "ARUSDT",       # Arweave
    "DASHUSDT",     # Dash
    "XMRUSDT",      # Monero (if listed)
    "SCUSDT",       # Siacoin

    # === DePIN (Decentralized Physical Infrastructure) ===
    "IOTXUSDT",     # IoTeX
    "HOTUSDT",      # Holo

    # === More Pump Candidates ===
    "JASMYUSDT",    # JasmyCoin
    "ONEUSDT",      # Harmony
    "CKBUSDT",      # Nervos Network
    "CELOUSDT",     # Celo
    "FLOWUSDT",     # Flow
    "THETAUSDT",    # Theta
    "EGLDUSDT",     # MultiversX (Elrond)
    "XTZUSDT",      # Tezos
    "EOSUSDT",      # EOS
    "NEOUSDT",      # Neo
    "WAVESUSDT",    # Waves
    "OMGUSDT",      # OMG Network
]

# Gate.io Pairs (underscore format) - Extended Coverage (80+ coins)
GATEIO_SYMBOLS = [
    # === Top Market Cap ===
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

    # === High Volume ===
    "TRX_USDT",
    "LINK_USDT",
    "ATOM_USDT",
    "LTC_USDT",
    "UNI_USDT",
    "ETC_USDT",
    "XLM_USDT",
    "FIL_USDT",
    "NEAR_USDT",
    "VET_USDT",
    "ALGO_USDT",
    "ICP_USDT",
    "HBAR_USDT",

    # === High Volatility / Pump Candidates ===
    "SHIB_USDT",
    "PEPE_USDT",
    "ARB_USDT",
    "OP_USDT",
    "APT_USDT",
    "SUI_USDT",
    "INJ_USDT",
    "SEI_USDT",
    "TIA_USDT",
    "RENDER_USDT",
    "ROSE_USDT",
    "FTM_USDT",
    "KAVA_USDT",
    "QNT_USDT",

    # === DeFi Ecosystem ===
    "AAVE_USDT",
    "MKR_USDT",
    "COMP_USDT",
    "CRV_USDT",
    "SNX_USDT",
    "SUSHI_USDT",
    "1INCH_USDT",
    "YFI_USDT",
    "BAL_USDT",
    "LRC_USDT",
    "ENJ_USDT",
    "CHZ_USDT",

    # === Layer 2 & Scaling ===
    "STX_USDT",
    "IMX_USDT",
    "RUNE_USDT",
    "METIS_USDT",
    "LDO_USDT",

    # === AI & Data (High Demand!) ===
    "WLD_USDT",
    "FET_USDT",
    "AGIX_USDT",
    "OCEAN_USDT",
    "GRT_USDT",
    "ARKM_USDT",

    # === Meme Coins (Extreme Volatility) ===
    "FLOKI_USDT",
    "BONK_USDT",
    "WIF_USDT",
    "MEME_USDT",

    # === Gaming & Metaverse ===
    "SAND_USDT",
    "MANA_USDT",
    "AXS_USDT",
    "GALA_USDT",
    "BLUR_USDT",
    "ILV_USDT",
    "MAGIC_USDT",
    "GMT_USDT",
    "APE_USDT",

    # === Privacy & Storage ===
    "STORJ_USDT",
    "AR_USDT",
    "DASH_USDT",
    "SC_USDT",

    # === DePIN Projects ===
    "IOTX_USDT",
    "HOT_USDT",

    # === More Altcoins (Pump Potential) ===
    "JASMY_USDT",
    "ONE_USDT",
    "CKB_USDT",
    "CELO_USDT",
    "FLOW_USDT",
    "THETA_USDT",
    "EGLD_USDT",
    "XTZ_USDT",
    "EOS_USDT",
    "NEO_USDT",
    "WAVES_USDT",
    "OMG_USDT",
    "ZIL_USDT",
]

# Volume ve Market Cap Filtreleri
MIN_24H_VOLUME = 1_000_000  # Minimum $1M 24h volume
MIN_MARKET_CAP = 10_000_000  # Minimum $10M market cap

# Pump Detection İçin Öncelikli Coinler
# Düşük market cap = yüksek pump potansiyeli
HIGH_PUMP_POTENTIAL = [
    # Meme Coins (Extreme Pump Potential)
    "PEPEUSDT", "SHIBUSDT", "FLOKIUSDT", "BONKUSDT", "WIFUSDT", "MEMEUSDT",

    # New L1/L2 (High Volatility)
    "ARBUSDT", "OPUSDT", "SUIUSDT", "SEIUSDT", "TIAUSDT", "APTUSDT",

    # AI Tokens (Trending Sector)
    "WLDUSDT", "FETUSDT", "AGIXUSDT", "ARKMUSDT", "RENDERUSDT",

    # Gaming & Metaverse (Community Driven)
    "GALAUSDT", "SANDUSDT", "AXSUSDT", "APEUSDT", "GMTUSDT", "BLURUSDT",

    # DeFi (Yield Farming Pumps)
    "YFIUSDT", "1INCHUSDT", "SUSHIUSDT", "CRVUSDT",

    # Low Cap Altcoins (High Risk/Reward)
    "JASMYUSDT", "ONEUSDT", "CKBUSDT", "HOTUSDT", "IOTXUSDT",

    # Layer 1 Competitors (Pump on News)
    "FTMUSDT", "ROSEUSDT", "KAVAUSDT", "NEARUSDT",
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
