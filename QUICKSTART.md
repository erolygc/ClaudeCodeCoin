# ClaudeCodeCoin - Hızlı Başlangıç Kılavuzu

## 🚀 Tek Komutla Başlatma

### Windows:
```bash
START_ALL.bat
```

### Linux/Mac:
```bash
chmod +x START_ALL.sh
./START_ALL.sh
```

Bu komut **3 component'i** otomatik olarak başlatır:
1. **Gate.io Data Collector** (550 coin veri toplama)
2. **Pump Scanner** (Gerçek zamanlı pump tespit)
3. **Paper Trading** (Sanal trading motoru)

---

## 🛑 Tüm Sistemi Durdurma

### Windows:
```bash
STOP_ALL.bat
```

### Linux/Mac:
```bash
./STOP_ALL.sh
```

---

## 📊 Sistem Durumunu Kontrol Etme

```bash
python SYSTEM_HEALTH_CHECK.py
```

Bu komut size şunları gösterir:
- ✅ Veritabanı durumu (toplanan veri sayısı)
- ✅ Pump alert sayısı
- ✅ Açık pozisyonlar ve bakiye
- ✅ Log dosyaları durumu
- ✅ Config dosyaları kontrolü

---

## ⚙️ İlk Kurulum

### 1. Gerekli Paketleri Yükleyin:
```bash
pip install websockets gate-api loguru python-dotenv
```

### 2. API Anahtarlarını Ayarlayın:
`config/secrets.env` dosyasını düzenleyin

### 3. Sistemi Başlatın:
```bash
START_ALL.bat   # Windows
./START_ALL.sh  # Linux
```

---

## 🔧 Sorun Giderme

### Collector Çalışmıyor:
```bash
# Log dosyasını kontrol edin:
tail -f logs/gateio_collector_1000coins.log
```

### Paper Trading Pozisyon Açmıyor:
```bash
# Alert dosyası var mı kontrol edin:
ls pump_alerts/
```

---

🎉 **Başarılı kurulum sonrası sistemin tamamı otomatik olarak çalışır!**
