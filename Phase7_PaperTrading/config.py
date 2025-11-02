"""
Paper Trading Configuration
Sanal trading için ayarlar
"""

# Başlangıç bakiyesi
INITIAL_BALANCE = 10000.0  # USD

# Risk Yönetimi
MAX_POSITION_SIZE_PERCENT = 10.0  # Portföyün maksimum %10'u tek işlemde
MIN_POSITION_SIZE = 50.0  # Minimum işlem büyüklüğü (USD)
MAX_OPEN_POSITIONS = 5  # Aynı anda açık olabilecek maksimum pozisyon sayısı

# Stop Loss & Take Profit
STOP_LOSS_PERCENT = 5.0  # %5 zarar durdur
TAKE_PROFIT_PERCENT = {
    'CRITICAL': 20.0,  # 85%+ confidence için %20 kar al
    'HIGH': 15.0,      # 70-85% confidence için %15 kar al
    'MEDIUM': 12.0,    # 50-70% confidence için %12 kar al
    'LOW': 10.0        # 30-50% confidence için %10 kar al
}

# Pozisyon Açma Kriterleri
MIN_CONFIDENCE_TO_TRADE = 50.0  # Minimum %50 confidence gerekli
MIN_VOLUME_SPIKE = 500.0  # Minimum %500 hacim artışı (5x)

# Pozisyon Boyutlandırma (Confidence'a göre)
POSITION_SIZE_MULTIPLIER = {
    'CRITICAL': 1.0,   # 85%+ confidence: Tam pozisyon
    'HIGH': 0.8,       # 70-85%: %80 pozisyon
    'MEDIUM': 0.6,     # 50-70%: %60 pozisyon
    'LOW': 0.4         # 30-50%: %40 pozisyon
}

# Pozisyon Kapatma Kriterleri
AUTO_CLOSE_AFTER_MINUTES = 30  # 30 dakika sonra otomatik kapat
TRAILING_STOP_PERCENT = 3.0  # Trailing stop: En yüksek değerden %3 düşerse kapat

# İşlem Ücretleri (Gerçekçi simulasyon için)
TRADING_FEE_PERCENT = 0.1  # %0.1 işlem ücreti (Binance maker/taker ortalama)

# Database
TRADES_DB = "data_output/paper_trades.db"
PERFORMANCE_LOG = "logs/paper_trading_performance.log"

# Exchange bilgileri (Pump scanner ile uyumlu)
DEFAULT_EXCHANGE = "gate.io"
