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

    # === New Layer 2 & Scaling (2024-2025) ===
    "STRKUSDT",     # Starknet
    "MANTAUSDT",    # Manta Network
    "ZKUSDT",       # ZKsync
    "BEAMXUSDT",    # Beam
    "ZKSYNCUSDT",   # ZKsync Era

    # === New Meme Coins (High Pump Potential) ===
    "BOMEUSDT",     # Book of Meme
    "MYRIAUSDT",    # Myria
    "ORDIUSDT",     # Ordinals
    "SATSUSDT",     # Satoshis

    # === AI & Big Data (Trending 2024-2025) ===
    "TAOLUSDT",     # Bittensor
    "IQUSDT",       # Everipedia
    "NMRUSDT",      # Numerai

    # === Gaming & Metaverse (New) ===
    "RONUSDT",      # Ronin
    "PIXELUSDT",    # Pixels
    "PORTALUSDT",   # Portal
    "XAIUSDT",      # Xai
    "NFTUSDT",      # APENFT
    "ACEUSDT",      # Endurance

    # === DeFi 2.0 (New Protocols) ===
    "JUPUSDT",      # Jupiter
    "PYTHUSDT",     # Pyth Network
    "WUSDT",        # Wormhole
    "PENDLEUSDT",   # Pendle
    "RDNTUSDT",     # Radiant Capital

    # === RWA (Real World Assets - Hot Sector!) ===
    "ONDOUSDT",     # Ondo Finance
    "POLYSUSDT",    # Polymath

    # === More DePIN ===
    "HNTUSDT",      # Helium

    # === Infrastructure & Oracles ===
    "CELRUSDT",     # Celer Network
    "SKLUSDT",      # SKALE
    "BANDUSDT",     # Band Protocol
    "ANKRUSDT",     # Ankr

    # === Established Altcoins (Not Yet Added) ===
    "BCHUSDT",      # Bitcoin Cash
    "ZECUSDT",      # Zcash
    "QTUMUSDT",     # Qtum
    "BATUSDT",      # Basic Attention
    "ZRXUSDT",      # 0x Protocol
    "KSMUSDT",      # Kusama
    "RENUSDT",      # Ren
    "RSRUSDT",      # Reserve Rights
    "COTIUSDT",     # COTI
    "REEFUSDT",     # Reef
    "KLAYUSDT",     # Klaytn
    "AUDIOUSDT",    # Audius
    "ALPHAUSDT",    # Alpha Finance
    "SFPUSDT",      # SafePal
    "PERPUSDT",     # Perpetual Protocol
    "SUPERUSDT",    # SuperFarm
    "CFXUSDT",      # Conflux
    "TLMUSDT",      # Alien Worlds
    "FORTHUSDT",    # Ampleforth
    "BAKEUSDT",     # BakeryToken
    "SLPUSDT",      # Smooth Love Potion
    "C98USDT",      # Coin98
    "CLVUSDT",      # Clover Finance
    "QIUSDT",       # BENQI
    "YGGUSDT",      # Yield Guild Games
    "BICOUSDT",     # Biconomy
    "AXLUSDT",      # Axelar
    "RAREUSDT",     # SuperRare
    "ENSUSDT",      # Ethereum Name Service
    "API3USDT",     # API3
    "IDEXUSDT",     # IDEX
    "POLYXUSDT",    # Polymesh
    "GMXUSDT",      # GMX
    "BLURUSDT",     # Blur (if not duplicate)
    "BELUSDT",      # Bella Protocol
    "DUSKUSDT",     # Dusk Network
    "RVNUSDT",      # Ravencoin
    "MOVRUSDT",     # Mover
    "ACHUSDT",      # Alchemy Pay
    "GLMRUSDT",     # Golem
    "BTCSTUSDT",    # Bitcoin Standard Hashrate
    "STPTUSDT",     # STP Network
    "TRIBEUSDT",    # Tribe
    "MOBUSDT",      # MobileCoin
    "VGXUSDT",      # Voyager
    "CTSIUSDT",     # Cartesi
    "WNXMUSDT",     # Wrapped NXM
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

    # === New Layer 2 & Scaling (2024-2025) ===
    "STRK_USDT",     # Starknet
    "MANTA_USDT",    # Manta Network
    "ZK_USDT",       # ZKsync
    "BEAMX_USDT",    # Beam

    # === New Meme Coins (High Pump Potential) ===
    "BOME_USDT",     # Book of Meme
    "MYRIA_USDT",    # Myria
    "ORDI_USDT",     # Ordinals
    "SATS_USDT",     # Satoshis

    # === AI & Big Data (Trending 2024-2025) ===
    "TAO_USDT",      # Bittensor
    "IQ_USDT",       # Everipedia
    "NMR_USDT",      # Numerai

    # === Gaming & Metaverse (New) ===
    "RON_USDT",      # Ronin
    "PIXEL_USDT",    # Pixels
    "PORTAL_USDT",   # Portal
    "XAI_USDT",      # Xai
    "NFT_USDT",      # APENFT
    "ACE_USDT",      # Endurance

    # === DeFi 2.0 (New Protocols) ===
    "JUP_USDT",      # Jupiter
    "PYTH_USDT",     # Pyth Network
    "W_USDT",        # Wormhole
    "PENDLE_USDT",   # Pendle
    "RDNT_USDT",     # Radiant Capital

    # === RWA (Real World Assets - Hot Sector!) ===
    "ONDO_USDT",     # Ondo Finance
    "POLYX_USDT",    # Polymesh

    # === More DePIN ===
    "HNT_USDT",      # Helium

    # === Infrastructure & Oracles ===
    "CELR_USDT",     # Celer Network
    "SKL_USDT",      # SKALE
    "BAND_USDT",     # Band Protocol
    "ANKR_USDT",     # Ankr

    # === Established Altcoins (Not Yet Added) ===
    "BCH_USDT",      # Bitcoin Cash
    "ZEC_USDT",      # Zcash
    "QTUM_USDT",     # Qtum
    "BAT_USDT",      # Basic Attention
    "ZRX_USDT",      # 0x Protocol
    "KSM_USDT",      # Kusama
    "REN_USDT",      # Ren
    "RSR_USDT",      # Reserve Rights
    "COTI_USDT",     # COTI
    "REEF_USDT",     # Reef
    "KLAY_USDT",     # Klaytn
    "AUDIO_USDT",    # Audius
    "ALPHA_USDT",    # Alpha Finance
    "SFP_USDT",      # SafePal
    "PERP_USDT",     # Perpetual Protocol
    "SUPER_USDT",    # SuperFarm
    "CFX_USDT",      # Conflux
    "TLM_USDT",      # Alien Worlds
    "FORTH_USDT",    # Ampleforth
    "BAKE_USDT",     # BakeryToken
    "SLP_USDT",      # Smooth Love Potion
    "C98_USDT",      # Coin98
    "CLV_USDT",      # Clover Finance
    "QI_USDT",       # BENQI
    "YGG_USDT",      # Yield Guild Games
    "BICO_USDT",     # Biconomy
    "AXL_USDT",      # Axelar
    "RARE_USDT",     # SuperRare
    "ENS_USDT",      # Ethereum Name Service
    "API3_USDT",     # API3
    "IDEX_USDT",     # IDEX
    "GMX_USDT",      # GMX
    "BEL_USDT",      # Bella Protocol
    "DUSK_USDT",     # Dusk Network
    "RVN_USDT",      # Ravencoin
    "MOVR_USDT",     # Mover
    "ACH_USDT",      # Alchemy Pay
    "GLMR_USDT",     # Golem/Moonbeam
    "STPT_USDT",     # STP Network
    "CTSI_USDT",     # Cartesi
]

# Volume ve Market Cap Filtreleri
MIN_24H_VOLUME = 1_000_000  # Minimum $1M 24h volume
MIN_MARKET_CAP = 10_000_000  # Minimum $10M market cap

# Pump Detection İçin Öncelikli Coinler
# Düşük market cap = yüksek pump potansiyeli
HIGH_PUMP_POTENTIAL = [
    # Meme Coins (Extreme Pump Potential)
    "PEPEUSDT", "SHIBUSDT", "FLOKIUSDT", "BONKUSDT", "WIFUSDT", "MEMEUSDT",
    "BOMEUSDT", "ORDIUSDT", "SATSUSDT",  # 2024-2025 New Memes

    # New L1/L2 (High Volatility)
    "ARBUSDT", "OPUSDT", "SUIUSDT", "SEIUSDT", "TIAUSDT", "APTUSDT",
    "STRKUSDT", "MANTAUSDT", "ZKUSDT", "BEAMXUSDT",  # New Layer 2s

    # AI Tokens (Trending Sector - HOT!)
    "WLDUSDT", "FETUSDT", "AGIXUSDT", "ARKMUSDT", "RENDERUSDT",
    "TAOLUSDT", "NMRUSDT", "IQUSDT",  # New AI Tokens

    # Gaming & Metaverse (Community Driven)
    "GALAUSDT", "SANDUSDT", "AXSUSDT", "APEUSDT", "GMTUSDT", "BLURUSDT",
    "RONUSDT", "PIXELUSDT", "PORTALUSDT", "XAIUSDT",  # New Gaming

    # DeFi 2.0 (Yield Farming Pumps)
    "YFIUSDT", "1INCHUSDT", "SUSHIUSDT", "CRVUSDT",
    "JUPUSDT", "PYTHUSDT", "PENDLEUSDT", "GMXUSDT",  # New DeFi

    # RWA (Real World Assets - 2025 Trend!)
    "ONDOUSDT", "POLYSUSDT",

    # Low Cap Altcoins (High Risk/Reward)
    "JASMYUSDT", "ONEUSDT", "CKBUSDT", "HOTUSDT", "IOTXUSDT",
    "MYRIAUSDT", "NFTUSDT", "ACEUSDT",  # More Low Caps

    # Layer 1 Competitors (Pump on News)
    "FTMUSDT", "ROSEUSDT", "KAVAUSDT", "NEARUSDT",
    "HNTUSDT", "CELRUSDT",  # More L1s
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
