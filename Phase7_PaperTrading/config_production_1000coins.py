"""
Paper Trading Configuration - PRODUCTION MODE (1000 Coin System)
Yüksek doğruluk, kaliteli sinyaller için optimize edilmiş
"""

# Başlangıç bakiyesi
INITIAL_BALANCE = 10000.0  # USD

# Risk Yönetimi
MAX_POSITION_SIZE_PERCENT = 8.0   # Portföyün maksimum %8'i tek işlemde (daha konservatif)
MIN_POSITION_SIZE = 50.0          # Minimum işlem büyüklüğü (USD)
MAX_OPEN_POSITIONS = 15           # Aynı anda açık olabilecek maksimum pozisyon sayısı

# Stop Loss & Take Profit
STOP_LOSS_PERCENT = 5.0  # %5 zarar durdur
TAKE_PROFIT_PERCENT = {
    'CRITICAL': 25.0,  # 85%+ confidence için %25 kar al (güçlü sinyaller için daha fazla)
    'HIGH': 20.0,      # 70-85% confidence için %20 kar al
    'MEDIUM': 15.0,    # 50-70% confidence için %15 kar al
    'LOW': 10.0        # 30-50% confidence için %10 kar al
}

# Pozisyon Açma Kriterleri - PRODUCTION MODE (Yüksek Kalite)
MIN_CONFIDENCE_TO_TRADE = 70.0   # Minimum %70 confidence - Sadece güçlü sinyaller
MIN_VOLUME_SPIKE = 800.0         # Minimum %800 hacim artışı - Gerçek pump'lar

# Pozisyon Boyutlandırma (Confidence'a göre)
POSITION_SIZE_MULTIPLIER = {
    'CRITICAL': 1.0,   # 85%+ confidence: Tam pozisyon
    'HIGH': 0.8,       # 70-85%: %80 pozisyon
    'MEDIUM': 0.6,     # 50-70%: %60 pozisyon
    'LOW': 0.4         # 30-50%: %40 pozisyon
}

# Pozisyon Kapatma Kriterleri
AUTO_CLOSE_AFTER_MINUTES = 45    # 45 dakika sonra otomatik kapat (daha uzun süre)
TRAILING_STOP_PERCENT = 3.0      # Trailing stop: En yüksek değerden %3 düşerse kapat

# İşlem Ücretleri (Gerçekçi simulasyon için)
TRADING_FEE_PERCENT = 0.1  # %0.1 işlem ücreti (Binance maker/taker ortalama)

# Database
TRADES_DB = "data_output/paper_trades.db"
PERFORMANCE_LOG = "logs/paper_trading_performance.log"

# Exchange bilgileri (Pump scanner ile uyumlu)
DEFAULT_EXCHANGE = "gate.io"


# ============================================================================
# PRODUCTION AYARLARI AÇIKLAMASI
# ============================================================================
"""
1000 COİN SİSTEMİ İÇİN OPTİMİZE EDİLMİŞ AYARLAR:

1. YÜK SEK DOĞRULUK FİLTRELERİ:
   - Confidence: %70+ (sadece çok güçlü sinyaller)
   - Volume Spike: %800+ (gerçek pump'lar)
   → Daha az sinyal ama çok daha yüksek kazanç oranı

2. RİSK YÖNETİMİ:
   - Max %8 pozisyon (daha konservatif)
   - 15 maksimum pozisyon (1000 coin için yeterli)
   → Portföy çeşitlendirmesi + risk kontrolü

3. KAR HEDEF LERİ:
   - CRITICAL: %25 (güçlü pump'lar için daha fazla kar)
   - AUTO_CLOSE: 45 dakika (trend takibi için daha uzun)
   → Büyük kazançları kaçırmamak

4. BEKLENEN PERFORMANS:
   - Win Rate: %60-70 (yüksek confidence sayesinde)
   - Günlük işlem: 5-15 pozisyon
   - Ortalama kazanç: %8-15 per trade
   - Aylık hedef: %30-50 ROI

NOT: İlk hafta performansı izle ve gerekirse ayarla!
"""
