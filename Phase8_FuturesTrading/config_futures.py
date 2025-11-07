"""
Futures Trading Configuration
Gate.io Vadeli İşlem (Futures) Trading için ayarlar
"""

# ============================================================================
# EXCHANGE API CONFIGURATION
# ============================================================================
EXCHANGE = "gate.io"
API_TYPE = "futures"  # futures (vadeli işlem) modu

# API Credentials (Gate.io Futures)
# IMPORTANT: .env dosyasından yüklenecek, buraya yazmayın!
GATEIO_API_KEY = ""  # .env'den yüklenecek
GATEIO_API_SECRET = ""  # .env'den yüklenecek

# ============================================================================
# ACCOUNT SETTINGS
# ============================================================================
INITIAL_BALANCE = 1000.0  # $1000 başlangıç bakiyesi
MAX_LEVERAGE = 3  # Maksimum 3x kaldıraç
DEFAULT_LEVERAGE = 3  # Varsayılan kaldıraç (tüm işlemler için)

# ============================================================================
# POSITION SETTINGS
# ============================================================================
POSITION_SIZE_USD = 100.0  # Her işlemde sabit $100 kullan
MAX_OPEN_POSITIONS = 10  # Maksimum 10 açık pozisyon (futures için makul)

# Calculated values
MARGIN_PER_POSITION = POSITION_SIZE_USD / MAX_LEVERAGE  # $33.33 margin per position
MAX_TOTAL_MARGIN = INITIAL_BALANCE * 0.8  # Maksimum %80 margin kullanımı ($800)

# ============================================================================
# RISK MANAGEMENT - FUTURES SPECIFIC
# ============================================================================
# Stop Loss & Take Profit
STOP_LOSS_PERCENT = 5.0  # %5 stop loss (3x kaldıraçta = %15 gerçek zarar)
TAKE_PROFIT_PERCENT = {
    'CRITICAL': 20.0,  # 3x kaldıraçta = %60 gerçek kar
    'HIGH': 15.0,      # 3x kaldıraçta = %45 gerçek kar
    'MEDIUM': 12.0,    # 3x kaldıraçta = %36 gerçek kar
    'LOW': 8.0         # 3x kaldıraçta = %24 gerçek kar
}

# Liquidation Protection
LIQUIDATION_BUFFER = 0.02  # %2 buffer from liquidation price
MAX_DRAWDOWN_PERCENT = 30.0  # Maksimum %30 drawdown, sonra dur

# Position Limits
MIN_CONFIDENCE_TO_TRADE = 65.0  # Futures için daha yüksek threshold - WIN RATE %60+ icin
MIN_VOLUME_SPIKE = 100.0  # Volume spike minimum %100 olmali (daha guclu sinyaller)

# ============================================================================
# ORDER EXECUTION
# ============================================================================
ORDER_TYPE = "limit"  # "limit" veya "market"
LIMIT_ORDER_OFFSET_PERCENT = 0.1  # Limit order için %0.1 slippage
SLIPPAGE_TOLERANCE = 0.3  # Maksimum %0.3 slippage toleransı

# Order Timeout
ORDER_TIMEOUT_SECONDS = 10  # 10 saniye içinde dolmazsa iptal et
MAX_RETRIES = 3  # Maksimum 3 deneme

# ============================================================================
# FEES (Gate.io Futures)
# ============================================================================
MAKER_FEE = 0.015  # %0.015 maker fee (futures)
TAKER_FEE = 0.05   # %0.05 taker fee (futures)

# ============================================================================
# TRAILING STOP
# ============================================================================
ENABLE_TRAILING_STOP = True
TRAILING_STOP_ACTIVATION = 5.0  # %5 kar olunca aktif ol
TRAILING_STOP_DISTANCE = 3.0  # Peak'ten %3 düşünce kapat

# ============================================================================
# POSITION MONITORING
# ============================================================================
CHECK_INTERVAL_SECONDS = 5  # Her 5 saniyede pozisyonları kontrol et
AUTO_CLOSE_AFTER_MINUTES = 60  # 60 dakika sonra otomatik kapat

# ============================================================================
# DATABASE & LOGGING
# ============================================================================
TRADES_DB = "data_output/futures_trading.db"
PERFORMANCE_LOG = "logs/futures_trading_performance.log"
POSITION_HISTORY_LOG = "logs/futures_positions_history.json"

# ============================================================================
# SAFETY LIMITS
# ============================================================================
# Emergency Shutdown Conditions
EMERGENCY_STOP_CONDITIONS = {
    'max_loss_per_day': 150.0,  # Günde $150'den fazla kayıp olursa dur
    'max_consecutive_losses': 5,  # Ard arda 5 kayıp olursa dur
    'min_balance': 700.0,  # Bakiye $700'ün altına düşerse dur
}

# Circuit Breaker
ENABLE_CIRCUIT_BREAKER = True
CIRCUIT_BREAKER_COOLDOWN_MINUTES = 30  # 30 dakika cooling period

# ============================================================================
# WEBHOOK & NOTIFICATIONS (Optional)
# ============================================================================
ENABLE_TELEGRAM_NOTIFICATIONS = False
TELEGRAM_BOT_TOKEN = ""  # .env'den yüklenecek
TELEGRAM_CHAT_ID = ""  # .env'den yüklenecek

ENABLE_WEBHOOK = False
WEBHOOK_URL = ""  # Trading view webhook URL

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================
# Hedge Mode (Long + Short aynı anda)
ENABLE_HEDGE_MODE = False  # False = One-way mode (sadece Long)

# Reduce Only Orders
USE_REDUCE_ONLY_FOR_TP_SL = True  # TP/SL için reduce-only kullan

# Post Only (Maker Orders)
PREFER_POST_ONLY = True  # Maker olmayı tercih et (düşük fee)

# ============================================================================
# POSITION SIZE MULTIPLIERS (Signal Quality Based)
# ============================================================================
POSITION_SIZE_MULTIPLIER = {
    'CRITICAL': 1.0,   # Full size ($100)
    'HIGH': 0.8,       # 80% ($80)
    'MEDIUM': 0.6,     # 60% ($60)
    'LOW': 0.5         # 50% ($50)
}

# ============================================================================
# MARKET CONDITIONS
# ============================================================================
# Trading hours (UTC)
TRADING_HOURS = {
    'enabled': False,  # False = 24/7 trading
    'start_hour': 8,   # 08:00 UTC
    'end_hour': 22     # 22:00 UTC
}

# Pause trading during high volatility
PAUSE_ON_HIGH_VOLATILITY = True
HIGH_VOLATILITY_THRESHOLD = 10.0  # %10 BTC price change in 1 hour

# ============================================================================
# VALIDATION
# ============================================================================
def validate_config():
    """Validate configuration settings"""
    errors = []

    # Balance checks
    if INITIAL_BALANCE < 500:
        errors.append("INITIAL_BALANCE too low (min $500 for futures)")

    # Leverage checks
    if MAX_LEVERAGE < 1 or MAX_LEVERAGE > 20:
        errors.append("MAX_LEVERAGE must be between 1-20")

    # Position size checks
    if POSITION_SIZE_USD > INITIAL_BALANCE * 0.2:
        errors.append("POSITION_SIZE_USD too high (max 20% of balance)")

    # Margin checks
    total_margin_required = MARGIN_PER_POSITION * MAX_OPEN_POSITIONS
    if total_margin_required > MAX_TOTAL_MARGIN:
        errors.append(f"Not enough margin: Need ${total_margin_required:.2f}, Have ${MAX_TOTAL_MARGIN:.2f}")

    # Risk checks
    if STOP_LOSS_PERCENT * MAX_LEVERAGE > 50:
        errors.append("Stop loss too wide for leverage (max 50% real loss)")

    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))

    return True

# Validate on import
try:
    validate_config()
    print("[CONFIG] Futures trading configuration validated successfully")
    print(f"[CONFIG] Account: ${INITIAL_BALANCE} | Leverage: {MAX_LEVERAGE}x | Position Size: ${POSITION_SIZE_USD}")
    print(f"[CONFIG] Max Positions: {MAX_OPEN_POSITIONS} | Total Margin: ${MARGIN_PER_POSITION * MAX_OPEN_POSITIONS:.2f}")
except ValueError as e:
    print(f"[ERROR] Configuration validation failed:\n{e}")
    raise
