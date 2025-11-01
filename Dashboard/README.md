# 📊 ClaudeCodeCoin - Live Monitoring Dashboard

Gerçek zamanlı sistem izleme ve analiz paneli

## Özellikler

### 📊 Genel Bakış
- **Collector Durumu**: Binance ve Gate.io collector'larının çalışıp çalışmadığını anlık izleme
- **Veri İstatistikleri**: Her sembol ve exchange için toplanan bar sayıları
- **Durum Göstergeleri**:
  - 🟢 Mükemmel (100+ bar)
  - 🟡 İyi (50-100 bar)
  - 🔴 Yetersiz (<50 bar)

### 📈 Canlı Grafikler
- **Candlestick Chart**: Gerçek zamanlı fiyat hareketleri
- **Bollinger Bands**: Volatilite bantları
- **RSI (14)**: Momentum göstergesi (30/70 seviyeleri ile)
- **MACD**: Trend takibi (Histogram ile)
- **İnteraktif Zoom**: Grafikleri yakınlaştırıp uzaklaştırma

### 🎯 Strateji Sinyalleri
- **RSI Stratejisi**:
  - 🟢 AL: RSI < 30 (Aşırı Satım)
  - 🔴 SAT: RSI > 70 (Aşırı Alım)
  - ⚪ NÖTR: 30-70 arası

- **MACD Stratejisi**:
  - 🟢 YÜKSELIŞ: MACD > Signal
  - 🔴 DÜŞÜŞ: MACD < Signal

- **Bollinger Bands Stratejisi**:
  - 🟢 AL: Fiyat alt banda değdi
  - 🔴 SAT: Fiyat üst banda değdi
  - ⚪ NÖTR: Bantlar içinde

### 🔧 Sistem İzleme
- **CPU Kullanımı**: Anlık işlemci yükü
- **RAM Kullanımı**: Bellek durumu
- **Disk Kullanımı**: Depolama alanı
- **Veritabanı Boyutu**: SQLite database boyutu
- **Log İzleme**: Collector loglarını canlı görüntüleme

## Kurulum

### 1. Gerekli Paketleri Yükle

```bash
pip install streamlit plotly psutil
```

veya tüm gereksinimleri yükle:

```bash
pip install -r requirements.txt
```

### 2. Dashboard'u Başlat

```bash
.\START_DASHBOARD.bat
```

veya manuel olarak:

```bash
streamlit run Dashboard/monitoring_dashboard.py
```

## Kullanım

### Başlatma

Dashboard başlatıldığında otomatik olarak browser'ınızda açılacaktır:
```
http://localhost:8501
```

### Ayarlar (Sol Panel)

- **Otomatik Yenileme**: Açık/Kapalı
- **Yenileme Süresi**: 5-60 saniye arası
- **Sembol Seçimi**: BTC_USDT, ETH_USDT, vb.
- **Exchange Seçimi**: Binance veya Gate.io
- **Veri Aralığı**: 50-500 bar arası

### Sekmeler

#### 📊 Genel Bakış
- Collector durumları
- Toplanan veri istatistikleri
- Sembol bazında detaylar
- İlk/Son veri zamanları

#### 📈 Grafikler
- Interaktif candlestick chart
- Teknik indikatörler
- Zoom ve pan özellikleri
- Son değerlerin özeti

#### 🎯 Stratejiler
- Anlık alım/satım sinyalleri
- RSI, MACD, Bollinger Bands stratejileri
- Trend analizi

#### 🔧 Sistem
- Sistem kaynak kullanımı
- Veritabanı bilgileri
- Log dosyalarını görüntüleme

## İpuçları

### Veri Toplama İzleme

1. Dashboard'u açın
2. "Genel Bakış" sekmesinde collector durumlarını kontrol edin
3. Eğer collector'lar duruyorsa, başlatın:
   ```bash
   .\COLLECT_DATA_QUICK.bat
   ```
4. Dashboard otomatik olarak yenilenecek ve bar sayıları artacak

### Grafik Analizi

1. "Grafikler" sekmesine geçin
2. Sembol ve exchange seçin
3. Grafikte zoom yapmak için:
   - Fare ile sürükleyin
   - Çift tıklayarak sıfırlayın
4. İndikatör çizgilerini görmek için legend'a tıklayın

### Strateji Takibi

1. "Stratejiler" sekmesine geçin
2. Her strateji için anlık sinyalleri görün
3. Yeşil = Al, Kırmızı = Sat, Beyaz = Nötr
4. En az 50 bar veri gereklidir

### Sistem Sağlığı

1. "Sistem" sekmesine geçin
2. CPU/RAM/Disk kullanımını izleyin
3. Veritabanı boyutunu kontrol edin
4. Log dosyalarını inceleyin

## Sorun Giderme

### Dashboard Açılmıyor

```bash
# Portun kullanımda olup olmadığını kontrol edin
netstat -ano | findstr :8501

# Farklı port kullanın
streamlit run Dashboard/monitoring_dashboard.py --server.port 8502
```

### Veri Görünmüyor

1. Collector'ların çalıştığından emin olun:
   ```bash
   .\CHECK_COLLECTORS_STATUS.bat
   ```

2. Veritabanı dosyasının var olduğunu kontrol edin:
   ```bash
   .\CHECK_DATA_STATUS.bat
   ```

3. En az 10-15 bar veri toplanmasını bekleyin

### Grafikler Yüklenmiyor

1. Yeterli veri var mı kontrol edin (en az 14 bar)
2. Sembol adının doğru olduğundan emin olun:
   - Gate.io: BTC_USDT
   - Binance: BTCUSDT
3. Exchange seçiminin doğru olduğunu kontrol edin

## Geliştirme

### Yeni Strateji Ekleme

`monitoring_dashboard.py` dosyasındaki "Stratejiler" sekmesine yeni sinyal mantığı ekleyebilirsiniz:

```python
# Örnek: Yeni strateji
st.subheader("Özel Stratejim")
if latest['sma_20'] > latest['sma_50']:
    st.success("🟢 GOLDEN CROSS - AL")
else:
    st.error("🔴 DEATH CROSS - SAT")
```

### Yeni Gösterge Ekleme

`calculate_indicators()` fonksiyonuna yeni indikatörler ekleyin:

```python
# Örnek: ATR hesaplama
df['tr'] = df[['high', 'low', 'close']].apply(
    lambda x: max(x['high'] - x['low'],
                  abs(x['high'] - x['close']),
                  abs(x['low'] - x['close'])),
    axis=1
)
df['atr'] = df['tr'].rolling(window=14).mean()
```

## Performans

- **Otomatik Yenileme**: Her 10 saniye (ayarlanabilir)
- **Veri Sorgusu**: Son 100 bar (ayarlanabilir)
- **Bellek Kullanımı**: ~50-100 MB
- **CPU Kullanımı**: Minimal (~1-2%)

## Güvenlik

- Dashboard yalnızca localhost'ta çalışır (varsayılan)
- Dış erişim için:
  ```bash
  streamlit run Dashboard/monitoring_dashboard.py --server.address 0.0.0.0
  ```
- Production'da reverse proxy kullanın (nginx, Apache)

## Katkıda Bulunma

Dashboard'a yeni özellikler eklemek için:

1. `Dashboard/monitoring_dashboard.py` dosyasını düzenleyin
2. Yeni sekme eklemek için `st.tabs()` kullanın
3. Yeni metrik eklemek için `st.metric()` kullanın
4. Yeni grafik için plotly kullanın

## Lisans

ClaudeCodeCoin projesi kapsamında
