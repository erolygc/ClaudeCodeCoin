# 🚀 Windows Hızlı Başlangıç

## ⚡ 3 Basit Adım

### **Adım 1: Kodu Güncelle**

```powershell
git pull origin claude/dev-project-update-011CUo3BwULJ7Rmb8JqRuqhd
```

### **Adım 2: Sistemi Başlat**

**Yöntem A: Python ile**

```powershell
python start_trading_system_windows.py
```

**Yöntem B: Batch dosyası ile**

```powershell
.\START_SYSTEM.bat
```

Çift tıklayarak da çalıştırabilirsiniz!

### **Adım 3: İzle**

**Yeni bir PowerShell penceresi açın:**

```powershell
# Log izleme scripti
.\watch_logs.ps1

# Veya manuel
Get-Content logs\paper_trading.log -Wait -Tail 20
```

**İşte bu kadar!** 🎉

---

## 🎮 Kullanım Modları

### **Otomatik (Top 50 Coin)**

```powershell
python start_trading_system_windows.py
```

### **Sadece Büyük Coinler**

```powershell
python start_trading_system_windows.py --coins BTC_USDT,ETH_USDT,SOL_USDT
```

### **Top 20**

```powershell
python start_trading_system_windows.py --top 20
```

---

## 🛑 Durdurma

**Terminal'de:**
```
Ctrl+C
```

**Veya:**
```powershell
Stop-Process -Name python
```

---

## 📊 İzleme Komutları (Windows)

### **Logları İzle**

```powershell
# Paper trading log
Get-Content logs\paper_trading.log -Wait -Tail 20

# Scanner log
Get-Content logs\realtime_hybrid_scanner.log -Wait -Tail 20

# Script ile (renkli)
.\watch_logs.ps1
.\watch_logs.ps1 logs\realtime_hybrid_scanner.log
```

### **Sinyalleri Görüntüle**

```powershell
# Sinyal dosyalarını listele
Get-ChildItem Phase6_PumpDetection\signals\

# Son sinyal
Get-Content (Get-ChildItem Phase6_PumpDetection\signals\*.json | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | ConvertTo-Json
```

### **Database Sorguları**

```powershell
# SQLite yükle (ilk kez)
# winget install SQLite.SQLite

# Database'i aç
sqlite3 paper_trading_performance.db

# Son 10 trade
sqlite3 paper_trading_performance.db "SELECT symbol, direction, pnl, pnl_percent FROM positions WHERE status='CLOSED' ORDER BY closed_at DESC LIMIT 10"

# Win rate
sqlite3 paper_trading_performance.db "SELECT COUNT(*) as total, SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins, ROUND(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as win_rate FROM positions WHERE status='CLOSED'"
```

---

## 📁 Dosya Konumları

```
C:\Users\...\ClaudeCodeCoin\
├── START_SYSTEM.bat                         ← Çift tıkla çalıştır
├── start_trading_system_windows.py          ← Ana script (Windows)
├── watch_logs.ps1                            ← Log izleme scripti
│
├── logs\
│   ├── paper_trading.log                    ← Trading logları
│   └── realtime_hybrid_scanner.log          ← Scanner logları
│
├── Phase6_PumpDetection\signals\            ← Oluşturulan sinyaller
│   └── hybrid_*.json
│
├── paper_trading_performance.db             ← Performance database
│
└── config\paper_trading_config.py           ← Ayarlar
```

---

## ⚙️ Ayar Değiştirme

`config\paper_trading_config.py` dosyasını düzenleyin:

```python
# Pozisyon boyutu
POSITION_SIZE = 200.0  # $200'e çıkar

# Max pozisyon sayısı
MAX_OPEN_POSITIONS = 5  # 5'e düşür

# Minimum confidence
MIN_SIGNAL_CONFIDENCE = 80.0  # %80'e çıkar
```

**Değiştirdikten sonra sistemi yeniden başlatın.**

---

## 🚨 Sorun Giderme

### **Problem: "python not recognized"**

**Çözüm:**
```powershell
# Virtual environment aktifleştir
.\venv\Scripts\Activate.ps1

# Sonra tekrar dene
python start_trading_system_windows.py
```

### **Problem: "ModuleNotFoundError"**

**Çözüm:**
```powershell
pip install -r requirements.txt
```

### **Problem: "Database not found"**

**Çözüm:**
```powershell
cd Phase1_DataCollection
python create_test_database.py
python add_pump_data.py
cd ..
```

### **Problem: Log dosyası boş**

**Sebep:** Sistem henüz başlamadı

**Çözüm:**
- Birkaç saniye bekleyin
- `logs\` klasörünün oluştuğunu kontrol edin

### **Problem: Servisler çöküyor**

**Kontrol:**
```powershell
# Servisleri tek tek test et
python Phase6_PumpDetection\realtime_hybrid_scanner.py
python Phase8_FuturesTrading\paper_trading_futures_engine.py
```

---

## 💡 Faydalı PowerShell Komutları

```powershell
# Python süreçlerini görüntüle
Get-Process python

# Tüm Python süreçlerini durdur
Stop-Process -Name python -Force

# Klasör boyutunu göster
Get-ChildItem logs\ | Measure-Object -Property Length -Sum

# En son değiştirilen dosya
Get-ChildItem Phase6_PumpDetection\signals\ | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# JSON dosyasını güzel göster
Get-Content dosya.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 📊 Gerçek Zamanlı İstatistikler

Sistem her 60 saniyede otomatik stats gösterir:

```
================================================================================
ACCOUNT STATISTICS
================================================================================
Balance: $10,234.50
Equity: $10,234.50
Realized PnL: +$234.50 (+2.35%)

Open Positions: 3/10
Total Trades: 24
Winning: 18 | Losing: 6
Win Rate: 75.0%

Max Drawdown: 3.21%
Today's PnL: +$156.20
================================================================================
```

---

## 🎯 Hızlı Referans

```powershell
# Sistemi başlat
python start_trading_system_windows.py

# Logları izle
.\watch_logs.ps1

# Sinyalleri listele
dir Phase6_PumpDetection\signals\

# Database sorgula
sqlite3 paper_trading_performance.db "SELECT * FROM positions WHERE status='CLOSED' ORDER BY closed_at DESC LIMIT 5"

# Sistemi durdur
Ctrl+C
```

---

## ✨ Ekstra İpuçları

### **Multiple Windows ile İzleme:**

**Pencere 1:** Ana sistem
```powershell
python start_trading_system_windows.py
```

**Pencere 2:** Trading logları
```powershell
.\watch_logs.ps1 logs\paper_trading.log
```

**Pencere 3:** Scanner logları
```powershell
.\watch_logs.ps1 logs\realtime_hybrid_scanner.log
```

### **Otomatik Başlatma:**

**Görev Zamanlayıcı ile:**

1. `Task Scheduler` aç
2. `Create Basic Task` tıkla
3. Trigger: `When I log on`
4. Action: `Start a program`
5. Program: `python`
6. Arguments: `start_trading_system_windows.py`
7. Start in: `C:\Users\...\ClaudeCodeCoin`

---

## 📞 Destek

- **Detaylı Dok:** `TRADING_SYSTEM_QUICKSTART.md`
- **Test:** `Phase6_PumpDetection\test_scanner.py`

---

**Windows'ta Başarılar! 🚀**

*Not: Bu bir paper trading sistemidir. Gerçek para kullanılmaz.*
