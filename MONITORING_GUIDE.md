# 📊 ClaudeCodeCoin - İzleme ve Metrik Rehberi

## 📋 İçindekiler
1. [Sistem Sağlığı Kontrolü](#sistem-sağlığı-kontrolü)
2. [Takip Edilmesi Gereken Metrikler](#takip-edilmesi-gereken-metrikler)
3. [Performans Göstergeleri (KPIs)](#performans-göstergeleri-kpis)
4. [Alarm ve Uyarılar](#alarm-ve-uyarılar)
5. [Log Analizi](#log-analizi)
6. [Optimizasyon Önerileri](#optimizasyon-önerileri)

---

## 🔍 Sistem Sağlığı Kontrolü

### Hızlı Kontrol
```bash
# Tek komutla tüm sistemi kontrol et
CHECK_SYSTEM.bat

# veya manuel
python SYSTEM_HEALTH_CHECK.py
```

### Ne Kontrol Edilir?

#### 1. **Veritabanı Durumu** 📁
- Veritabanı dosyaları mevcut mu?
- Kayıt sayısı yeterli mi?
- Son veri güncellemesi ne zaman yapıldı?

**Beklenen:**
- ✅ Binance Data: 10,000+ kayıt
- ✅ Paper Trading DB: Mevcut
- ✅ Son güncelleme: <5 dakika önce

**Sorun Göstergeleri:**
- ❌ Veritabanı bulunamadı
- ⚠️ Son güncelleme >10 dakika önce
- ⚠️ 0 kayıt

#### 2. **Pump Scanner Durumu** 🔍
- Scanner çalışıyor mu?
- Alert üretiliyor mu?
- Son alert ne zaman?

**Beklenen:**
- ✅ Bugün en az 1 alert
- ✅ Son 1 saatte veri var

**Sorun Göstergeleri:**
- ❌ Bugün hiç alert yok
- ⚠️ Son 2 saatte alert yok (sakin piyasa olabilir)

#### 3. **Paper Trading Durumu** 💰
- Trading engine çalışıyor mu?
- Pozisyonlar açılıyor mu?
- Bakiye doğru mu?

**Beklenen:**
- ✅ Bakiye: $8,000 - $12,000 arası (başlangıç $10,000)
- ✅ Açık pozisyonlar: 0-15 arası
- ✅ Toplam trade: >0

**Sorun Göstergeleri:**
- ❌ Bakiye <$5,000 (çok fazla kayıp)
- ⚠️ Hiç trade yok (birkaç saat sonra)
- ⚠️ Açık pozisyon >15 (config hatası)

#### 4. **Log Dosyaları** 📝
- Log dosyaları oluşturuluyor mu?
- Boyutlar normal mi?
- Hatalar var mı?

**Beklenen:**
- ✅ paper_trading.log mevcut
- ✅ hybrid_scanner.log mevcut
- ✅ Boyut: <100 MB

**Sorun Göstergeleri:**
- ❌ Log dosyası yok
- ⚠️ Boyut >500 MB (temizleme gerekli)
- ❌ Son değişiklik >30 dakika önce

---

## 📈 Takip Edilmesi Gereken Metrikler

### 1. **Trading Performance Metrikleri**

#### Temel Metrikler
| Metrik | Açıklama | İdeal Değer | Kritik Eşik |
|--------|----------|-------------|-------------|
| **Win Rate** | Kazanan trade oranı | >60% | <40% |
| **Avg P&L** | Ortalama kar/zarar | >$2 | <$0 |
| **Total P&L** | Toplam kar/zarar | >$0 | <-$500 |
| **Max Drawdown** | En büyük düşüş | <15% | >30% |
| **Sharpe Ratio** | Risk/getiri oranı | >1.5 | <0.5 |

#### Nasıl Hesaplanır?

**Win Rate:**
```python
win_rate = (kazanan_trade_sayısı / toplam_trade) * 100
```

**Max Drawdown:**
```python
max_drawdown = ((düşük_bakiye - başlangıç_bakiye) / başlangıç_bakiye) * 100
```

**Sharpe Ratio:**
```python
sharpe_ratio = (ortalama_getiri - risksiz_faiz) / standart_sapma
```

### 2. **Operational Metrikleri**

#### Veri Kalitesi
- **Data Freshness**: Son veri <5 dakika önceki
- **Symbol Coverage**: Hedeflenen coinlerin %90+'ı var
- **Alert Frequency**: Saatte 1-10 alert

#### Sistem Performansı
- **Response Time**: Pozisyon açma <5 saniye
- **Uptime**: %99+ (günde <15 dakika downtime)
- **CPU Usage**: <50%
- **Memory Usage**: <2 GB
- **Disk Usage**: <80%

---

## 🎯 Performans Göstergeleri (KPIs)

### Günlük Takip Edilecekler

#### Her Sabah Kontrol Et (09:00)
```bash
CHECK_SYSTEM.bat
```

**Kontrol Listesi:**
- [ ] Gece boyunca sistem çalıştı mı?
- [ ] Yeni pozisyonlar açıldı mı?
- [ ] Kapatılan pozisyonlar kar etti mi?
- [ ] Bakiye değişimi nedir?
- [ ] Bugün için alert var mı?

#### Her Akşam Kontrol Et (21:00)
```bash
python CHECK_PAPER_TRADING_STATUS.py
```

**Kontrol Listesi:**
- [ ] Açık pozisyonlar neler?
- [ ] Günlük P&L nedir?
- [ ] Win rate ne durumda?
- [ ] Yarına açık kalacak pozisyon var mı?

### Haftalık Rapor

Her Pazartesi sabahı:

```python
# Haftalık performans özeti
python -c "
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('Phase7_PaperTrading/data_output/paper_trading.db')
cursor = conn.cursor()

# Son 7 gün
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

cursor.execute('''
    SELECT
        COUNT(*) as total_trades,
        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
        AVG(pnl) as avg_pnl,
        SUM(pnl) as total_pnl
    FROM positions
    WHERE status='CLOSED' AND entry_time >= ?
''', (week_ago,))

stats = cursor.fetchone()
print(f'📊 HAFTALIK RAPOR')
print(f'  Toplam Trade: {stats[0]}')
print(f'  Win Rate: {(stats[1]/stats[0]*100):.1f}%')
print(f'  Avg P&L: ${stats[2]:.2f}')
print(f'  Total P&L: ${stats[3]:.2f}')

conn.close()
"
```

---

## 🚨 Alarm ve Uyarılar

### Kritik Alarmlar (Hemen Müdahale)

#### 1. **Büyük Kayıp**
```
Tetikleyici: Bakiye < $7,000 veya günlük kayıp > $500
Aksiyon: Sistemi durdur, logları incele
```

#### 2. **Sistem Durmuş**
```
Tetikleyici: Son veri >30 dakika önce
Aksiyon: Sistemi yeniden başlat
```

#### 3. **Çok Fazla Açık Pozisyon**
```
Tetikleyici: Açık pozisyon > 15
Aksiyon: Config'i kontrol et, sistemi durdur
```

### Uyarılar (İzle)

#### 1. **Düşük Win Rate**
```
Tetikleyici: Win rate < 50% (20+ trade sonrası)
Aksiyon: Confidence threshold'u yükselt
```

#### 2. **Az Sinyal**
```
Tetikleyici: 2 saatte 0 alert
Aksiyon: Piyasa sakin, normal olabilir - izlemeye devam
```

#### 3. **Disk Dolmak Üzere**
```
Tetikleyici: Disk kullanımı > 85%
Aksiyon: Log dosyalarını temizle
```

---

## 📝 Log Analizi

### Önemli Log Mesajları

#### Başarılı İşlemler
```
[OK] Pozisyon açıldı: SOL_USDT
[CLOSE] Pozisyon kapatıldı: BTC_USDT, P&L: $12.50
[ALERT] Pump detected: ETH_USDT (Confidence: 75%)
```

#### Hatalar
```
[ERROR] Fiyat alınamadı: XYZ_USDT
[ERROR] Database bağlantı hatası
[ERROR] Pozisyon açılamadı: Bakiye yetersiz
```

#### Uyarılar
```
[WARN] Confidence çok düşük (35% < 50%)
[WARN] Volume spike yetersiz
[WARN] Bu coin için fiyat verisi yok
```

### Log Filtreleme

```powershell
# Sadece hataları göster
Get-Content logs\paper_trading.log | Select-String "ERROR"

# Son 1 saatin logları
Get-Content logs\paper_trading.log -Tail 500 | Select-String "$(Get-Date -Format 'yyyy-MM-dd HH')"

# Belirli bir coin için
Get-Content logs\paper_trading.log | Select-String "BTC_USDT"

# Açılan pozisyonlar
Get-Content logs\paper_trading.log | Select-String "\[OPEN\]"
```

---

## 💡 Optimizasyon Önerileri

### Win Rate Düşükse (<50%)

#### Çözüm 1: Confidence Threshold Yükselt
```python
# Phase7_PaperTrading/config.py
MIN_CONFIDENCE_TO_TRADE = 60.0  # 50 → 60
```

#### Çözüm 2: Volume Spike Ekle
```python
MIN_VOLUME_SPIKE = 50.0  # 0 → 50 (en az %50 artış)
```

#### Çözüm 3: Take Profit Düşür (Kar erken al)
```python
TAKE_PROFIT_PERCENT = {
    'CRITICAL': 15.0,  # 25 → 15
    'HIGH': 12.0,      # 20 → 12
    'MEDIUM': 10.0,    # 15 → 10
    'LOW': 8.0         # 10 → 8
}
```

### Çok Az Sinyal Geliyorsa

#### Çözüm 1: Confidence Düşür
```python
MIN_CONFIDENCE_TO_TRADE = 40.0  # 50 → 40
```

#### Çözüm 2: Volume Şartını Kaldır
```python
MIN_VOLUME_SPIKE = 0.0  # Zaten 0
```

#### Çözüm 3: Daha Fazla Coin Ekle
```python
# start_trading_system_windows.py çalıştırırken
python start_trading_system_windows.py --top 100  # 50 → 100
```

### Çok Fazla Pozisyon Açılıyorsa

#### Çözüm: Max Pozisyon Azalt
```python
# Phase7_PaperTrading/config.py
MAX_OPEN_POSITIONS = 10  # 15 → 10
```

### Kayıplar Çok Büyükse

#### Çözüm 1: Stop Loss Sıkılaştır
```python
STOP_LOSS_PERCENT = 3.0  # 5 → 3
```

#### Çözüm 2: Trailing Stop Ekle
```python
TRAILING_STOP_PERCENT = 2.0  # 3 → 2 (daha sıkı)
```

#### Çözüm 3: Pozisyon Boyutu Küçült
```python
MAX_POSITION_SIZE_PERCENT = 5.0  # 10 → 5
```

---

## 📊 Dashboard Metrikleri

### Dashboard'da İzlenecek Grafikler

#### 1. **Equity Curve** (P&L Grafiği)
- Bakiye zamanla nasıl değişiyor?
- Trend yukarı mı aşağı mı?
- Volatilite nasıl?

**İdeal:** Sürekli yükselen, düşük volatilite
**Problem:** Aşağı trend, yüksek volatilite

#### 2. **Win Rate Grafiği**
- Win rate zamanla nasıl değişiyor?
- Trend iyileşiyor mu?

**İdeal:** %55-70 arası stabil
**Problem:** %40'ın altına düşüyor

#### 3. **Trade Distribution**
- Kazançlar vs kayıplar dağılımı
- Büyük kayıplar var mı?

**İdeal:** Kazançlar daha fazla ve büyük
**Problem:** Büyük kayıplar, küçük kazançlar

---

## 🔄 Rutin Bakım

### Günlük Bakım (2 dakika)
```bash
# Sabah kontrolü
CHECK_SYSTEM.bat

# Logları kısa gözden geçir
Get-Content logs\paper_trading.log -Tail 50
```

### Haftalık Bakım (10 dakika)
```bash
# Performans raporu
python CHECK_PAPER_TRADING_STATUS.py

# Log dosyalarını temizle (>100 MB ise)
# Manuel: Eski logları sil veya arşivle

# Backup al
xcopy Phase7_PaperTrading\data_output\paper_trading.db backups\ /Y
```

### Aylık Bakım (30 dakika)
```bash
# Tam sistem sıfırlaması ve yeniden başlatma
RESET_SYSTEM.bat
START_AUTO_TRADING_SIMPLE.bat

# Ayarları gözden geçir ve optimize et
notepad Phase7_PaperTrading\config.py
```

---

## 📞 Sorun Giderme Kontrol Listesi

### Problem: Hiç pozisyon açılmıyor

**Kontrol Sırası:**
1. ✅ Scanner çalışıyor mu? → `CHECK_SYSTEM.bat`
2. ✅ Alert üretiliyor mu? → `python CHECK_PUMP_ALERTS.py`
3. ✅ Fiyat verisi var mı? → Database kontrolü
4. ✅ Config çok sıkı mı? → `MIN_CONFIDENCE_TO_TRADE` düşür
5. ✅ Bakiye var mı? → En az $100 gerekli

### Problem: Win rate çok düşük

**Kontrol Sırası:**
1. ✅ Kaç trade yapıldı? → En az 20 trade gerekli
2. ✅ Confidence threshold yeterli mi? → 60'a çıkar
3. ✅ Take profit çok yüksek mi? → Düşür
4. ✅ Stop loss çok geniş mi? → Daralt
5. ✅ Piyasa trendi nasıl? → Bear market'te zor

### Problem: Sistem durmuş

**Kontrol Sırası:**
1. ✅ Process'ler çalışıyor mu? → Task Manager
2. ✅ Hata logu var mı? → Log dosyalarını kontrol et
3. ✅ Disk dolu mu? → Disk kontrolü
4. ✅ Network bağlantısı var mı? → Ping test
5. ✅ Yeniden başlat → `START_AUTO_TRADING_SIMPLE.bat`

---

## 🎯 Başarı Kriterleri

### 1 Hafta Sonra
- [ ] En az 10 trade yapılmış
- [ ] Win rate >40%
- [ ] Bakiye >$9,500
- [ ] Sistem %95+ uptime

### 1 Ay Sonra
- [ ] En az 50 trade yapılmış
- [ ] Win rate >50%
- [ ] Bakiye >$10,000 (pozitif)
- [ ] Sharpe Ratio >0.5

### 3 Ay Sonra
- [ ] En az 200 trade yapılmış
- [ ] Win rate >55%
- [ ] Bakiye >$11,000 (10% getiri)
- [ ] Max Drawdown <20%
- [ ] Sharpe Ratio >1.0

---

**Başarılar! Bu metrikleri düzenli takip ederek sisteminizi optimize edebilirsiniz.** 🚀
