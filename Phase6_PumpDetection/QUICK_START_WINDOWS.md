# 🚀 Hybrid Pump Scanner - Windows Hızlı Başlangıç

## ⚡ 5 Dakikada Kurulum

### **Adım 1: Test Database Oluştur**

```powershell
cd Phase1_DataCollection
python create_test_database.py
```

✅ **Beklenen:** BTC, ETH, SOL için 10,000+ bar oluşturuldu

---

### **Adım 2: Pump Verisi Ekle**

```powershell
python add_pump_data.py
```

✅ **Beklenen:** Son 5 bara pump pattern eklendi

---

### **Adım 3: Multi-Timeframe Verilerini Oluştur**

```powershell
python -c "from timeframe_aggregator import TimeframeAggregator; agg = TimeframeAggregator(); agg.process_symbol('BTC_USDT', 'gate.io'); agg.process_symbol('ETH_USDT', 'gate.io'); agg.process_symbol('SOL_USDT', 'gate.io')"
```

✅ **Beklenen:** 8 zaman dilimi (1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d) oluşturuldu

---

### **Adım 4: Test Et**

```powershell
cd ..\Phase6_PumpDetection
python test_scanner.py
```

✅ **Beklenen Çıktı:**
```
✅ SIGNAL GENERATED!
   Symbol: BTC_USDT
   Direction: LONG
   Final Confidence: 79.1%
   Entry: $71,952.51
   Stop Loss: $67,868.47 (-5.68%)
   Take Profit: $84,204.61 (+17.03%)
   R:R Ratio: 1:3.00
```

---

### **Adım 5: Realtime Tarama Başlat**

```powershell
python realtime_hybrid_scanner.py
```

**Durdurma:** `Ctrl+C`

---

## 🔧 Özel Ayarlar

### **Daha Yüksek Kalite (Daha Az Sinyal):**

```powershell
python realtime_hybrid_scanner.py --final-min 80.0
```

### **Daha Hızlı Tarama (60 saniyede bir):**

```powershell
python realtime_hybrid_scanner.py --interval 60
```

### **Sadece Pump Detection (Hybrid Kapalı):**

```powershell
python realtime_hybrid_scanner.py --pump-only
```

---

## 📊 Manuel Test

### **Tek Coin Test:**

```powershell
python -c "import sys; sys.path.insert(0, '.'); from Phase6_PumpDetection.hybrid_pump_scanner import HybridPumpScanner; scanner = HybridPumpScanner(); signal = scanner.scan_symbol('BTC_USDT', 'gate.io'); print(f\"Signal: {signal['final_confidence']:.1f}% | Entry: ${signal['entry_price']:.2f}\") if signal else print('No signal')"
```

---

## ❌ Sorun Giderme

### **Problem:** `ModuleNotFoundError: No module named 'pandas'`

**Çözüm:**
```powershell
pip install -r requirements.txt
```

### **Problem:** `FileNotFoundError: binance_data.db`

**Çözüm:**
```powershell
cd Phase1_DataCollection
python create_test_database.py
```

### **Problem:** `KeyError: 'overall_confidence'`

**Çözüm:** `final_confidence` kullanın (sistem güncellemesi yapıldı)

### **Problem:** PowerShell'de Python kodu çalışmıyor

**Çözüm:** Kodu `.py` dosyasına kaydedin ve `python dosya.py` ile çalıştırın

---

## 📁 Dosya Konumları

```
C:\Users\...\ClaudeCodeCoin\
├── Phase1_DataCollection\
│   ├── data_output\binance_data.db          ← Database
│   └── data_multi_timeframe\*.parquet       ← Multi-TF veriler
│
├── Phase6_PumpDetection\
│   ├── signals\hybrid_*.json                ← Oluşturulan sinyaller
│   ├── test_scanner.py                      ← Test scripti
│   └── realtime_hybrid_scanner.py           ← Realtime scanner
│
└── logs\
    └── realtime_hybrid_scanner.log          ← Log dosyası
```

---

## 🎯 Hızlı Komutlar

```powershell
# Tüm setup'ı çalıştır (Adım 1-3)
cd Phase1_DataCollection
python create_test_database.py && python add_pump_data.py
python -c "from timeframe_aggregator import TimeframeAggregator; agg = TimeframeAggregator(); [agg.process_symbol(s, 'gate.io') for s in ['BTC_USDT', 'ETH_USDT', 'SOL_USDT']]"

# Test et
cd ..\Phase6_PumpDetection
python test_scanner.py

# Realtime başlat
python realtime_hybrid_scanner.py
```

---

## ✅ Başarı Kriterleri

Scanner düzgün çalışıyorsa:

1. ✅ Test scanner çalıştırıldığında sinyal oluşturulmalı
2. ✅ Final confidence 70%+ olmalı
3. ✅ Entry, Stop Loss, Take Profit hesaplanmalı
4. ✅ R:R ratio ~1:3.0 olmalı
5. ✅ Component scores görüntülenmeli

---

## 📞 Yardım

Detaylı dokümantasyon: `HYBRID_SYSTEM_COMPLETE_GUIDE.md`

**Son Güncelleme:** 2025-11-08
