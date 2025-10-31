# 🚀 Docker Olmadan ClaudeCodeCoin - Hızlı Başlangıç

Bu guide, Docker olmadan Phase 1 POC'yi test etmek içindir.

## ✅ Ön Gereksinimler

- ✅ Python 3.11+ kurulu
- ✅ İnternet bağlantısı (Binance WebSocket için)
- ❌ Docker GEREKLİ DEĞİL!

## 🎯 Ne Yapıyoruz?

Phase 1'in temel amacı **Binance'ten gerçek zamanlı veri toplamak**.

**Normal versiyon**: Binance → Kafka → TimescaleDB (Docker gerekli)
**Standalone versiyon**: Binance → CSV + SQLite (Docker GEREKMİYOR!)

## 📦 Kurulum

### Adım 1: Proje Dizinine Git

```powershell
cd C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin
```

### Adım 2: Virtual Environment Oluştur ve Aktif Et

```powershell
# Virtual environment oluştur
python -m venv venv

# Aktif et
.\venv\Scripts\Activate.ps1

# Execution policy hatası alırsanız:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Adım 3: Git Pull (Güncel Dosyaları Al)

```powershell
git pull origin claude/crypto-quant-fund-architecture-011CUez7v2mujBBJSFQkeihx
```

### Adım 4: Minimal Dependencies Kur

```powershell
pip install -r requirements-minimal.txt
```

**Beklenen süre**: 2-5 dakika

## 🚀 Veri Toplamaya Başla

### Collector'ı Çalıştır

```powershell
python Phase1_DataBackbone\collectors\standalone_binance_collector.py
```

**Ne olacak:**

1. ✅ Binance WebSocket'e bağlanacak
2. ✅ BTC, ETH, SOL, BNB, XRP için 1 dakikalık mum verileri toplayacak
3. ✅ Her kapanan mum için:
   - CSV dosyasına yazacak (`data_output/csv/`)
   - SQLite veritabanına kaydedecek (`data_output/binance_data.db`)
4. ✅ Ekranda gerçek zamanlı veriyi göreceksiniz!

**Örnek Çıktı:**

```
======================================================================
🚀 ClaudeCodeCoin - Standalone Binance Collector
======================================================================
Docker olmadan çalışan versiyon
Veri: CSV + SQLite
======================================================================

✅ SQLite database oluşturuldu: data_output\binance_data.db
🚀 WebSocket bağlantısı açıldı!
📡 Dinlenen coinler: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT
⏱️  Zaman aralığı: 1m
💾 Veri klasörü: C:\Users\...\data_output
📊 Database: binance_data.db
======================================================================
🔄 Veri toplamaya başlandı... (Durdurmak için Ctrl+C)
======================================================================

📊 BTCUSDT 1m | O: 69234.50 H: 69245.00 L: 69200.12 C: 69230.75 | V: 123.45 | 💾 Saved (Total: 1)
📊 ETHUSDT 1m | O: 3456.78 H: 3460.00 L: 3450.00 C: 3458.50 | V: 567.89 | 💾 Saved (Total: 2)
📊 SOLUSDT 1m | O: 145.67 H: 146.00 L: 145.50 C: 145.89 | V: 1234.56 | 💾 Saved (Total: 3)
...
```

### Durdurmak İçin

```
Ctrl + C
```

## 📊 Toplanan Veriyi Görüntüle

### Basit Görünüm

```powershell
python Phase1_DataBackbone\collectors\view_collected_data.py
```

**Çıktı örneği:**

```
======================================================================
📊 ClaudeCodeCoin - Toplanan Veri Analizi
======================================================================

📈 Toplam Kayıt: 150 mum

📊 Coin Bazında İstatistikler:
----------------------------------------------------------------------
  BTCUSDT    | Mum:     30 | İlk: 2025-10-31 12:00 | Son: 2025-10-31 12:29 | Avg Vol: 125.45
  ETHUSDT    | Mum:     30 | İlk: 2025-10-31 12:00 | Son: 2025-10-31 12:29 | Avg Vol: 567.89
  SOLUSDT    | Mum:     30 | İlk: 2025-10-31 12:00 | Son: 2025-10-31 12:29 | Avg Vol: 1234.56

📋 Son 10 Kayıt:
----------------------------------------------------------------------
  2025-10-31 12:29:00 | BTCUSDT    | O:  69234.50 H:  69245.00 L:  69200.12 C:  69230.75 | Vol:      123.45
  2025-10-31 12:29:00 | ETHUSDT    | O:   3456.78 H:   3460.00 L:   3450.00 C:   3458.50 | Vol:      567.89
  ...

💰 Fiyat Analizi (Son Mum):
----------------------------------------------------------------------
  🟢 BTCUSDT    | Fiyat: $  69,230.75 | Değişim:  +0.05% | Hacim:         123.45
  🔴 ETHUSDT    | Fiyat: $   3,458.50 | Değişim:  -0.12% | Hacim:         567.89
  ...

💾 Veritabanı Boyutu: 0.25 MB
📁 Konum: C:\Users\...\data_output\binance_data.db
======================================================================
```

### CSV Export (Pandas gerekli)

```powershell
# Pandas kuruluysa
python Phase1_DataBackbone\collectors\view_collected_data.py --export

# Pandas yoksa kur
pip install pandas
```

## 📁 Dosya Yapısı

Veri topladıktan sonra:

```
ClaudeCodeCoin/
└── data_output/
    ├── binance_data.db              # SQLite veritabanı (tüm veriler)
    └── csv/
        ├── BTCUSDT_1m.csv          # BTC verileri
        ├── ETHUSDT_1m.csv          # ETH verileri
        ├── SOLUSDT_1m.csv          # SOL verileri
        ├── BNBUSDT_1m.csv          # BNB verileri
        └── XRPUSDT_1m.csv          # XRP verileri
```

### CSV Formatı

```csv
timestamp,datetime,open,high,low,close,volume,number_of_trades,collected_at
1730380800000,2025-10-31T12:00:00,69234.5,69245.0,69200.12,69230.75,123.45,450,2025-10-31T12:01:00.123456
```

## 🎨 SQLite Veriyi Excel/Python ile Aç

### Excel ile

1. Excel'i aç
2. **Data** → **Get Data** → **From Database** → **From SQLite Database**
3. `data_output/binance_data.db` seç
4. `klines` tablosunu seç

### Python Pandas ile

```python
import sqlite3
import pandas as pd

# Veritabanına bağlan
conn = sqlite3.connect('data_output/binance_data.db')

# Veriyi pandas'a al
df = pd.read_sql_query("SELECT * FROM klines", conn)

# Analiz yap
print(df.describe())
print(df.groupby('symbol')['close'].mean())

# Grafik çiz
df[df['symbol'] == 'BTCUSDT'].plot(x='datetime', y='close')
```

## 🔧 Ayarlar (Özelleştirme)

`standalone_binance_collector.py` dosyasını düzenleyerek:

### Farklı Coinler

```python
# Dosyanın sonunda main() fonksiyonunu düzenleyin
symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]  # İstediğiniz coinler
```

### Farklı Zaman Aralığı

```python
interval = "5m"  # 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d
```

### Farklı Output Klasörü

```python
output_dir = "my_crypto_data"  # İstediğiniz klasör adı
```

## 📊 Veriyle Ne Yapabilirim?

### 1. Gerçek Zamanlı Fiyat İzleme
- Collector çalıştığı sürece gerçek fiyatları görürsünüz

### 2. Tarihsel Veri Analizi
- SQLite/CSV'deki veriyi Python/Excel ile analiz edin
- Fiyat değişimlerini, hacim patternlerini inceleyin

### 3. Strateji Backtesting
- Toplanan veriyle kendi stratejilerinizi test edin
- "RSI 30'un altına düşünce al" gibi kuralları test edin

### 4. Makine Öğrenmesi
- Pandas ile veriyi işleyin
- Sklearn ile fiyat tahmini modelleri oluşturun

## ⚡ Hızlı Testler

### Test 1: 5 Dakika Veri Topla

```powershell
# Collector'ı başlat
python Phase1_DataBackbone\collectors\standalone_binance_collector.py

# 5 dakika bekle (5 coin × 5 dakika = 25 mum verisi)
# Ctrl+C ile durdur

# Veriyi gör
python Phase1_DataBackbone\collectors\view_collected_data.py
```

### Test 2: Sadece BTC Topla

`standalone_binance_collector.py` dosyasındaki `main()` fonksiyonunu düzenleyin:

```python
symbols = ["BTCUSDT"]  # Sadece BTC
```

## 🆚 Docker vs Standalone Karşılaştırma

| Özellik | Docker Versiyonu | Standalone Versiyonu |
|---------|------------------|----------------------|
| **Kurulum** | Karmaşık, Docker gerekli | Basit, sadece Python |
| **Veri Kaynağı** | Binance WebSocket | Binance WebSocket |
| **Veri İşleme** | Kafka (gerçek zamanlı) | Direkt kayıt |
| **Veri Depolama** | TimescaleDB (PostgreSQL) | SQLite + CSV |
| **Cache** | Redis | Yok (gerekmiyor) |
| **Monitoring** | Grafana, Prometheus | Terminal çıktısı |
| **Ölçeklenebilirlik** | ⭐⭐⭐⭐⭐ Yüksek | ⭐⭐ Orta (1 bilgisayar) |
| **Performans** | ⭐⭐⭐⭐⭐ Çok yüksek | ⭐⭐⭐ İyi (POC için yeterli) |
| **Kullanım Kolaylığı** | ⭐⭐ Zor | ⭐⭐⭐⭐⭐ Çok kolay |
| **Önerilen** | Production için | Geliştirme/Test için |

## 🐛 Sorun Giderme

### "ModuleNotFoundError: No module named 'websocket'"

```powershell
pip install websocket-client
```

### "Permission denied" (SQLite yazamıyor)

```powershell
# Yönetici olarak PowerShell açın veya farklı klasör kullanın
```

### WebSocket bağlantısı kapanıyor

- İnternet bağlantınızı kontrol edin
- Script otomatik olarak yeniden bağlanmayı deneyecek

### Veri görünmüyor

- En az **1 dakika** bekleyin (1m interval için)
- İlk mum kapanmadan veri kaydedilmez

## 🎯 Başarı Kriterleri

✅ Collector çalıştı
✅ WebSocket bağlandı
✅ Gerçek zamanlı veriler göründü
✅ `data_output/` klasörü oluştu
✅ CSV dosyaları oluştu
✅ SQLite veritabanı oluştu
✅ Viewer scripti veriyi gösterdi

**Tebrikler! Phase 1 POC başarıyla çalışıyor!** 🎉

## ⏭️ Sonraki Adımlar

### Kısa Vadede:
1. Farklı coinler ve zaman aralıkları deneyin
2. Toplanan veriyi Python/Excel ile analiz edin
3. Basit stratejiler test edin

### Orta Vadede:
1. İndikatör hesaplama ekleyin (RSI, MACD)
2. Basit bir backtesting motoru yazın
3. Sinyal üretimi ekleyin

### Uzun Vadede:
1. Docker'ı kurun ve tam versiyona geçin
2. Kafka ile gerçek zamanlı processing
3. Machine learning modelleri ekleyin

## 📞 Destek

Sorun yaşarsanız:
1. Hata mesajını not edin
2. `view_collected_data.py` çalışıyor mu test edin
3. GitHub Issues'da sorun bildirin

---

**Güncelleme**: 2025-10-31
**Versiyon**: Standalone 1.0
**Yazar**: ClaudeCodeCoin Team
