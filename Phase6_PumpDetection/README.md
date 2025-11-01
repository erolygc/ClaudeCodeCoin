# Phase 6: Pump & Dump Detection

Gelişmiş pump ve dump tespit sistemi. Gerçek zamanlı anomali algılama ile yüksek doğruluklu pump sinyalleri.

## 🎯 Özellikler

### Tespit Edilen Sinyaller

1. **Volume Spike (Hacim Patlaması)**
   - Normal hacmin 3-10x üzeri
   - Aniden artan alım/satım aktivitesi
   - RSI ve fiyat değişimi ile kombine analiz

2. **Price Surge (Hızlı Fiyat Artışı)**
   - 5 dakikada %10+ artış
   - 15 dakikada %20+ ekstrem artış
   - Momentum indikatörleri ile doğrulama

3. **Volatility Spike (Volatilite Patlaması)**
   - ATR'nin 2.5x+ artması
   - Fiyat dalgalanmalarının anormal artışı
   - Hacim ile birlikte değerlendirme

4. **Coordinated Buying (Koordineli Alım)**
   - Ardışık 4-5 yeşil (yükseliş) barı
   - Hacim artışı ile birlikte
   - Toplam %5+ fiyat artışı

### Confidence Seviyeleri

| Seviye | Aralık | Emoji | Açıklama |
|--------|--------|-------|----------|
| **CRITICAL** | 85%+ | 🔴🔴🔴 | Çok yüksek pump olasılığı |
| **HIGH** | 70-85% | 🔴🔴 | Yüksek pump olasılığı |
| **MEDIUM** | 50-70% | 🟡 | Orta pump olasılığı |
| **LOW** | 30-50% | 🟢 | Düşük pump olasılığı |

## 📁 Dosya Yapısı

```
Phase6_PumpDetection/
├── pump_detection_engine.py      # Ana tespit motoru
├── realtime_pump_scanner.py      # Sürekli tarama sistemi
└── README.md                      # Bu dosya
```

## 🚀 Kullanım

### 1. Tek Sembol Analizi

```python
from Phase6_PumpDetection.pump_detection_engine import PumpDetectionEngine

# Engine oluştur
engine = PumpDetectionEngine()

# BTC_USDT'yi analiz et
signals = engine.analyze_symbol("BTC_USDT", "gate.io")

# Sinyalleri göster
for signal in signals:
    print(f"{signal.message}")
    print(f"Confidence: {signal.confidence:.1f}%")
```

### 2. Tüm Sembolleri Tara

```python
# Tüm sembolleri tara
results = engine.scan_all_symbols(exchange="gate.io")

# Sonuçları göster
for symbol, signals in results.items():
    print(f"{symbol}: {len(signals)} sinyal")
```

### 3. Real-Time Scanner

```bash
# Scanner'ı başlat
.\START_PUMP_SCANNER.bat
```

Scanner:
- Her 60 saniyede tüm sembolleri tarar
- Confidence >50% olan sinyaller için alert oluşturur
- Alerts `pump_alerts/` klasörüne JSON olarak kaydedilir
- Aynı coin için 5 dakika cooldown vardır

### 4. Dashboard Entegrasyonu

Dashboard'da "🔥 Pump Signals" sekmesini kullanın:

```bash
# Dashboard'u başlat
.\START_DASHBOARD.bat
```

Dashboard özellikleri:
- Seçili sembol için pump analizi
- Tüm coinleri tarama butonu
- Top pump coins listesi
- Alert geçmişi görüntüleme
- Confidence slider ile filtreleme

## 🔧 Parametreler

### Tespit Eşikleri

`pump_detection_engine.py` içindeki parametreleri değiştirebilirsiniz:

```python
self.params = {
    # Hacim Spike Parametreleri
    'volume_spike_threshold': 3.0,      # 3x normal hacim
    'extreme_volume_threshold': 5.0,    # 5x ekstrem hacim

    # Fiyat Değişim Parametreleri
    'price_surge_threshold': 10.0,      # %10 artış
    'extreme_price_threshold': 20.0,    # %20 ekstrem artış

    # Volatilite Parametreleri
    'volatility_spike_threshold': 2.5,  # 2.5x normal volatilite

    # Zaman Pencereleri (dakika)
    'short_window': 5,    # Kısa vadeli
    'medium_window': 15,  # Orta vadeli
    'long_window': 60,    # Uzun vadeli
}
```

### Scanner Ayarları

`realtime_pump_scanner.py` içinde:

```python
self.scan_interval = 60          # Tarama aralığı (saniye)
self.alert_cooldown = 300        # Alert cooldown (saniye)
```

## 📊 Sinyal Yapısı

Her pump sinyali şu bilgileri içerir:

```python
{
    'symbol': 'BTC_USDT',
    'exchange': 'gate.io',
    'timestamp': '2024-01-01T12:00:00',
    'signal_type': 'volume_spike',
    'level': 'high',
    'confidence': 75.5,
    'price_change_pct': 12.5,
    'volume_change_pct': 450.0,
    'time_window_minutes': 5,
    'current_price': 45000.0,
    'current_volume': 1500000.0,
    'indicators': {
        'volume_ratio': 4.5,
        'rsi': 78.0,
        'atr_pct': 3.2
    },
    'message': '🔥 HACIM SPIKE: 4.5x normal hacim!'
}
```

## 🎓 Test

### Manuel Test

```bash
.\TEST_PUMP_DETECTION.bat
```

### Python Test

```bash
python Phase6_PumpDetection/pump_detection_engine.py
```

## 📈 Dashboard Kullanımı

1. **Tekli Analiz**:
   - Sol panelden sembol seçin
   - "🔥 Pump Signals" sekmesine geçin
   - Otomatik olarak analiz yapılır

2. **Toplu Tarama**:
   - "Tüm Coinleri Tara" butonuna tıklayın
   - Tüm semboller taranır
   - Sonuçlar tabloda gösterilir
   - En yüksek 3 confidence kartlarda gösterilir

3. **Alert Geçmişi**:
   - Alt kısımda alert geçmişi görüntülenir
   - Son 10 alert gösterilir
   - JSON dosyasından okunur

## ⚠️ Önemli Notlar

### Risk Uyarıları

- ⚠️ Bu sistem **tahmin** yapar, %100 doğruluk garantisi **yoktur**
- ⚠️ High confidence bile kesin alım sinyali **değildir**
- ⚠️ Pump'ların çoğu **dump** ile sonuçlanır
- ⚠️ Dump fazı genellikle pump'tan **çok daha hızlıdır**
- ⚠️ Her zaman **risk yönetimi** kurallarını uygulayın

### En İyi Uygulamalar

1. **Çoklu Sinyal Bekleyin**: Birden fazla sinyal türü bir araya geldiğinde confidence artar

2. **Hacim Kontrolü**: Hacim artışı olmadan sadece fiyat artışı şüphelidir

3. **Time Window**: Çok kısa sürede (%1-2 dakika) olan pump'lar genellikle bot aktivitesidir

4. **Exchange Kontrolü**: Düşük hacimli exchange'lerde pump daha kolay organize edilir

5. **Market Cap**: Düşük market cap'li coinlerde pump daha sık görülür

6. **Zaman Analizi**: Gece saatlerinde (düşük likidite) pump riski artar

## 🔬 Algoritma Detayları

### Volume Spike Detection

```
1. 20 periyotluk hacim ortalaması hesapla (MA20)
2. Güncel hacim / MA20 oranını hesapla
3. Oran >= 3.0 ise sinyal üret
4. Confidence = 30 + (ratio - 3) * 10
5. Fiyat artışı varsa confidence += 15
```

### Price Surge Detection

```
1. 5 ve 15 dakikalık fiyat değişimini hesapla
2. Değişim >= %10 ise sinyal üret
3. Confidence = 40 + (change - 10) * 2
4. Hacim ratio > 2 ise confidence += 15
5. RSI > 70 ise confidence += 10
```

### Coordinated Buying Detection

```
1. Son 5 bar'ı kontrol et
2. En az 4 tanesi yeşil (close > open) mi?
3. Toplam fiyat artışı >= %5 mi?
4. Ortalama hacim ratio >= 1.5 mi?
5. Tüm şartlar sağlanırsa sinyal üret
```

### Signal Combination

```
1. Aynı timestamp'teki sinyalleri grupla
2. 2+ sinyal varsa confidence artır
3. Combined confidence = max + (count - 1) * 10
4. En yüksek seviyeyi al
5. Kombine sinyal oluştur
```

## 📚 Referanslar

### Teknik İndikatörler

- **RSI**: Relative Strength Index (14 periyot)
- **ATR**: Average True Range (14 periyot)
- **Volume MA**: 20 periyotluk hacim ortalaması
- **Price ROC**: Rate of Change (5, 15 periyot)

### Anomali Tespiti

- Z-Score analizi
- Percentile thresholds
- Moving average deviations
- Pattern matching

## 🛠️ Geliştirme

### Yeni Sinyal Tipi Ekleme

```python
def _detect_my_signal(self, df: pd.DataFrame, symbol: str,
                     exchange: str) -> List[PumpSignal]:
    """Özel sinyal tespiti"""
    signals = []

    # Analiz yap
    # ...

    if condition_met:
        signal = PumpSignal(
            symbol=symbol,
            exchange=exchange,
            # ... diğer parametreler
        )
        signals.append(signal)

    return signals
```

### Parametreleri Optimize Etme

1. Backtesting ile geçmiş verileri test edin
2. False positive oranını ölçün
3. True positive oranını ölçün
4. Threshold'ları ayarlayın
5. Yeniden test edin

## 📞 Destek

Sorular için:
- Dashboard'daki "ℹ️ Pump Detection Nasıl Çalışır?" bölümünü okuyun
- `pump_detection_engine.py` kodunu inceleyin
- Test scriptlerini çalıştırın

## 📄 Lisans

ClaudeCodeCoin projesi kapsamında
