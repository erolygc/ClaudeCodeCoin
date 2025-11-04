"""
ClaudeCodeCoin - Trading Pairs Configuration (EXPANDED - 1000+ Coins)

1000 coin ile yüksek doğruluk pump detection için
"""

# ============================================================================
# BINANCE USDT PAIRS - COMPREHENSIVE (500+ coins)
# ============================================================================

BINANCE_SYMBOLS = [
    # === Top 30 Market Cap (Tier 1) ===
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "MATICUSDT", "DOTUSDT", "AVAXUSDT",
    "TRXUSDT", "LINKUSDT", "ATOMUSDT", "LTCUSDT", "UNIUSDT",
    "ETCUSDT", "XLMUSDT", "FILUSDT", "LDOUSDT", "NEARUSDT",
    "VETUSDT", "ALGOUSDT", "ICPUSDT", "HBARUSDT", "BCHUSDT",
    "QNTUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "MANAUSDT",

    # === Top 60 Market Cap (Tier 2) ===
    "SANDUSDT", "AAVEUSDT", "MKRUSDT", "EGLDUSDT", "AXSUSDT",
    "THETAUSDT", "EOSUSDT", "XTZUSDT", "FLOWUSDT", "FTMUSDT",
    "GRTUSDT", "INJUSDT", "NEOUSDT", "KLAYUSDT", "CHZUSDT",
    "ENJUSDT", "SNXUSDT", "CRVUSDT", "COMPUSDT", "YFIUSDT",
    "SUSHIUSDT", "1INCHUSDT", "RUNEUSDT", "ZILUSDT", "WAVESUSDT",
    "IOTXUSDT", "ZECUSDT", "DASHUSDT", "QTUMUSDT", "BATUSDT",

    # === Meme Coins (High Pump Potential) ===
    "SHIBUSDT", "PEPEUSDT", "FLOKIUSDT", "BONKUSDT", "WIFUSDT",
    "MEMEUSDT", "BOMEUSDT", "ORDIUSDT", "SATSUSDT", "RATSUSDT",
    "AIUSDT", "NFTUSDT", "TURBOUSDT", "BABYDOGEUSDT", "SAMOUSDT",

    # === Layer 2 & Scaling Solutions ===
    "STXUSDT", "IMXUSDT", "METISUSDT", "STRKUSDT", "MANTAUSDT",
    "ZKUSDT", "BEAMXUSDT", "CELRUSDT", "SKLUSDT", "POLYXUSDT",
    "LRCUSDT", "OMGUSDT", "MATICUSDT", "AXLUSDT", "CTSIUSDT",

    # === AI & Machine Learning (HOT SECTOR!) ===
    "WLDUSDT", "FETUSDT", "AGIXUSDT", "OCEANUSDT", "ARKMUSDT",
    "TAOLUSDT", "NMRUSDT", "IQUSDT", "RENDERUSDT", "PHBUSDT",
    "AIUSDT", "RNDRETH", "GPTUSDT", "AIOZUSDT", "CGPTUSDT",

    # === Gaming & Metaverse (Tier 1) ===
    "GALAUSDT", "BLURUSDT", "ILVUSDT", "MAGICUSDT", "GMTUSDT",
    "APEUSDT", "RONUSDT", "PIXELUSDT", "PORTALUSDT", "XAIUSDT",
    "ACEUSDT", "YGGUSDT", "TLMUSDT", "MCUSDT", "GHSTUSDT",
    "ALICEUSDT", "SLPUSDT", "PETSUSDT", "RAREUSDT", "DEGOUSDT",

    # === DeFi 2.0 & DEX Tokens ===
    "JUPUSDT", "PYTHUSDT", "WUSDT", "PENDLEUSDT", "RDNTUSDT",
    "GMXUSDT", "BALUSDT", "RADUSDT", "DYDXUSDT", "CVXUSDT",
    "CAKEUSDT", "BEFIUSDT", "ANKRUSDT", "BANDUSDT", "OOKIUSDT",
    "PERPUSDT", "DUSKUSDT", "PROSUSDT", "BADGERUSDT", "DIAUSDT",

    # === RWA (Real World Assets - 2025 Trend!) ===
    "ONDOUSDT", "POLYSUSDT", "CFXUSDT", "RIOUSA", "ACHUSDT",
    "XVSUSDT", "ALPINUSDT", "LOKAUSDT", "VITEUSDT", "KEYUSDT",

    # === DePIN (Decentralized Physical Infrastructure) ===
    "HNTUSDT", "HOTUSDT", "IOTAUSDT", "MOBUSDT", "RLCUSDT",
    "GNSUSDT", "PONDUSDT", "PNTSUSDT", "RPLUSDT", "REPUSDT",

    # === New Layer 1 Blockchains ===
    "SUIUSDT", "SEIUSDT", "TIAUSDT", "APTUSDT", "KAVAUSDT",
    "ROSEUSDT", "CELUSDT", "MINA", "CELOUSDT", "AGLDUSDT",
    "KSMUSDT", "MOVRUSDT", "GLMRUSDT", "SCRTUSDT", "TFUELUSDT",

    # === Oracles & Infrastructure ===
    "API3USDT", "TRBUSDT", "FLUXUSDT", "DIAUSDT", "ERNUSDT",
    "BNTUSDT", "MLNUSDT", "REQUSDT", "QKCUSDT", "CELOUSDT",

    # === Privacy Coins ===
    "XMRUSDT", "SCUSDT", "RENUSDT", "TORNUSDT", "KEEPUSDT",
    "NUUSDT", "NUTUSDT", "PRQUSDT", "XZCUSDT", "BEAMUSDT",

    # === Established Altcoins (Top 200) ===
    "RVNUSDT", "ONTUSDT", "WANUSDT", "WAXPUSDT", "NKNUSDT",
    "OGNUSDT", "LSKUSDT", "STMXUSDT", "FUNUSDT", "CHROMATICUSDT",
    "BTCSTUSDT", "TRUUSDT", "PAXGUSDT", "LUNCUSDT", "LUAUSDT",
    "USTCUSDT", "IDEXUSDT", "CTXCUSDT", "VTHUSDT", "PHAUSDT",

    # === Newer Listings (2024-2025) ===
    "ACHUSDT", "ALPACAUSDT", "PSGUSDT", "JUVUSDT", "ASRUSDT",
    "OGUSDT", "ATMUSDT", "BARUSDT", "LEVSUSDT", "FIDAUSDT",
    "LITUSDT", "FRONTUSDT", "BTCDOMUSDT", "CVPUSDT", "STRAXUSDT",
    "FORTHUSDT", "EZUSDT", "BELOUSDT", "WINGUSDT", "SWRVUSDT",

    # === More DeFi Protocols ===
    "GHSTUSDT", "QUICKUSDT", "UMAMUSDT", "VOXELUSDT", "HIGHUSDT",
    "PEOPLEUSDT", "ASTRUSDT", "ALPINEUSDT", "TUSDT", "SNTUSDT",
    "ARPAUSDT", "PROMOUDT", "XVGUSDT", "ATAUSDT", "GTCUSDT",

    # === Fan Tokens & Partnerships ===
    "SANTOSUSDT", "PORTOUSDT", "LAZIOUSA", "CHELSEAUSDT", "CITYUSDT",
    "NAVIUSDT", "IBUSDT", "BIFIUSDT", "DARUSDT", "MANAUSDT",

    # === More Gaming Tokens ===
    "SUPERUSDT", "SFPUSDT", "DFUSDT", "FISUSDT", "OMUSDT",
    "PONDCUSDT", "DEXEUSDT", "AUDUSDT", "BURGERUSDT", "SPAUSDT",

    # === Staking & Yield ===
    "BETAUSDT", "RAMPUSDT", "FXSUSDT", "CITYUSDT", "OOKIUSDT",
    "BICOUSDT", "FLUXUSDT", "VOXELUSDT", "JASMYUSDT", "PHAUSDT",

    # === More Layer 2 & Rollups ===
    "GALUSDT", "PUNDIXUSDT", "NULSUSDT", "CVXUSDT", "LUNA2USDT",
    "LOKSUSDT", "JAMUSDT", "POLUSDT", "MDXUSDT", "MASKUSDT",

    # === Infrastructure & Tools ===
    "DREPUSDT", "WNXMUSDT", "TVKUSDT", "BADGERUSDT", "FISUSDT",
    "OMUSDT", "PONDUSDT", "DEXEUSDT", "AUTOUSDT", "LIUSDT",

    # === Smaller Cap High Risk/Reward ===
    "C98USDT", "CLVUSDT", "QIUSDT", "TLMUSDT", "COTIUSDT",
    "REEFUSDT", "AUDIOUSDT", "ALPHAUSDT", "SFPUSDT", "PERPUSDT",
    "SUPERUSDT", "CFXUSDT", "FORTHUSDT", "BAKEUSDT", "SLPUSDT",

    # === More Mid-Cap Altcoins ===
    "BETAUSDT", "LINAUSDT", "COCOSUSDT", "VITEUSDT", "OXTUSDT",
    "ORNUSDT", "MDTUSDT", "STPTUSDT", "DATAUSDT", "CTSIUSDT",
    "WNXMUSDT", "TRIBEUSDT", "MOBUSDT", "VGXUSDT", "CTSIUSDT",

    # === Experimental & New ===
    "NBTUSDT", "STGUSDT", "ACHUSDT", "FORTHUSDT", "FIDAUSDT",
    "LPTUUSDT", "CTKUSDT", "TORNUSDT", "ERNUSDT", "KLAYUSDT",
    "BETAUSDT", "LINAUSDT", "IDEXUSDT", "COCOSUSDT", "VITEUSDT",

    # === More Options (Fill to 500+) ===
    "BTGUSDT", "DGBUSDT", "SYSUSDT", "VIACUSDT", "GXSUSDT",
    "PIXUSDT", "JOEUSDT", "SPELLUSDT", "BSWUSDT", "BIDRUSA",
    "ARDRUSA", "HIVEUSDT", "DENTUSDT", "BTGTUSDT", "REQUSDT",
    "VIBUSDT", "DLTUSDT", "MDAUSDT", "ACHUSDT", "COSUSDT",
    "MTLUSDT", "ONEUSDT", "CKBUSDT", "TFUELUSDT", "MIRUSDT",
    "BARUSDT", "ILVUSDT", "YGGUSDT", "FETUSDT", "ASTRUSDT",
    "ANKRUSDT", "FORTHUSDT", "PAXUSDT", "AUCTIONUSDT", "TVKUSDT",
    "LAZIUSDT", "SANTOSUSDT", "MCUSDT", "POWRUSDT", "VGXUSDT",

    # === Additional Top Volume Pairs (500-600) ===
    "AMBUSDT", "UMAUSDT", "POLYUSDT", "SYNUSDT", "PSGUSDT",
    "DGBUSDT", "MITHUSDT", "TWTUSDT", "MBLUSDT", "TOMOUSDT",
    "HNTUSDT", "AVUSDT", "BELUSDT", "WINGUSDT", "SWRVUSDT",
    "CREAMUSDT", "UNIUSDT", "FLMUSDT", "SCRTUSDT", "ORNUSDT",
    "UTUSDT", "XVSUSDT", "ALPHUSDT", "VIDUSDT", "AIONUSDT",
    "RLCUSDT", "MFTUSDT", "POLSUSDT", "MDXUSDT", "MASKUSDT",
    "LPTUSDT", "XVGUSDT", "ATAUSDT", "GTCUSDT", "TORNUSDT",
    "ERNUSDT", "KLAYUSDT", "PHAUSDT", "BONDUSDT", "MLNUSDT",
    "DEXEUSDT", "C98USDT", "CLVUSDT", "QIUSDT", "YGGUSDT",
    "FIOUSDT", "RADIUSDT", "AGLDUSDT", "RADUSDT", "BETAUSDT",
    "RAREUSDT", "LAZIOUSDT", "ADXUSDT", "AUCTIONUSDT", "DARUSDT",
    "BNXUSDT", "RGT", "MOVRUSDT", "CITYUSDT", "ENSUSDT",

    # === More DeFi & Yield (600-700) ===
    "ICXUSDT", "MINAUSDT", "RAYUSDT", "FARMUSTD", "ALCUSDT",
    "ASTRALUSDT", "GMTUSDT", "KDAUSDT", "APEUSDT", "BSWUSDT",
    "MULTIUSDT", "ASTRUSDT", "BSVUSDT", "HFTUSDT", "HOOKUSDT",
    "MAGICUSDT", "TUSDT", "RNDRUSDT", "HIGHUSDT", "MINAUSDT",
    "ASTUSAT", "GMXUSDT", "CFXUSDT", "STGUSDT", "RPLUSDT",
    "ACHUSDT", "SSVUSDT", "CKBUSDT", "PERPUSDT", "TRUUSDT",
    "LUAUSDT", "GALUSDT", "LDOUSDT", "EPXUSDT", "USTUSDT",
    "ASTRAUSDT", "GLMUSDT", "PROUSDT", "SYNUSDT", "VOXELUSDT",
    "IBUSDT", "PROSUSDT", "APTUSDT", "OSMOUSDT", "HFTUSDT",
    "PHBUSDT", "HOOKUSDT", "MAGICUSDT", "GFTUSDT", "MDTUSDT",

    # === Layer 1 & Infrastructure (700-800) ===
    "COMBOUSDT", "MAVUSDT", "PENDLEUSDT", "ARKMUSDT", "WLDUSDT",
    "FDUSDUSDT", "SEIUSDT", "CYBERUSDT", "HIFIUSDT", "ARKUSDT",
    "FRONTUSDT", "GLMRUSDT", "BICOUSDT", "FLUXUSDT", "VGXUSDT",
    "CVXUSDT", "AGIXUSDT", "NTRNUSDT", "ACEUSDT", "NFPUSDT",
    "AIUSDT", "XAIUSDT", "WIFUSDT", "MANTAUSDT", "ONDOUSDT",
    "LSKUSDT", "ALTUSDT", "JUPUSDT", "PYTHUSDT", "RONINUSDT",
    "DYMUSDT", "OMUSDT", "PIXELUSDT", "STRKUSDT", "PORTALUSDT",
    "PDAUSDT", "AXLUSDT", "WLDUSDT", "METISUSDT", "AEVOUSDT",
    "VANRYUSDT", "BOMEUSDT", "ETHFIUSDT", "ENAUSDT", "WUSDT",
    "TNSRUSDT", "SAGAUSDT", "TAOUSDT", "REZUSDT", "BBUSDT",
]

# ============================================================================
# GATE.IO PAIRS - COMPREHENSIVE (500+ coins)
# ============================================================================

GATEIO_SYMBOLS = [
    # === Top 30 Market Cap (Tier 1) ===
    "BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "BNB_USDT",
    "ADA_USDT", "DOGE_USDT", "MATIC_USDT", "DOT_USDT", "AVAX_USDT",
    "TRX_USDT", "LINK_USDT", "ATOM_USDT", "LTC_USDT", "UNI_USDT",
    "ETC_USDT", "XLM_USDT", "FIL_USDT", "NEAR_USDT", "VET_USDT",
    "ALGO_USDT", "ICP_USDT", "HBAR_USDT", "BCH_USDT", "QNT_USDT",
    "APT_USDT", "ARB_USDT", "OP_USDT", "MANA_USDT", "SAND_USDT",

    # === Top 60 Market Cap (Tier 2) ===
    "AAVE_USDT", "MKR_USDT", "EGLD_USDT", "AXS_USDT", "THETA_USDT",
    "EOS_USDT", "XTZ_USDT", "FLOW_USDT", "FTM_USDT", "GRT_USDT",
    "INJ_USDT", "NEO_USDT", "KLAY_USDT", "CHZ_USDT", "ENJ_USDT",
    "SNX_USDT", "CRV_USDT", "COMP_USDT", "YFI_USDT", "SUSHI_USDT",
    "1INCH_USDT", "RUNE_USDT", "ZIL_USDT", "WAVES_USDT", "IOTX_USDT",
    "ZEC_USDT", "DASH_USDT", "QTUM_USDT", "BAT_USDT", "LDO_USDT",

    # === Meme Coins (High Volatility) ===
    "SHIB_USDT", "PEPE_USDT", "FLOKI_USDT", "BONK_USDT", "WIF_USDT",
    "MEME_USDT", "BOME_USDT", "ORDI_USDT", "SATS_USDT", "RATS_USDT",
    "AI_USDT", "NFT_USDT", "TURBO_USDT", "BABYDOGE_USDT", "SAMO_USDT",

    # === Layer 2 & Scaling ===
    "STX_USDT", "IMX_USDT", "METIS_USDT", "STRK_USDT", "MANTA_USDT",
    "ZK_USDT", "BEAMX_USDT", "CELR_USDT", "SKL_USDT", "POLYX_USDT",
    "LRC_USDT", "OMG_USDT", "MATIC_USDT", "AXL_USDT", "CTSI_USDT",

    # === AI & Data (Trending!) ===
    "WLD_USDT", "FET_USDT", "AGIX_USDT", "OCEAN_USDT", "ARKM_USDT",
    "TAO_USDT", "NMR_USDT", "IQ_USDT", "RENDER_USDT", "PHB_USDT",
    "AI_USDT", "RNDR_USDT", "GPT_USDT", "AIOZ_USDT", "CGPT_USDT",

    # === Gaming & Metaverse ===
    "GALA_USDT", "BLUR_USDT", "ILV_USDT", "MAGIC_USDT", "GMT_USDT",
    "APE_USDT", "RON_USDT", "PIXEL_USDT", "PORTAL_USDT", "XAI_USDT",
    "ACE_USDT", "YGG_USDT", "TLM_USDT", "MC_USDT", "GHST_USDT",
    "ALICE_USDT", "SLP_USDT", "PETS_USDT", "RARE_USDT", "DEGO_USDT",

    # === DeFi 2.0 ===
    "JUP_USDT", "PYTH_USDT", "W_USDT", "PENDLE_USDT", "RDNT_USDT",
    "GMX_USDT", "BAL_USDT", "RAD_USDT", "DYDX_USDT", "CVX_USDT",
    "CAKE_USDT", "BIFI_USDT", "ANKR_USDT", "BAND_USDT", "OOKI_USDT",
    "PERP_USDT", "DUSK_USDT", "PROS_USDT", "BADGER_USDT", "DIA_USDT",

    # === RWA (Real World Assets) ===
    "ONDO_USDT", "POLYX_USDT", "CFX_USDT", "RIO_USDT", "ACH_USDT",
    "XVS_USDT", "ALPINE_USDT", "LOKA_USDT", "VITE_USDT", "KEY_USDT",

    # === DePIN Projects ===
    "HNT_USDT", "HOT_USDT", "IOTA_USDT", "MOB_USDT", "RLC_USDT",
    "GNS_USDT", "POND_USDT", "PNT_USDT", "RPL_USDT", "REP_USDT",

    # === New Layer 1s ===
    "SUI_USDT", "SEI_USDT", "TIA_USDT", "APT_USDT", "KAVA_USDT",
    "ROSE_USDT", "CEL_USDT", "MINA_USDT", "CELO_USDT", "AGLD_USDT",
    "KSM_USDT", "MOVR_USDT", "GLMR_USDT", "SCRT_USDT", "TFUEL_USDT",

    # === Oracles & Infrastructure ===
    "API3_USDT", "TRB_USDT", "FLUX_USDT", "DIA_USDT", "ERN_USDT",
    "BNT_USDT", "MLN_USDT", "REQ_USDT", "QKC_USDT", "CELO_USDT",

    # === Privacy Coins ===
    "XMR_USDT", "SC_USDT", "REN_USDT", "TORN_USDT", "KEEP_USDT",
    "NU_USDT", "NUT_USDT", "PRQ_USDT", "XZC_USDT", "BEAM_USDT",

    # === Established Altcoins ===
    "RVN_USDT", "ONT_USDT", "WAN_USDT", "WAXP_USDT", "NKN_USDT",
    "OGN_USDT", "LSK_USDT", "STMX_USDT", "FUN_USDT", "CHR_USDT",
    "BTCST_USDT", "TRU_USDT", "PAXG_USDT", "LUNC_USDT", "LUNA_USDT",
    "USTC_USDT", "IDEX_USDT", "CTXC_USDT", "VTH_USDT", "PHA_USDT",

    # === Newer Listings ===
    "ACH_USDT", "ALPACA_USDT", "PSG_USDT", "JUV_USDT", "ASR_USDT",
    "OG_USDT", "ATM_USDT", "BAR_USDT", "LEV_USDT", "FIDA_USDT",
    "LIT_USDT", "FRONT_USDT", "BTCDOM_USDT", "CVP_USDT", "STRAX_USDT",
    "FORTH_USDT", "EZ_USDT", "BEL_USDT", "WING_USDT", "SWRV_USDT",

    # === More DeFi ===
    "GHST_USDT", "QUICK_USDT", "UMA_USDT", "VOXEL_USDT", "HIGH_USDT",
    "PEOPLE_USDT", "ASTR_USDT", "ALPINE_USDT", "T_USDT", "SNT_USDT",
    "ARPA_USDT", "PROM_USDT", "XVG_USDT", "ATA_USDT", "GTC_USDT",

    # === Fan Tokens ===
    "SANTOS_USDT", "PORTO_USDT", "LAZIO_USDT", "CHELSEA_USDT", "CITY_USDT",
    "NAVI_USDT", "IB_USDT", "BIFI_USDT", "DAR_USDT", "MANA_USDT",

    # === More Gaming ===
    "SUPER_USDT", "SFP_USDT", "DF_USDT", "FIS_USDT", "OM_USDT",
    "PONDC_USDT", "DEXE_USDT", "AUD_USDT", "BURGER_USDT", "SPA_USDT",

    # === Staking & Yield ===
    "BETA_USDT", "RAMP_USDT", "FXS_USDT", "CITY_USDT", "OOKI_USDT",
    "BICO_USDT", "FLUX_USDT", "VOXEL_USDT", "JASMY_USDT", "PHA_USDT",

    # === More Layer 2 ===
    "GAL_USDT", "PUNDIX_USDT", "NULS_USDT", "CVX_USDT", "LUNA2_USDT",
    "LOKA_USDT", "JAM_USDT", "POL_USDT", "MDX_USDT", "MASK_USDT",

    # === Infrastructure ===
    "DREP_USDT", "WNXM_USDT", "TVK_USDT", "BADGER_USDT", "FIS_USDT",
    "OM_USDT", "POND_USDT", "DEXE_USDT", "AUTO_USDT", "LI_USDT",

    # === Small Cap High Risk ===
    "C98_USDT", "CLV_USDT", "QI_USDT", "TLM_USDT", "COTI_USDT",
    "REEF_USDT", "AUDIO_USDT", "ALPHA_USDT", "SFP_USDT", "PERP_USDT",
    "SUPER_USDT", "CFX_USDT", "FORTH_USDT", "BAKE_USDT", "SLP_USDT",

    # === More Mid-Cap ===
    "BETA_USDT", "LINA_USDT", "COCOS_USDT", "VITE_USDT", "OXT_USDT",
    "ORN_USDT", "MDT_USDT", "STPT_USDT", "DATA_USDT", "CTSI_USDT",
    "WNXM_USDT", "TRIBE_USDT", "MOB_USDT", "VGX_USDT", "CTSI_USDT",

    # === Experimental ===
    "NBT_USDT", "STG_USDT", "ACH_USDT", "FORTH_USDT", "FIDA_USDT",
    "LPT_USDT", "CTK_USDT", "TORN_USDT", "ERN_USDT", "KLAY_USDT",
    "BETA_USDT", "LINA_USDT", "IDEX_USDT", "COCOS_USDT", "VITE_USDT",

    # === More Options (Fill to 500+) ===
    "BTG_USDT", "DGB_USDT", "SYS_USDT", "VIA_USDT", "GXS_USDT",
    "PIX_USDT", "JOE_USDT", "SPELL_USDT", "BSW_USDT", "BIDR_USDT",
    "ARDR_USDT", "HIVE_USDT", "DENT_USDT", "BTGT_USDT", "REQ_USDT",
    "VIB_USDT", "DLT_USDT", "MDA_USDT", "ACH_USDT", "COS_USDT",
    "MTL_USDT", "ONE_USDT", "CKB_USDT", "TFUEL_USDT", "MIR_USDT",
    "BAR_USDT", "ILV_USDT", "YGG_USDT", "FET_USDT", "ASTR_USDT",
    "ANKR_USDT", "FORTH_USDT", "PAX_USDT", "AUCTION_USDT", "TVK_USDT",
    "LAZIO_USDT", "SANTOS_USDT", "MC_USDT", "POWR_USDT", "VGX_USDT",

    # === Additional Top Volume Pairs (500-600) ===
    "AMB_USDT", "UMA_USDT", "POLY_USDT", "SYN_USDT", "PSG_USDT",
    "DGB_USDT", "MITH_USDT", "TWT_USDT", "MBL_USDT", "TOMO_USDT",
    "HNT_USDT", "AV_USDT", "BEL_USDT", "WING_USDT", "SWRV_USDT",
    "CREAM_USDT", "UNI_USDT", "FLM_USDT", "SCRT_USDT", "ORN_USDT",
    "UT_USDT", "XVS_USDT", "ALPH_USDT", "VID_USDT", "AION_USDT",
    "RLC_USDT", "MFT_USDT", "POLS_USDT", "MDX_USDT", "MASK_USDT",
    "LPT_USDT", "XVG_USDT", "ATA_USDT", "GTC_USDT", "TORN_USDT",
    "ERN_USDT", "KLAY_USDT", "PHA_USDT", "BOND_USDT", "MLN_USDT",
    "DEXE_USDT", "C98_USDT", "CLV_USDT", "QI_USDT", "YGG_USDT",
    "FIO_USDT", "RADI_USDT", "AGLD_USDT", "RAD_USDT", "BETA_USDT",
    "RARE_USDT", "LAZIO_USDT", "ADX_USDT", "AUCTION_USDT", "DAR_USDT",
    "BNX_USDT", "RGT_USDT", "MOVR_USDT", "CITY_USDT", "ENS_USDT",

    # === More DeFi & Yield (600-700) ===
    "ICX_USDT", "MINA_USDT", "RAY_USDT", "FARM_USDT", "ALC_USDT",
    "ASTRAL_USDT", "GMT_USDT", "KDA_USDT", "APE_USDT", "BSW_USDT",
    "MULTI_USDT", "ASTR_USDT", "BSV_USDT", "HFT_USDT", "HOOK_USDT",
    "MAGIC_USDT", "T_USDT", "RNDR_USDT", "HIGH_USDT", "MINA_USDT",
    "ASTU_USDT", "GMX_USDT", "CFX_USDT", "STG_USDT", "RPL_USDT",
    "ACH_USDT", "SSV_USDT", "CKB_USDT", "PERP_USDT", "TRU_USDT",
    "LUA_USDT", "GAL_USDT", "LDO_USDT", "EPX_USDT", "UST_USDT",
    "ASTRA_USDT", "GLM_USDT", "PRO_USDT", "SYN_USDT", "VOXEL_USDT",
    "IB_USDT", "PROS_USDT", "APT_USDT", "OSMO_USDT", "HFT_USDT",
    "PHB_USDT", "HOOK_USDT", "MAGIC_USDT", "GFT_USDT", "MDT_USDT",

    # === Layer 1 & Infrastructure (700-800) ===
    "COMBO_USDT", "MAV_USDT", "PENDLE_USDT", "ARKM_USDT", "WLD_USDT",
    "FDUSD_USDT", "SEI_USDT", "CYBER_USDT", "HIFI_USDT", "ARK_USDT",
    "FRONT_USDT", "GLMR_USDT", "BICO_USDT", "FLUX_USDT", "VGX_USDT",
    "CVX_USDT", "AGIX_USDT", "NTRN_USDT", "ACE_USDT", "NFP_USDT",
    "AI_USDT", "XAI_USDT", "WIF_USDT", "MANTA_USDT", "ONDO_USDT",
    "LSK_USDT", "ALT_USDT", "JUP_USDT", "PYTH_USDT", "RONIN_USDT",
    "DYM_USDT", "OM_USDT", "PIXEL_USDT", "STRK_USDT", "PORTAL_USDT",
    "PDA_USDT", "AXL_USDT", "WLD_USDT", "METIS_USDT", "AEVO_USDT",
    "VANRY_USDT", "BOME_USDT", "ETHFI_USDT", "ENA_USDT", "W_USDT",
    "TNSR_USDT", "SAGA_USDT", "TAO_USDT", "REZ_USDT", "BB_USDT",
]

# ============================================================================
# PRODUCTION MODE - 1000 COIN SYSTEM CONFIGURATION
# ============================================================================

# Volume ve Market Cap Filtreleri (Çok daha sıkı)
MIN_24H_VOLUME = 5_000_000   # Minimum $5M 24h volume (1000 coin için daha yüksek)
MIN_MARKET_CAP = 50_000_000  # Minimum $50M market cap (kalite odaklı)

# Pump Detection İçin Öncelikli Coinler (En yüksek potansiyel)
# Düşük-orta market cap + yüksek volatilite = en iyi pump kandidatları
HIGH_PUMP_POTENTIAL = [
    # === Tier 1: Extreme Pump Potential (Meme + New L1/L2) ===
    "PEPEUSDT", "SHIBUSDT", "FLOKIUSDT", "BONKUSDT", "WIFUSDT",
    "MEMEUSDT", "BOMEUSDT", "ORDIUSDT", "SATSUSDT",
    "ARBUSDT", "OPUSDT", "SUIUSDT", "SEIUSDT", "TIAUSDT",
    "STRKUSDT", "MANTAUSDT", "ZKUSDT", "BEAMXUSDT",

    # === Tier 2: AI Sector (Trending!) ===
    "WLDUSDT", "FETUSDT", "AGIXUSDT", "ARKMUSDT", "RENDERUSDT",
    "TAOLUSDT", "NMRUSDT", "IQUSDT", "OCEANUSDT", "PHBUSDT",

    # === Tier 3: Gaming & Metaverse ===
    "GALAUSDT", "SANDUSDT", "AXSUSDT", "APEUSDT", "GMTUSDT",
    "BLURUSDT", "RONUSDT", "PIXELUSDT", "PORTALUSDT", "XAIUSDT",

    # === Tier 4: DeFi 2.0 ===
    "YFIUSDT", "1INCHUSDT", "SUSHIUSDT", "CRVUSDT",
    "JUPUSDT", "PYTHUSDT", "PENDLEUSDT", "GMXUSDT",

    # === Tier 5: RWA (2025 Mega Trend!) ===
    "ONDOUSDT", "POLYSUSDT",

    # === Tier 6: Low Cap Altcoins (High Risk/Reward) ===
    "JASMYUSDT", "ONEUSDT", "CKBUSDT", "HOTUSDT", "IOTXUSDT",
]

# ============================================================================
# MULTI-INSTANCE COLLECTOR CONFIGURATION (1000 Coin System)
# ============================================================================

# Binance WebSocket Limits: ~100-150 streams per instance
# 500 coins → 5-6 instances needed

BINANCE_COLLECTOR_INSTANCES = [
    {
        "id": 1,
        "symbols": BINANCE_SYMBOLS[0:100],
        "description": "Top 100 Market Cap + High Volume"
    },
    {
        "id": 2,
        "symbols": BINANCE_SYMBOLS[100:200],
        "description": "Meme Coins + Layer 2"
    },
    {
        "id": 3,
        "symbols": BINANCE_SYMBOLS[200:300],
        "description": "AI + Gaming + DeFi"
    },
    {
        "id": 4,
        "symbols": BINANCE_SYMBOLS[300:400],
        "description": "Mid-Cap Altcoins"
    },
    {
        "id": 5,
        "symbols": BINANCE_SYMBOLS[400:],
        "description": "Small Cap + Experimental"
    }
]

# Gate.io: Yüksek limit, tek instance yeterli
GATEIO_COLLECTOR_INSTANCES = [
    {
        "id": 1,
        "symbols": GATEIO_SYMBOLS,
        "description": "All Gate.io Pairs (High Capacity)"
    }
]

# Collector Ayarları
COLLECTOR_CONFIG = {
    "binance": {
        "symbols": BINANCE_SYMBOLS,
        "interval": "1m",
        "max_symbols_per_stream": 100,  # Per instance
        "instances": len(BINANCE_COLLECTOR_INSTANCES),
    },
    "gateio": {
        "symbols": GATEIO_SYMBOLS,
        "interval": "1m",
        "max_symbols_per_stream": 500,  # Gate.io high capacity
        "instances": 1,
    }
}

# Pump Scanner Ayarları (PRODUCTION MODE - High Accuracy!)
PUMP_SCANNER_CONFIG = {
    "scan_interval": 60,         # 60 saniye
    "alert_cooldown": 300,       # 5 dakika
    "min_confidence": 70,        # %70+ confidence (sadece güçlü sinyaller)
    "min_volume_spike": 800,     # %800+ hacim artışı (gerçek pump'lar)
    "min_bars": 50,              # Minimum veri gereksinimi
    "priority_symbols": HIGH_PUMP_POTENTIAL,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_binance_symbols():
    """Tüm Binance sembol listesi"""
    return BINANCE_SYMBOLS

def get_gateio_symbols():
    """Tüm Gate.io sembol listesi"""
    return GATEIO_SYMBOLS

def get_all_symbols():
    """Tüm exchange'ler için semboller"""
    return {
        "binance": BINANCE_SYMBOLS,
        "gateio": GATEIO_SYMBOLS
    }

def get_priority_symbols():
    """Yüksek pump potansiyelli coinler"""
    return HIGH_PUMP_POTENTIAL

def get_binance_instance_config(instance_id):
    """Belirli bir Binance collector instance için config"""
    for instance in BINANCE_COLLECTOR_INSTANCES:
        if instance["id"] == instance_id:
            return instance
    return None

def get_gateio_instance_config(instance_id=1):
    """Gate.io collector instance config"""
    return GATEIO_COLLECTOR_INSTANCES[0]

# ============================================================================
# SYSTEM STATS
# ============================================================================

if __name__ == "__main__":
    print("="*100)
    print("📊 ClaudeCodeCoin - 1000 COIN SYSTEM CONFIGURATION")
    print("="*100)
    print()

    print(f"🔷 Binance Symbols:        {len(BINANCE_SYMBOLS):,} coins")
    print(f"🔶 Gate.io Symbols:        {len(GATEIO_SYMBOLS):,} coins")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 TOTAL COINS:            {len(BINANCE_SYMBOLS) + len(GATEIO_SYMBOLS):,} coins")
    print(f"🔥 High Pump Potential:    {len(HIGH_PUMP_POTENTIAL)} coins")
    print()

    print(f"🖥️  Binance Instances:      {len(BINANCE_COLLECTOR_INSTANCES)} collectors")
    print(f"🖥️  Gate.io Instances:      {len(GATEIO_COLLECTOR_INSTANCES)} collector")
    print()

    print("📋 BINANCE COLLECTOR DISTRIBUTION:")
    for instance in BINANCE_COLLECTOR_INSTANCES:
        print(f"   Instance {instance['id']}: {len(instance['symbols']):3d} coins - {instance['description']}")
    print()

    print("📋 GATE.IO COLLECTOR DISTRIBUTION:")
    for instance in GATEIO_COLLECTOR_INSTANCES:
        print(f"   Instance {instance['id']}: {len(instance['symbols']):3d} coins - {instance['description']}")
    print()

    print("⚙️  PRODUCTION MODE FILTERS:")
    print(f"   Min Confidence:     {PUMP_SCANNER_CONFIG['min_confidence']}%")
    print(f"   Min Volume Spike:   {PUMP_SCANNER_CONFIG['min_volume_spike']}%")
    print(f"   Min 24h Volume:     ${MIN_24H_VOLUME:,}")
    print(f"   Min Market Cap:     ${MIN_MARKET_CAP:,}")
    print()

    print("="*100)
    print("✅ CONFIGURATION LOADED - READY FOR 1000+ COIN PRODUCTION SYSTEM")
    print("="*100)
