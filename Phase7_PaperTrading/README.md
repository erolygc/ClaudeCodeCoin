# Phase 7 - Paper Trading System 💰

Gerçek piyasa koşullarında sanal bakiye ile işlem yapan otomatik trading sistemi.

## 🎯 Özellikler

### Sanal Trading Parametreleri
- **Başlangıç Bakiyesi:** $10,000 USD
- **Maksimum Açık Pozisyon:** 5 adet eşzamanlı
- **Stop Loss:** %5 (sabit)
- **Take Profit:** %10-20 (confidence'a göre değişken)
  - CRITICAL (85%+): %20 TP
  - HIGH (70-85%): %15 TP
  - MEDIUM (50-70%): %12 TP
  - LOW (30-50%): %10 TP
- **Trailing Stop:** %3 (en yüksek fiyattan)
- **Auto-Close:** 30 dakika sonra otomatik kapatma
- **Trading Fee:** %0.1 (gerçekçi simulasyon)

### Risk Yönetimi
- Pozisyon büyüklüğü confidence'a göre ayarlanır (40-100%)
- Portföyün maksimum %10'u tek işlemde kullanılır
- Minimum işlem büyüklüğü: $50
- Yetersiz bakiye kontrolü

## 🚀 Kullanım

### 1. Paper Trading'i Başlatma

```bash
START_PAPER_TRADING.bat
```

Bu komut:
- Pump scanner'ın alert'lerini takip eder
- 50%+ confidence ve 5x+ hacim spike olan sinyallerde pozisyon açar
- Açık pozisyonları her 30 saniyede kontrol eder
- SL/TP/Timeout koşullarında pozisyon kapatır

### 2. Dashboard'da İzleme

Multi-coin sistemin dashboard'ında (http://localhost:8501) yeni bir **"💰 Paper Trading"** sekmesi eklenmiştir:

**Gösterilen Bilgiler:**
- 💰 Mevcut bakiye ve toplam P&L
- 📊 Win rate ve açık pozisyon sayısı
- 📈 Performans metrikleri (ortalama kazanç/kayıp, süre)
- 📋 İşlem geçmişi tablosu
- 📉 Bakiye grafiği
- 🏆 Sembol bazlı performans
- 🚪 Çıkış sebepleri analizi

## 📂 Dosya Yapısı

```
Phase7_PaperTrading/
├── config.py                  # Trading parametreleri
├── position_manager.py        # Pozisyon yönetimi
├── paper_trading_engine.py    # Ana trading engine
└── performance_tracker.py     # Performans analizi

data_output/
└── paper_trades.db           # İşlem kayıtları (SQLite)

logs/
└── paper_trading.log         # Trading logları
```

## 🔄 Çalışma Mantığı

### 1. Sinyal İşleme
Paper trading engine, pump scanner tarafından üretilen alert'leri okur:
```
pump_alerts/pump_alerts_YYYYMMDD.json
```

### 2. Pozisyon Açma Kriterleri
Bir pozisyon açılması için:
- ✅ Confidence ≥ 50%
- ✅ Volume spike ≥ 5x
- ✅ Sembolde zaten açık pozisyon yok
- ✅ Maksimum pozisyon sayısına ulaşılmamış
- ✅ Yeterli bakiye var

### 3. Pozisyon Yönetimi

**Entry:**
- Güncel fiyattan pozisyon açılır
- Quantity = (Bakiye × 10% × Confidence Multiplier) / Fiyat
- Stop Loss ve Take Profit hesaplanır

**Monitoring:**
- Her 30 saniyede güncel fiyat kontrol edilir
- Trailing stop güncellenir (en yüksek fiyat takip edilir)

**Exit Sebepleri:**
- **TP (Take Profit):** Hedef kar seviyesine ulaşıldı
- **SL (Stop Loss):** Zarar durdur seviyesine ulaşıldı
- **TRAILING_STOP:** En yüksek fiyattan %3 düştü
- **TIMEOUT:** 30 dakika geçti, otomatik kapatma

### 4. P&L Hesaplama

```
Gross P&L = (Exit Price - Entry Price) × Quantity
Fees = Entry Fee + Exit Fee
Net P&L = Gross P&L - Fees

Entry Fee = Entry Price × Quantity × 0.1%
Exit Fee = Exit Price × Quantity × 0.1%
```

## 📊 Performans Metrikleri

### Temel Metrikler
- **Total P&L:** Toplam kar/zarar
- **Win Rate:** Kazanan işlem yüzdesi
- **Avg Win/Loss:** Ortalama kazanç ve kayıp
- **Max Win/Loss:** En büyük kazanç ve kayıp
- **Avg Duration:** Ortalama pozisyon süresi

### Detaylı Analizler
- Sembol bazlı performans
- Confidence seviyesine göre başarı oranı
- Çıkış sebeplerine göre dağılım
- Zaman bazlı bakiye değişimi

## 🎓 Örnek Senaryo

### Sinyal Geldi
```json
{
  "symbol": "PEPE_USDT",
  "confidence": 85.5,
  "volume_spike": 10.2,
  "price": 0.00001234
}
```

### Pozisyon Açıldı
```
Entry Price: $0.00001234
Quantity: 8,100,000 PEPE (confidence: CRITICAL → %100 multiplier)
Position Value: $1,000 (%10 of $10,000 balance)
Stop Loss: $0.00001172 (-5%)
Take Profit: $0.00001481 (+20% for CRITICAL)
```

### Pozisyon Takip Ediliyor
```
5 dakika sonra:
Current Price: $0.00001350
Unrealized P&L: +$94.00 (+9.4%)
Trailing Stop Active: $0.00001309
```

### Pozisyon Kapandı
```
Exit Price: $0.00001450
Exit Reason: TP (Take Profit hit)
Duration: 12 dakika
Gross P&L: $175.00
Fees: $2.00
Net P&L: $173.00 (+17.3%)
```

## ⚠️ Önemli Notlar

1. **Sanal Para:** Bu sistem gerçek para kullanmaz, sadece simulasyondur
2. **Eğitim Amaçlı:** Stratejiyi test etmek ve öğrenmek için kullanın
3. **Gerçek Piyasa Koşulları:** Fiyatlar gerçek borsa verilerine dayanır
4. **Slippage Yok:** Gerçek hayatta fiyat kayması (slippage) olabilir
5. **Likidite Varsayımı:** Tüm işlemlerin gerçekleşeceği varsayılır

## 🔧 İleri Seviye Ayarlar

`Phase7_PaperTrading/config.py` dosyasından ayarları değiştirebilirsiniz:

```python
# Risk parametreleri
INITIAL_BALANCE = 10000.0
MAX_POSITION_SIZE_PERCENT = 10.0
STOP_LOSS_PERCENT = 5.0

# Pozisyon boyutlandırma
POSITION_SIZE_MULTIPLIER = {
    'CRITICAL': 1.0,   # %100
    'HIGH': 0.8,       # %80
    'MEDIUM': 0.6,     # %60
    'LOW': 0.4         # %40
}
```

## 📈 Performans İzleme

### Console Çıktısı
Her 10 iterasyonda durum raporu yazdırılır:
```
📊 PORTFÖY DURUMU
💰 Bakiye: $10,234.50
📈 Toplam P&L: $234.50 (+2.35%)
📊 Açık Pozisyon: 2
✅ Toplam İşlem: 15
🎯 Win Rate: 66.7%
```

### Dashboard Görünümü
Real-time grafik ve tablolarla:
- Bakiye değişim grafiği
- İşlem geçmişi tablosu
- Sembol bazlı performans bar chart
- Exit sebepleri pie chart

## 🐛 Sorun Giderme

### "Paper trading henüz başlatılmamış"
- `START_PAPER_TRADING.bat` dosyasını çalıştırın
- Engine'in çalıştığını kontrol edin

### "Güncel fiyat bulunamadı"
- Multi-coin collector'ların çalıştığından emin olun
- `data_output/binance_data.db` dosyasının güncel veri içerdiğini kontrol edin

### "Yetersiz bakiye"
- Tüm bakiyeniz açık pozisyonlarda olabilir
- Bazı pozisyonların kapanmasını bekleyin veya balance'ı artırın

## 📝 Sonraki Adımlar

1. ✅ Paper trading'i başlatın
2. ✅ Dashboard'dan performansı izleyin
3. ✅ İlk işlemlerin sonuçlarını bekleyin (15-30 dakika)
4. 📊 Günlük/haftalık performans raporları oluşturun
5. 🔧 Parametreleri optimize edin (confidence threshold, TP/SL seviyeleri)
6. 🎯 Başarılı stratejileri dokümante edin

## 🎉 Başarı Hedefleri

- **Kısa Vade (1 gün):** İlk 10 işlemi tamamlayın
- **Orta Vade (1 hafta):** %50+ win rate elde edin
- **Uzun Vade (1 ay):** Pozitif P&L sürdürün

---

**Hazırlayan:** ClaudeCodeCoin Development Team
**Versiyon:** 1.0.0
**Son Güncelleme:** 2025-11-02
