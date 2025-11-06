# ClaudeCodeCoin - Hızlı Başlangıç

## 📦 İLK KURULUM (Sadece İlk Kez)

Dashboard için gerekli kütüphaneleri yükleyin:

```bash
pip install streamlit plotly
```

veya tüm gereksinimleri yükleyin:

```bash
pip install -r requirements.txt
```

---

## 🚀 TEK KOMUTLA BAŞLAT

### Windows
```powershell
cd C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin
.\START_SYSTEM.ps1
```

### Linux/Mac
```bash
cd /home/user/ClaudeCodeCoin
./START_SYSTEM.sh
```

Bu script:
- ✅ En son kod güncellemelerini çeker (git pull)
- ✅ Konfigürasyonu kontrol eder
- ✅ Database'i doğrular
- ✅ 4 komponenti otomatik başlatır:
  1. **Data Collector** (Gate.io WebSocket)
  2. **Pump Scanner** (Alert Generation)
  3. **Paper Trading Engine** (Auto-Trading)
  4. **Dashboard** (Web UI - http://localhost:8501)

**Dashboard otomatik açılır!** Sistemler senkronize olup trade açılacak!

**2-3 dakika bekleyin**, sistemler senkronize olacak ve trade açılacak!

---

## 📊 DURUM KONTROLÜ

### Hızlı Kontrol
```powershell
python SYSTEM_HEALTH_CHECK.py
```

### Pozisyon Kontrolü
```powershell
cd Phase7_PaperTrading
python -c "from paper_trading_engine import PaperTradingEngine; e = PaperTradingEngine(); e.print_status()"
```

---

## ⚙️ MANUEL BAŞLATMA (İsterseniz)

### Terminal 1: Data Collector
```powershell
python Phase1_DataBackbone\collectors\multi_coin_gateio_collector_1000coins.py
```

### Terminal 2: Pump Scanner
```powershell
cd Phase6_PumpDetection
python realtime_pump_scanner.py
```

### Terminal 3: Paper Trading
```powershell
cd Phase7_PaperTrading
python paper_trading_engine.py
```

---

## 🎯 BEKLENEN SONUÇLAR

### İlk 5 Dakika
```
Data Collector: ✅ 550 coin'den veri geliyor
Pump Scanner:   ⏳ İlk tarama yapılıyor (60 saniye)
Paper Trading:  ⏳ Alert bekliyor
```

### 5-10 Dakika Sonra
```
Data Collector: ✅ 10,000+ kayıt toplandı
Pump Scanner:   ✅ 2-5 alert oluşturuldu
Paper Trading:  ✅ 1-3 pozisyon açıldı
```

### 1 Saat Sonra
```
Data Collector: ✅ 100,000+ kayıt
Pump Scanner:   ✅ 10-20 alert
Paper Trading:  ✅ 5-10 trade, birkaç açık pozisyon
```

---

## 🔧 SORUN GİDERME

### "No positions opening"

1. Config'i kontrol et:
```powershell
Get-Content Phase7_PaperTrading\config.py | Select-String "MIN_VOLUME_SPIKE"
```

Görmeli: `MIN_VOLUME_SPIKE = 0.0`

Eğer `200.0` görüyorsan:
```powershell
git pull origin claude/dev-project-update-011CUo3BwULJ7Rmb8JqRuqhd
```

2. Paper Trading'i restart et (yukarıdaki Terminal 3 komutu)

### "Database not found"

Collector çalışmıyor. Terminal 1'i başlat.

### "No alerts"

Market sakin veya Pump Scanner çalışmıyor. Terminal 2'yi başlat.

---

## 📈 PERFORMANS İZLEME

### 🎨 Gerçek Zamanlı Dashboard (ÇOK ÖNEMLİ!)

Dashboard otomatik başlatılır veya manuel başlatabilirsiniz:

**Windows:**
```powershell
streamlit run dashboard.py
```

**Linux/Mac:**
```bash
streamlit run dashboard.py
```

**Dashboard Özellikleri:**
- 💰 **Portfolio Özeti**: Bakiye, Win Rate, Açık Pozisyonlar, Ortalama P&L
- 📈 **Candlestick Grafikleri**: Her coin için gerçek zamanlı fiyat ve hacim grafikleri
- 💼 **Pozisyon Takibi**: Tüm açık pozisyonlarınızı canlı görün
- 🚨 **Alert Feed**: Son pump alertlerini anlık takip edin
- 📊 **Analytics**: P&L grafiği, trade istatistikleri, performans metrikleri

**Dashboard'a Erişim:**
- Browser otomatik açılır: `http://localhost:8501`
- Manuel erişim: Tarayıcınızda `http://localhost:8501` adresini açın
- Auto-refresh: Her 30 saniyede otomatik yenilenir

### Log Dosyaları
```powershell
# Collector logs
Get-Content logs\gateio_collector_1000coins.log -Tail 20

# Pump scanner logs
Get-Content logs\pump_scanner.log -Tail 20

# Paper trading logs
Get-Content logs\paper_trading.log -Tail 20
```

---

## 🛑 DURDURMA

Her terminal'de `Ctrl+C` basın.

---

## 📞 DESTEK

Sorun mu var?

1. `python SYSTEM_HEALTH_CHECK.py` çalıştır
2. `python COMPREHENSIVE_SYSTEM_TEST.py` çalıştır
3. Sonuçları benimle paylaş!

---

## ⚡ PRO TİPS

- Collector her zaman çalışmalı (7/24 data toplar)
- Pump Scanner'ı sadece trading saatlerinde çalıştırabilirsiniz
- Paper Trading'i durdurup başlatabilirsiniz, pozisyonlar kaybolmaz

---

**Son Güncelleme**: 2025-11-06
**Version**: 2.0 - Dashboard Added!
