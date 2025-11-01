# 🚀 ClaudeCodeCoin - Sistem Kullanım Rehberi

Tüm sistemi tek komutla başlatın ve yönetin!

## 📋 Hızlı Başlangıç

### 1️⃣ Tüm Sistemi Başlat

```bash
START_ALL_SYSTEMS.bat
```

Bu komut **otomatik olarak**:
- ✅ Binance Collector'ı başlatır
- ✅ Gate.io Collector'ı başlatır
- ✅ Pump Scanner'ı başlatır
- ✅ Dashboard'u açar (http://localhost:8501)

Her bileşen **ayrı bir pencerede** açılır.

### 2️⃣ Sistem Durumunu Kontrol Et

```bash
CHECK_SYSTEM_STATUS.bat
```

Gösterir:
- Hangi bileşenler çalışıyor
- Veritabanı durumu
- Alert ve log dosyaları
- Genel sistem sağlığı

### 3️⃣ Tüm Sistemi Durdur

```bash
STOP_ALL_SYSTEMS.bat
```

Tüm ClaudeCodeCoin bileşenlerini güvenli şekilde durdurur.

---

## 🎯 Sistem Bileşenleri

### 1. Data Collectors (Veri Toplayıcılar)

**Binance Collector**
- Real-time WebSocket bağlantısı
- 1 dakikalık mumlar
- Semboller: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT

**Gate.io Collector**
- Real-time WebSocket bağlantısı
- 1 dakikalık mumlar
- Semboller: BTC_USDT, ETH_USDT, SOL_USDT

**Veri:**
- SQLite veritabanına kaydedilir
- Konum: `data_output/binance_data.db`
- Duplicate kontrolü var

### 2. Pump Scanner (Pump Tespit)

**Özellikler:**
- Her 60 saniyede tüm coinleri tarar
- 4 farklı pump sinyali tespit eder
- Confidence >50% için alert verir
- JSON'a kaydeder: `pump_alerts/`

**Tespit Edilen Sinyaller:**
1. Volume Spike (Hacim Patlaması)
2. Price Surge (Hızlı Fiyat Artışı)
3. Volatility Spike (Volatilite Patlaması)
4. Coordinated Buying (Koordineli Alım)

**Alert Cooldown:** 5 dakika/sembol

### 3. Dashboard (İzleme Paneli)

**URL:** http://localhost:8501

**Sekmeler:**
- 📊 Genel Bakış: Collector durumu, veri istatistikleri
- 📈 Grafikler: Candlestick, RSI, MACD, Bollinger Bands
- 🎯 Stratejiler: RSI, MACD, BB sinyalleri
- 🔥 Pump Signals: Pump detection, tüm coinleri tarama
- 🔧 Sistem: CPU, RAM, Disk, logs

**Özellikler:**
- Otomatik yenileme (10 saniye)
- İnteraktif grafikler
- Real-time pump analizi
- Alert geçmişi

---

## 🎮 Kullanım Senaryoları

### Senaryo 1: İlk Kez Başlatma

```bash
# 1. Tüm sistemi başlat
START_ALL_SYSTEMS.bat

# 2. 5 dakika bekle

# 3. Durumu kontrol et
CHECK_SYSTEM_STATUS.bat

# Çıktı:
# ✅ Binance Collector  : ÇALIŞIYOR
# ✅ Gate.io Collector  : ÇALIŞIYOR
# ✅ Pump Scanner       : ÇALIŞIYOR
# ✅ Dashboard          : ÇALIŞIYOR
```

### Senaryo 2: Veri Durumu Kontrolü

```bash
# Veri istatistiklerini gör
CHECK_DATA_STATUS.bat

# Çıktı:
# BTC_USDT (gate.io): 125 bars
# ETH_USDT (gate.io): 125 bars
# ...
```

### Senaryo 3: Pump Alert İzleme

**Dashboard'da:**
1. http://localhost:8501 aç
2. "🔥 Pump Signals" sekmesine git
3. "Tüm Coinleri Tara" butonuna tıkla
4. Sonuçları gör

**Scanner'da:**
- Scanner penceresini izle
- Alert geldiğinde:
```
🔴🔴 PUMP ALERT: BTC_USDT
   🔥 HACIM SPIKE: 4.5x normal hacim!
   Confidence: 82.5%
```

### Senaryo 4: Sistemi Yeniden Başlatma

```bash
# 1. Sistemi durdur
STOP_ALL_SYSTEMS.bat

# 2. 5 saniye bekle

# 3. Yeniden başlat
START_ALL_SYSTEMS.bat
```

---

## 📊 Pencere Yönetimi

START_ALL_SYSTEMS.bat çalıştırıldığında **4 pencere** açılır:

```
┌─────────────────────────────────────┐
│ Pencere 1: Binance Collector        │
│ └── Sürekli veri akışı gösterir     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Pencere 2: Gate.io Collector        │
│ └── Sürekli veri akışı gösterir     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Pencere 3: Pump Scanner              │
│ └── Her 60 saniyede tarama raporu   │
│ └── Alert'ler burada görünür         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Pencere 4: Dashboard                 │
│ └── Streamlit çıktıları              │
│ └── Browser'da görüntülenecek        │
└─────────────────────────────────────┘
```

**⚠️ ÖNEMLİ:** Pencereleri **kapatmayın**! Minimize edip bırakın.

---

## 🔧 Sorun Giderme

### Sorun 1: "Python bulunamadı" hatası

**Çözüm:**
```bash
# Venv'i manuel aktifleştir
venv\Scripts\activate

# Sonra scripti çalıştır
START_ALL_SYSTEMS.bat
```

### Sorun 2: Dashboard açılmıyor

**Kontrol:**
1. Dashboard penceresi hata veriyor mu?
2. Port 8501 kullanımda mı?

**Çözüm:**
```bash
# Port kontrolü
netstat -ano | findstr :8501

# Farklı port kullan
streamlit run Dashboard\monitoring_dashboard.py --server.port 8502
```

### Sorun 3: Collector'lar veri toplamıyor

**Kontrol:**
```bash
CHECK_DATA_STATUS.bat
```

**Çözüm:**
1. API anahtarları doğru mu? (`.env` dosyasını kontrol et)
2. İnternet bağlantısı var mı?
3. Exchange servisleri çalışıyor mu?

### Sorun 4: Pump Scanner alert vermiyor

**Sebep:** Yetersiz veri

**Çözüm:**
1. En az 50-100 bar veri toplanmasını bekleyin
2. 1-2 saat sonra yeterli veri olacak
3. Normal piyasa koşullarında pump nadirdir

### Sorun 5: Sistem çok yavaş çalışıyor

**Kontrol:**
```bash
CHECK_SYSTEM_STATUS.bat
# CPU/RAM kullanımına bakın
```

**Çözüm:**
1. Dashboard'u kapatın (en fazla kaynak tüketen)
2. Daha az sembol toplayın
3. Pump Scanner aralığını artırın (60 → 120 saniye)

---

## 📁 Dosya Yapısı

```
ClaudeCodeCoin/
│
├── 🚀 Sistem Başlatma/Durdurma
│   ├── START_ALL_SYSTEMS.bat          ← Tüm sistemi başlat
│   ├── STOP_ALL_SYSTEMS.bat           ← Tüm sistemi durdur
│   └── CHECK_SYSTEM_STATUS.bat        ← Durum kontrolü
│
├── 📊 Veri Toplama
│   ├── COLLECT_DATA_QUICK.bat         ← 1 saat veri topla
│   ├── COLLECT_DATA_EXTENDED.bat      ← 6 saat veri topla
│   └── CHECK_DATA_STATUS.bat          ← Veri istatistikleri
│
├── 🔥 Pump Detection
│   ├── TEST_PUMP_DETECTION.bat        ← Pump testi
│   └── START_PUMP_SCANNER.bat         ← Scanner başlat
│
├── 📈 Dashboard
│   └── START_DASHBOARD.bat            ← Dashboard başlat
│
├── 📁 Veri Klasörleri
│   ├── data_output/                   ← SQLite veritabanı
│   ├── pump_alerts/                   ← Pump alert JSON'ları
│   └── logs/                          ← Log dosyaları
│
└── 📚 Dokümantasyon
    └── SISTEM_KULLANIM_REHBERI.md     ← Bu dosya
```

---

## ⏱️ Timeline Beklentileri

### İlk 5 Dakika
```
✅ Sistemler başlatıldı
✅ WebSocket bağlantıları kuruldu
✅ İlk veriler toplandı (~5 bar)
❌ Henüz pump detection çalışmıyor (yetersiz veri)
```

### 30 Dakika Sonra
```
✅ ~30 bar veri toplandı
✅ Temel indikatörler hesaplanabiliyor
🟡 Pump detection kısmen çalışıyor
```

### 1 Saat Sonra
```
✅ ~60 bar veri toplandı
✅ Tüm indikatörler hesaplanabiliyor
✅ Pump detection tam kapasitede çalışıyor
✅ Alert'ler gelmeye başladı
```

### 6 Saat Sonra
```
✅ ~360 bar veri (çok iyi!)
✅ Güvenilir pump detection
✅ Geçmiş pump'ları görebilirsiniz
✅ Backtest yapabilirsiniz
```

---

## 🎯 En İyi Uygulamalar

### 1. Sürekli Çalışma

**Önerilen:**
```bash
# Sabah sistemi başlat
START_ALL_SYSTEMS.bat

# Pencereleri minimize et
# Bilgisayarı açık bırak

# Akşam sonuçlara bak
# Dashboard > Pump Signals
```

### 2. Veri Toplama

**İlk Gün:**
- En az 6 saat çalıştırın
- Yeterli veri toplanmasını bekleyin
- Ardından pump detection düzgün çalışacak

**Sonraki Günler:**
- Sistemi sürekli açık tutun
- Her gün daha fazla veri toplanacak
- Daha iyi pump detection

### 3. Pump Alert İzleme

**Önerilen Ayarlar:**
- Minimum Confidence: 70%
- Scanner Aralığı: 60 saniye
- Alert Cooldown: 5 dakika

**Alert Geldiğinde:**
1. ⚠️ Panik yapmayın
2. 📊 Dashboard'da detayları görün
3. 📈 Grafikleri analiz edin
4. 🧠 Kendi kararınızı verin
5. 💰 Risk yönetimi uygulayın

### 4. Performans

**Düşük Kaynak Modı:**
```bash
# Sadece collector'ları ve scanner'ı çalıştır
# Dashboard'u kapatın

# Manuel başlatma:
start cmd /k "venv\Scripts\activate && python Phase1_DataBackbone\collectors\standalone_binance_collector.py"
start cmd /k "venv\Scripts\activate && python Phase1_DataBackbone\collectors\standalone_gateio_collector.py"
start cmd /k "venv\Scripts\activate && python Phase6_PumpDetection\realtime_pump_scanner.py"
```

---

## 📊 Dashboard Kullanım İpuçları

### Pump Signals Sekmesi

**Tekli Analiz:**
1. Sol panelden sembol seç (BTC_USDT)
2. Exchange seç (gate.io)
3. Otomatik analiz yapılır
4. Confidence slider ile filtrele

**Toplu Tarama:**
1. "Tüm Coinleri Tara" butonuna tıkla
2. Bekle (5-10 saniye)
3. Sonuçları tabloda gör
4. Top 3 pump'ları kartlarda gör

**Alert Geçmişi:**
1. Sayfanın altına kaydır
2. Son 10 alert'i görürsünüz
3. Zaman, sembol, confidence, fiyat değişimi

---

## 🚨 Güvenlik ve Riskler

### API Anahtarları

**Önemli:**
- `.env` dosyasını Git'e commit **ETMEYİN**
- API anahtarlarınızı kimseyle **PAYLAŞMAYIN**
- Sadece **read-only** anahtarlar kullanın
- Trading izni **VERMEYIN**

### Pump Trading Riskleri

**⚠️ UYARILAR:**
- Pump detection **tahmin** yapar, garanti vermez
- High confidence **≠** Kesin kazanç
- Pump'ların %90'ı dump ile biter
- Dump çok daha hızlı gerçekleşir
- Stop-loss **MUTLAKA** kullanın
- Pozisyon boyutunu **KÜÇÜK** tutun

### Sistem Güvenliği

**En İyi Uygulamalar:**
- Güvenlik duvarını açık tutun
- Antivirüs güncel olsun
- Windows güncellemelerini yapın
- Bilinmeyen kaynaklardan script çalıştırmayın

---

## 📞 Yardım ve Destek

### Sık Karşılaşılan Hatalar

**"ModuleNotFoundError"**
→ `pip install -r requirements.txt`

**"Permission Denied"**
→ Yönetici olarak çalıştırın

**"Port already in use"**
→ Başka bir uygulama portu kullanıyor, farklı port deneyin

### Detaylı Dokümantasyon

- Dashboard: `Dashboard/README.md`
- Pump Detection: `Phase6_PumpDetection/README.md`
- Data Collection: `Phase1_DataBackbone/README.md`

---

## 🎓 Özet

### Tek Komutla Başlatma

```bash
START_ALL_SYSTEMS.bat
```

### Durum Kontrolü

```bash
CHECK_SYSTEM_STATUS.bat
```

### Durdurma

```bash
STOP_ALL_SYSTEMS.bat
```

**Hepsi bu kadar!** 🚀

---

**İyi şanslar ve iyi trading'ler!** 📈💰

**Unutmayın:** Bu bir eğitim ve araştırma projesidir. Mali tavsiye değildir. DYOR (Do Your Own Research)!
