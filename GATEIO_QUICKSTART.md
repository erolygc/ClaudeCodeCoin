# 🚀 Gate.io Hızlı Başlangıç Kılavuzu

## 📋 İçindekiler
- [Sistem Özeti](#sistem-özeti)
- [Hızlı Başlatma](#hızlı-başlatma)
- [Durum Kontrolü](#durum-kontrolü)
- [Sorun Giderme](#sorun-giderme)

---

## 🎯 Sistem Özeti

Bu sistem **Gate.io**'dan **550 coin** için gerçek zamanlı veri toplar ve pump detection yapar.

### Özellikler:
- ✅ **550 USDT Trading Pairs** (BTC, ETH, SOL, vb.)
- ✅ **1 Dakikalık Candlestick** verisi
- ✅ **SQLite Database** (hafif ve hızlı)
- ✅ **Otomatik Reconnect** (network kesintilerinde)
- ✅ **Real-time Monitoring**

### API Bilgileri:
Gate.io API bilgileriniz `config/secrets.env` dosyasına kaydedildi:
```
GATEIO_API_KEY=5a36b056a39a5b1e6320f0b00be654ca
GATEIO_SECRET_KEY=9225a79f6049bfa96cf25a4ca942f2594808d468ce2ce6d512ab857caf9bde1d
```

---

## 🚀 Hızlı Başlatma

### Windows:
```batch
START_GATEIO_ONLY.bat
```

### Linux/Mac:
```bash
./START_GATEIO_ONLY.sh
```

### Manuel Başlatma:
```bash
python3 Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py
```

---

## 📊 Durum Kontrolü

### Sistem Durumunu Kontrol Et:
```bash
python3 CHECK_GATEIO_STATUS.py
```

Bu komut gösterir:
- ✅ Kaç coin izleniyor
- ✅ Toplam kaç candlestick toplandı
- ✅ Son veri ne zaman geldi
- ✅ Collector aktif mi

### Database'i Manuel Kontrol:
```bash
python3 Phase1_DataBackbone/collectors/view_collected_data.py
```

### Log Dosyalarını Gör:
```bash
# Linux/Mac
tail -f logs/gateio_collector_1000coins.log

# Windows
type logs\gateio_collector_1000coins.log
```

---

## 📁 Dosya Yapısı

```
ClaudeCodeCoin/
├── START_GATEIO_ONLY.bat        # Windows başlatma scripti
├── START_GATEIO_ONLY.sh         # Linux/Mac başlatma scripti
├── CHECK_GATEIO_STATUS.py       # Durum kontrol scripti
├── config/
│   └── secrets.env              # Gate.io API bilgileri (GİTİGNORE'da!)
├── data_output/
│   └── binance_data.db          # SQLite database
├── logs/
│   └── gateio_collector_1000coins.log
└── Phase1_DataBackbone/
    └── collectors/
        └── multi_coin_gateio_collector_1000coins.py
```

---

## ⚙️ Gelişmiş Kullanım

### 1. Pump Detection Scanner Başlat:
Veri toplandıktan sonra (en az 50 candlestick), pump detection'ı başlatın:

```bash
# Windows
START_PUMP_SCANNER.bat

# Linux/Mac
python3 Phase6_PumpDetection/realtime_pump_scanner.py
```

### 2. Paper Trading Başlat:
Pump sinyalleri tespit edildiğinde, otomatik paper trading:

```bash
# Windows
START_PAPER_TRADING.bat

# Linux/Mac
python3 Phase7_PaperTrading/paper_trading_engine.py
```

### 3. Tüm Sistemi Başlat (Sırayla):
```bash
# Terminal 1: Gate.io Collector
START_GATEIO_ONLY.bat

# Terminal 2: Pump Scanner (5 dakika sonra)
START_PUMP_SCANNER.bat

# Terminal 3: Paper Trading (10 dakika sonra)
START_PAPER_TRADING.bat
```

---

## 🔧 Sorun Giderme

### ❌ Problem: "WebSocket connection error: HTTP 403"
**Çözüm:**
- Gate.io API key'lerinizi kontrol edin
- IP whitelist ekleyin (Gate.io dashboard'da)
- VPN/Proxy kullanıyorsanız kapatın

### ❌ Problem: "Database boş"
**Çözüm:**
- Collector'ın çalıştığından emin olun
- 2-3 dakika bekleyin (ilk veriler gelene kadar)
- Log dosyasını kontrol edin: `logs/gateio_collector_1000coins.log`

### ❌ Problem: "No module named 'websockets'"
**Çözüm:**
```bash
pip install websockets
```

### ❌ Problem: Collector durdu
**Çözüm:**
- Collector'ı yeniden başlatın
- Otomatik reconnect sistemi var, 10 saniye bekleyip tekrar dener
- Network bağlantınızı kontrol edin

---

## 📈 Beklenen Sonuçlar

### İlk 5 Dakika:
- ✅ 550 coin için WebSocket bağlantısı
- ✅ Dakikada ~550 candlestick (her coin için 1)
- ✅ Database'de ~2,750 kayıt (5 dakika × 550 coin)

### 1 Saat Sonra:
- ✅ ~33,000 candlestick (550 coin × 60 dakika)
- ✅ Pump detection sinyalleri başlayabilir
- ✅ Paper trading için yeterli veri

### 24 Saat Sonra:
- ✅ ~792,000 candlestick
- ✅ Detaylı pump analizi mümkün
- ✅ Backtest için zengin veri seti

---

## 🎯 Önerilen Workflow

1. **Başlatma** (5 dk):
   ```bash
   START_GATEIO_ONLY.bat
   ```

2. **Durum Kontrolü** (Her saat):
   ```bash
   python3 CHECK_GATEIO_STATUS.py
   ```

3. **Pump Scanner** (Veri toplandıktan sonra):
   ```bash
   START_PUMP_SCANNER.bat
   ```

4. **Paper Trading** (Sinyaller başladıktan sonra):
   ```bash
   START_PAPER_TRADING.bat
   ```

---

## 📞 Destek

**GitHub Issues:** [ClaudeCodeCoin/issues](https://github.com/erolygc/ClaudeCodeCoin/issues)

**Log Dosyaları:**
- Gate.io Collector: `logs/gateio_collector_1000coins.log`
- Pump Scanner: `logs/pump_scanner.log`
- Paper Trading: `logs/paper_trading.log`

---

## ⚠️ Önemli Notlar

1. **Secrets Dosyası:** `config/secrets.env` dosyası `.gitignore`'da - asla commit edilmez!
2. **Database:** SQLite kullanıldığı için ayrı database server'a gerek yok
3. **Network:** Stabil internet bağlantısı gerekli (WebSocket için)
4. **Sistem Kaynakları:** Minimum 2GB RAM, 1GB disk alanı

---

## 🔄 Güncelleme

GitHub'dan en son güncellemeleri almak için:

```bash
# Linux/Mac
./git_update.sh

# Windows
GIT_UPDATE.bat
```

---

**Son Güncelleme:** 2025-11-04
**Versiyon:** 1.0 - Gate.io Only System
