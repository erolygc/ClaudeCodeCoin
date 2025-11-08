# 🚀 ClaudeCodeCoin - Sistem Başlatma Rehberi

## 📋 İçindekiler
1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [Sistemi Sıfırdan Başlatma](#sistemi-sıfırdan-başlatma)
3. [Manuel Başlatma](#manuel-başlatma)
4. [Sorun Giderme](#sorun-giderme)
5. [Sistem Ayarları](#sistem-ayarları)

---

## 🎯 Hızlı Başlangıç

### Seçenek 1: Tek Tıkla Başlat (Önerilen)
```
START_AUTO_TRADING_SIMPLE.bat
```
Bu script:
- ✅ Dashboard'u otomatik başlatır (http://localhost:8501)
- ✅ Trading engine'i başlatır
- ✅ Top 50 coin ile çalışır

### Seçenek 2: Sadece Trading Engine
```
START_AUTO_TRADING.bat
```

---

## 🔄 Sistemi Sıfırdan Başlatma

### Adım 1: Mevcut Sistemi Durdur
```
CTRL + C (trading engine penceresinde)
```
veya tüm pencereleri kapatın

### Adım 2: Sistemi Sıfırla
```
RESET_SYSTEM.bat
```
Bu şunları yapar:
- 🗑️ Tüm trading geçmişini siler
- 🗑️ Pozisyonları temizler
- 🗑️ Log dosyalarını siler
- 🗑️ Pump alert'leri siler
- ♻️ Bakiyeyi $10,000'a sıfırlar

### Adım 3: Sistemi Yeniden Başlat
```
START_AUTO_TRADING_SIMPLE.bat
```

---

## 🔧 Manuel Başlatma

### 1️⃣ Virtual Environment Aktif Et
```powershell
cd C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin
.\venv\Scripts\Activate.ps1
```

### 2️⃣ Dashboard Başlat (Opsiyonel - Ayrı Pencere)
```powershell
streamlit run dashboard.py
```
📊 Dashboard: http://localhost:8501

### 3️⃣ Trading Sistemini Başlat
```powershell
# Top 50 coin ile
python start_trading_system_windows.py --top 50

# Belirli coinler ile
python start_trading_system_windows.py --coins BTC_USDT,ETH_USDT,SOL_USDT

# Top 20 coin ile
python start_trading_system_windows.py --top 20
```

---

## 🎮 Sistem Bileşenleri

### Çalışan Servisler:
1. **Hybrid Scanner** (PID gösterilir)
   - Pump sinyalleri üretir
   - Her 30 saniyede kontrol eder
   - Sinyaller: `pump_alerts/pump_alerts_YYYYMMDD.json`

2. **Paper Trading Engine** (PID gösterilir)
   - Sinyalleri işler
   - Otomatik pozisyon açar/kapatır
   - Database: `Phase7_PaperTrading/data_output/paper_trading.db`

3. **Dashboard** (Port 8501)
   - Gerçek zamanlı görselleştirme
   - Pozisyon takibi
   - Performance metrikleri

---

## ⚙️ Sistem Ayarları

### Trading Parametreleri
Dosya: `Phase7_PaperTrading/config.py`

```python
# Başlangıç Sermayesi
INITIAL_BALANCE = 10000.0  # USD

# Risk Yönetimi
MAX_POSITION_SIZE_PERCENT = 10.0  # %10 max pozisyon
MAX_OPEN_POSITIONS = 15  # Maksimum 15 açık pozisyon

# Stop Loss & Take Profit
STOP_LOSS_PERCENT = 5.0  # %5 zarar durdur
TAKE_PROFIT_PERCENT = {
    'CRITICAL': 25.0,  # 85%+ confidence → %25 kar
    'HIGH': 20.0,      # 70-85% → %20 kar
    'MEDIUM': 15.0,    # 50-70% → %15 kar
    'LOW': 10.0        # 30-50% → %10 kar
}

# Sinyal Filtreleri
MIN_CONFIDENCE_TO_TRADE = 50.0  # Minimum %50 confidence
MIN_VOLUME_SPIKE = 0.0  # TEST MODE: Volume şartı yok

# Otomatik Kapatma
AUTO_CLOSE_AFTER_MINUTES = 45  # 45 dakika sonra kapat
TRAILING_STOP_PERCENT = 3.0  # %3 trailing stop
```

### Ayarları Değiştirme:
1. `Phase7_PaperTrading/config.py` dosyasını düzenleyin
2. Sistemi yeniden başlatın
3. Değişiklikler otomatik yüklenir

---

## 🎨 Dashboard Kullanımı

### Sekmeler:

#### 📈 Chart
- Gerçek zamanlı candlestick grafiği
- Volume gösterimi
- Symbol seçimi (sidebar)

#### 💼 Positions
- Açık pozisyonlar listesi
- Gerçek zamanlı P&L
- Stop Loss & Take Profit seviyeleri

#### 🚨 Alerts
- Son pump sinyalleri
- Confidence ve volume bilgisi
- Tarih/saat damgası

#### 📊 Analytics
- Equity curve
- Win rate
- Ortalama kazanç/kayıp
- Trade istatistikleri

---

## 🔍 Sorun Giderme

### Problem: Dashboard açılmıyor
**Çözüm:**
```powershell
# Port'u kontrol et
netstat -ano | findstr :8501

# Eğer kullanımdaysa, process'i öldür
taskkill /F /PID <PID_NUMBER>

# Dashboard'u yeniden başlat
streamlit run dashboard.py
```

### Problem: Trading Engine hata veriyor
**Çözüm:**
```powershell
# Logları kontrol et
cat logs/paper_trading.log

# Sistemi sıfırla
RESET_SYSTEM.bat

# Yeniden başlat
START_AUTO_TRADING_SIMPLE.bat
```

### Problem: Hiç sinyal gelmiyor
**Sebep:** Bu normal olabilir! Pump sinyalleri belirli koşullar gerektirir.

**Kontrol:**
1. Scanner çalışıyor mu? → Log'lara bakın
2. Database'de veri var mı? → `data_output/binance_data.db`
3. Alerts klasörü var mı? → `pump_alerts/`

**Test için ayarları gevşetme:**
```python
# Phase7_PaperTrading/config.py
MIN_CONFIDENCE_TO_TRADE = 30.0  # %30'a düşür
```

### Problem: Pozisyon açılmıyor
**Sebep:** Fiyat verisi eksik olabilir

**Çözüm:**
```powershell
# Data collector çalışıyor mu kontrol et
python CHECK_COLLECTORS.py
```

---

## 📊 Sistem Durumunu Kontrol

### Hızlı Kontrol Script'leri:
```powershell
# Genel sistem durumu
python SYSTEM_STATUS_CHECK.py

# Collector durumu
python CHECK_COLLECTORS.py

# Pump alerts kontrol
python CHECK_PUMP_ALERTS.py

# Paper trading durumu
python CHECK_PAPER_TRADING_STATUS.py
```

---

## 📁 Önemli Dosya Konumları

```
ClaudeCodeCoin/
│
├── START_AUTO_TRADING_SIMPLE.bat  # Ana başlatıcı
├── RESET_SYSTEM.bat               # Sistemi sıfırla
├── dashboard.py                   # Dashboard
│
├── Phase6_PumpDetection/
│   ├── realtime_hybrid_scanner.py # Pump scanner
│   └── signals/                   # Signal dosyaları
│
├── Phase7_PaperTrading/
│   ├── paper_trading_engine.py    # Trading engine
│   ├── config.py                  # Ayarlar
│   └── data_output/
│       └── paper_trading.db       # Trading database
│
├── pump_alerts/
│   └── pump_alerts_YYYYMMDD.json  # Günlük alertler
│
└── logs/
    ├── paper_trading.log          # Trading logları
    └── hybrid_scanner.log         # Scanner logları
```

---

## 🎯 İlk Çalıştırma Checklist

- [ ] Virtual environment aktif
- [ ] `RESET_SYSTEM.bat` ile temiz başlangıç
- [ ] `START_AUTO_TRADING_SIMPLE.bat` ile sistem başlatıldı
- [ ] Dashboard açıldı (http://localhost:8501)
- [ ] Trading engine logları akıyor
- [ ] Scanner çalışıyor (PID gösterildi)
- [ ] İlk sinyal bekleniyor (5-30 dakika)

---

## 📞 Yardım

### Log Dosyalarını İnceleme:
```powershell
# Trading engine logs
Get-Content logs\paper_trading.log -Tail 50

# Scanner logs
Get-Content logs\hybrid_scanner.log -Tail 50

# Gerçek zamanlı log takibi
Get-Content logs\paper_trading.log -Wait -Tail 20
```

### Sistemi Tamamen Durdurma:
1. Trading engine penceresinde `CTRL + C`
2. Dashboard penceresini kapat
3. Veya tüm pencereleri kapat

---

## 🚀 Hızlı Komutlar Özeti

```powershell
# Sistemi başlat
START_AUTO_TRADING_SIMPLE.bat

# Sistemi sıfırla
RESET_SYSTEM.bat

# Sadece dashboard
streamlit run dashboard.py

# Manuel trading engine
python start_trading_system_windows.py --top 50

# Ayarları düzenle
notepad Phase7_PaperTrading\config.py

# Logları görüntüle
Get-Content logs\paper_trading.log -Tail 50
```

---

## 💡 İpuçları

1. **İlk Sinyal için Sabırlı Olun**: Pump sinyalleri gelmesi 5-60 dakika sürebilir
2. **Volatil Saatlerde Test Edin**: Crypto piyasaları en aktif UTC 12:00-20:00 arası
3. **Ayarlarla Oynayın**: `config.py` dosyasındaki parametreleri değiştirerek optimize edin
4. **Logları Takip Edin**: Her şey loglarda! Sorun olunca önce logları kontrol edin
5. **Dashboard'u Kullanın**: Görsel takip her zaman daha kolay

---

**Başarılar! 🚀 Sorularınız için lütfen GitHub Issues'ı kullanın.**
