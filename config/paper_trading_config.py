"""
Paper Trading Configuration
$10,000 initial balance, $100 per position
"""

# =============================================================================
# TRADING PARAMETERS
# =============================================================================

# Initial Balance
INITIAL_BALANCE = 10000.0  # $10,000 USD

# Position Sizing
POSITION_SIZE = 100.0  # $100 per position
MAX_OPEN_POSITIONS = 10  # Maximum 10 positions at once (total $1,000 exposure)
MAX_PORTFOLIO_RISK = 0.20  # 20% of total balance

# Risk Management
STOP_LOSS_PERCENT = 0.05  # 5% stop loss
TAKE_PROFIT_PERCENT = 0.15  # 15% take profit (1:3 R:R)
USE_SIGNAL_LEVELS = True  # Use stop loss/take profit from signal

# =============================================================================
# SIGNAL PARAMETERS
# =============================================================================

# Signal Thresholds
MIN_SIGNAL_CONFIDENCE = 70.0  # Minimum 70% confidence to trade
MIN_PUMP_CONFIDENCE = 60.0
MIN_ADVANCED_CONFIDENCE = 65.0

# Signal Source
SIGNAL_DIR = "Phase6_PumpDetection/signals"  # Directory to watch for signals
SIGNAL_CHECK_INTERVAL = 5  # Check for new signals every 5 seconds

# =============================================================================
# GATE.IO FUTURES
# =============================================================================

# Exchange
EXCHANGE = "gate.io"

# Contracts
USE_TOP_VOLUME_ONLY = True  # Only trade top volume contracts
TOP_VOLUME_LIMIT = 50  # Top 50 contracts by volume

# Specific contracts (if not using top volume)
SPECIFIC_CONTRACTS = [
    'BTC_USDT', 'ETH_USDT', 'BNB_USDT', 'SOL_USDT', 'XRP_USDT',
    'ADA_USDT', 'DOGE_USDT', 'MATIC_USDT', 'DOT_USDT', 'AVAX_USDT'
]

# =============================================================================
# DATA COLLECTION
# =============================================================================

# Database
DB_PATH = "Phase1_DataCollection/data_output/binance_data.db"

# Collection Interval
COLLECTION_INTERVAL = 60  # Collect 1m candles every 60 seconds

# Data Retention
MAX_BARS_PER_SYMBOL = 1000  # Keep last 1000 1m bars

# =============================================================================
# HYBRID SCANNER
# =============================================================================

# Scanner Settings
SCAN_INTERVAL = 30  # Scan every 30 seconds
HYBRID_MODE = True  # Use hybrid pump + advanced validation

# Timeframes
TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '1d']

# =============================================================================
# LOGGING
# =============================================================================

# Log Settings
LOG_LEVEL = "INFO"
LOG_DIR = "logs"
LOG_FILE = "paper_trading.log"

# Performance Tracking
TRACK_PERFORMANCE = True
PERFORMANCE_DB = "paper_trading_performance.db"

# =============================================================================
# SAFETY LIMITS
# =============================================================================

# Daily Limits
MAX_DAILY_LOSS = 500.0  # Stop trading if daily loss exceeds $500
MAX_DAILY_TRADES = 50  # Maximum 50 trades per day

# Cooldown
COOLDOWN_AFTER_LOSS = 300  # Wait 5 minutes after a loss
COOLDOWN_AFTER_STOP_OUT = 900  # Wait 15 minutes after stop out

# =============================================================================
# NOTIFICATION (Optional)
# =============================================================================

# Alerts
ENABLE_ALERTS = False
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# Alert Triggers
ALERT_ON_SIGNAL = True
ALERT_ON_TRADE_OPEN = True
ALERT_ON_TRADE_CLOSE = True
ALERT_ON_DAILY_LOSS = True

# =============================================================================
# PAPER TRADING MODE
# =============================================================================

# Execution
PAPER_TRADING_MODE = True  # ALWAYS True for safety
SIMULATE_SLIPPAGE = True
SLIPPAGE_PERCENT = 0.001  # 0.1% slippage

# Fees
MAKER_FEE = 0.0002  # 0.02%
TAKER_FEE = 0.0005  # 0.05%

# =============================================================================
# DISPLAY
# =============================================================================

# Console Output
SHOW_REALTIME_STATS = True
STATS_UPDATE_INTERVAL = 60  # Update stats every 60 seconds

# Dashboard
ENABLE_DASHBOARD = True
DASHBOARD_PORT = 8501
DASHBOARD_AUTO_REFRESH = 10  # Refresh every 10 seconds
