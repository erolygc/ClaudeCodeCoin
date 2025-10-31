# 🚀 ClaudeCodeCoin - Quick Start Guide (Phase 1 Testing)

Bu guide, Phase 1 (Data Backbone) POC'sini test etmek için adım adım talimatlar içerir.

## ✅ Ön Gereksinimler

1. **Docker & Docker Compose** kurulu olmalı
2. **Python 3.11+** kurulu olmalı
3. **PostgreSQL client** (psql) kurulu olmalı
4. **Git** kurulu olmalı

### Kurulum Kontrolü

```bash
docker --version
docker-compose --version
python --version
psql --version
git --version
```

## 📦 Adım 1: Repository'yi Klonla (veya Pull)

```bash
# Eğer yeni klonluyorsanız
git clone <repository-url>
cd ClaudeCodeCoin

# Eğer zaten klonladıysanız
git pull origin claude/crypto-quant-fund-architecture-011CUez7v2mujBBJSFQkeihx
```

## 🔧 Adım 2: Python Dependencies Kur

```bash
# Virtual environment oluştur (önerilir)
python -m venv venv

# Activate et
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Dependencies kur
pip install -r requirements.txt
```

**Not**: `ta-lib` kurulumu sistem bazlı binary gerektirir:
- **Mac**: `brew install ta-lib`
- **Linux**: https://github.com/mrjbq7/ta-lib#dependencies
- **Windows**: https://github.com/mrjbq7/ta-lib#windows

Eğer ta-lib kurulumu hata verirse, şimdilik atlayabilirsiniz (Phase 1 POC için zorunlu değil).

## 🐳 Adım 3: Docker Infrastructure'ı Başlat

```bash
# Tüm servisleri arka planda başlat
docker-compose up -d

# Logları takip et (opsiyonel)
docker-compose logs -f
```

Bu aşağıdaki servisleri başlatır:
- ✅ **Zookeeper** (port 2181)
- ✅ **Kafka** (port 9092)
- ✅ **Kafka UI** (port 8080) - http://localhost:8080
- ✅ **TimescaleDB** (port 5432)
- ✅ **Redis** (port 6379)
- ✅ **Prometheus** (port 9090) - http://localhost:9090
- ✅ **Grafana** (port 3000) - http://localhost:3000

### Servislerin Durumunu Kontrol Et

```bash
docker-compose ps
```

Tüm servisler "Up" durumunda olmalı.

### Sorun Giderme

Eğer bir servis başlamazsa:

```bash
# Logları kontrol et
docker-compose logs <service-name>

# Örnek: Kafka loglarını gör
docker-compose logs kafka

# Servisleri yeniden başlat
docker-compose restart

# Veya sıfırdan başlat
docker-compose down
docker-compose up -d
```

## 🗄️ Adım 4: Veritabanı Schema'sını Yükle

```bash
# TimescaleDB'ye bağlan ve schema'yı yükle
docker exec -i ccc-timescaledb psql -U ccc_user -d ccc_trading < Phase1_DataBackbone/storage/timescaledb_schema.sql
```

Alternatif olarak:

```bash
psql -h localhost -U ccc_user -d ccc_trading -f Phase1_DataBackbone/storage/timescaledb_schema.sql
# Password: ccc_password_change_in_production
```

Başarılı olursa şunu göreceksiniz:
```
ClaudeCodeCoin TimescaleDB schema created successfully!
```

### Schema'yı Doğrula

```bash
docker exec -it ccc-timescaledb psql -U ccc_user -d ccc_trading -c "\dt"
```

Aşağıdaki tablolar görünmeli:
- raw_klines
- raw_orderbook
- raw_trades
- funding_rates
- indicators
- signals
- orders
- positions
- vs.

## 🧪 Adım 5: Test Scriptlerini Çalıştır

### Test 1: Database Connection

```bash
python tests/test_database_connection.py
```

**Beklenen Sonuç**: Tüm testler PASSED olmalı.

### Test 2: Kafka Connection

```bash
python tests/test_kafka_connection.py
```

**Beklenen Sonuç**: Tüm testler PASSED olmalı.

## 📊 Adım 6: Gerçek Veri Toplama (POC Test)

### 6.1: Binance Collector'ı Başlat (Terminal 1)

```bash
python Phase1_DataBackbone/collectors/binance_collector.py
```

**Ne beklemeliyiz:**
- WebSocket bağlantısı açılacak
- BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT için 1 dakikalık mum verileri gelecek
- Her kapanan mum için Kafka'ya mesaj gönderilecek

**Örnek Log:**
```
🚀 WebSocket connection opened for 5 symbols
📊 BTCUSDT 1m | O: 50000 H: 50100 L: 49900 C: 50050 | V: 123.45 | Sent to Kafka
```

**Not**: İlk mum kapanana kadar (~1 dakika) hiç mesaj göremeyebilirsiniz. Bu normaldir.

### 6.2: Kafka Consumer'ı Başlat (Terminal 2)

Yeni bir terminal açın:

```bash
python Phase1_DataBackbone/kafka/kafka_consumer.py
```

**Ne beklemeliyiz:**
- Kafka'dan mesajlar okunacak
- TimescaleDB'ye yazılacak
- Her kayıt için log gelecek

**Örnek Log:**
```
💾 Saved: BTCUSDT 1m | C: 50050.0 | V: 123.45
📊 Stats: Consumed=10, Saved=10, Errors=0, Success Rate=100.00%
```

### 6.3: Kafka UI'dan Verileri Gör (Tarayıcı)

http://localhost:8080 adresine git

- **Topics** sekmesine tıkla
- `raw.klines.1m` topic'ini seç
- **Messages** tab'ine tıkla
- Gerçek zamanlı mesajları göreceksin!

### 6.4: Veritabanındaki Verileri Kontrol Et

Yeni bir terminal açın:

```bash
docker exec -it ccc-timescaledb psql -U ccc_user -d ccc_trading
```

SQL komutları:

```sql
-- Son 10 mumu göster
SELECT
    time,
    symbol,
    open,
    high,
    low,
    close,
    volume
FROM raw_klines
ORDER BY time DESC
LIMIT 10;

-- Sembol başına kaç mum var
SELECT
    symbol,
    COUNT(*) as count,
    MIN(time) as first_candle,
    MAX(time) as last_candle
FROM raw_klines
GROUP BY symbol;

-- Çıkış için
\q
```

## 🎯 Adım 7: Grafana Dashboard (Opsiyonel)

http://localhost:3000 adresine git
- **Username**: admin
- **Password**: admin

İlk girişte şifre değiştirmenizi isteyecek (atlayabilirsiniz).

**Not**: Phase 1 POC'de henüz hazır dashboard yok, ama Prometheus veri kaynağını ekleyebilir ve kendi dashboard'larınızı oluşturabilirsiniz.

## 🛑 Sistemi Durdurma

### Collector & Consumer'ı Durdur
Her iki terminal'de de `Ctrl+C` yapın

### Infrastructure'ı Durdur

```bash
# Servisleri durdur ama verileri sakla
docker-compose stop

# Servisleri durdur ve container'ları sil (veriler kalır)
docker-compose down

# HER ŞEYİ SİL (VERİLER DAHİL!) - DİKKATLİ KULLAN
docker-compose down -v
```

## 📊 Başarı Kriterleri

Phase 1 POC test başarılı sayılır eğer:

✅ Tüm Docker servisleri ayakta
✅ Database ve Kafka test scriptleri PASSED
✅ Binance collector WebSocket'e bağlanabilir
✅ Kafka topic'ine mesaj gönderebilir
✅ Consumer mesajları okuyup DB'ye yazabilir
✅ Kafka UI'da mesajları görebilir
✅ SQL ile veriyi sorgulayabilir

## 🐛 Sık Karşılaşılan Sorunlar

### 1. "Connection refused" Hatası

**Sebep**: Docker servisleri henüz başlamamış olabilir.

**Çözüm**:
```bash
docker-compose ps  # Servislerin durumunu kontrol et
docker-compose up -d  # Yeniden başlat
```

### 2. "ta-lib" Kurulum Hatası

**Çözüm**: Şimdilik ta-lib'i requirements.txt'den çıkarabilirsiniz:
```bash
pip install -r requirements.txt --ignore-installed ta-lib
```

Phase 1 POC için ta-lib zorunlu değil.

### 3. "Port already in use" Hatası

**Sebep**: Port'lar başka bir uygulama tarafından kullanılıyor.

**Çözüm**:
- Ya o uygulamayı durdurun
- Ya da docker-compose.yml dosyasındaki port'ları değiştirin

```bash
# Hangi process hangi portu kullanıyor
# Linux/Mac:
lsof -i :9092
# Windows:
netstat -ano | findstr :9092
```

### 4. WebSocket Bağlantısı Kapanıyor

**Sebep**: İnternet bağlantısı veya Binance API sorunu.

**Çözüm**:
- İnternet bağlantınızı kontrol edin
- Script otomatik yeniden bağlanmayı dener
- Logları kontrol edin

### 5. "No module named 'Phase1_DataBackbone'"

**Sebep**: Python path sorunu.

**Çözüm**:
```bash
# Proje root dizininde olduğunuzdan emin olun
cd ClaudeCodeCoin

# PYTHONPATH'i set edin
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%cd%      # Windows
```

## 📞 Destek

Sorun yaşarsanız:
1. Log dosyalarını kontrol edin: `logs/`
2. Docker loglarını kontrol edin: `docker-compose logs <service>`
3. GitHub Issues'da issue açın

## 🎉 Başarılı Test Sonrası

Tebrikler! Phase 1 POC başarıyla çalışıyor.

**Sıradaki Adımlar**:
1. **Indicator Calculator** ekle (RSI, MACD, Bollinger Bands)
2. **Order Book Collector** ekle
3. **Social Media Collector** ekle (Twitter/Reddit sentiment)
4. **Feature Store (FEAST)** kur

Phase 2 (Alpha Engine) hazır olduğunda backtesting ve strateji optimizasyonuna geçebilirsiniz!

---

**Son Güncelleme**: 2025-10-31
**Versiyon**: 1.0
**Yazar**: ClaudeCodeCoin Team
