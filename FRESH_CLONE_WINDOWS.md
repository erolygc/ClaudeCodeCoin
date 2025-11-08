# 🔄 Windows'ta Temiz Proje Kurulumu

GitHub'dan sıfırdan temiz proje kurulumu rehberi.

---

## 🗑️ ADIM 1: Eski Projeyi Temizle

```powershell
# 1. Tüm Python processlerini durdur
Get-Process python,streamlit -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. PowerShell'i kapatıp yeniden aç (virtual environment'tan çıkmak için)

# 3. Eski proje klasörünü sil
cd C:\Users\Botai\Desktop\Projeler
Remove-Item -Recurse -Force ClaudeCodeCoin

# 4. Doğrula (klasör gitmiş olmalı)
Test-Path ClaudeCodeCoin
# False döndürmeli
```

---

## 📥 ADIM 2: GitHub'dan Fresh Clone

```powershell
# 1. Projeler klasörüne git
cd C:\Users\Botai\Desktop\Projeler

# 2. GitHub'dan clone (TEMIZ versiyon)
git clone https://github.com/erolygc/ClaudeCodeCoin.git

# 3. Proje klasörüne gir
cd ClaudeCodeCoin

# 4. Branch'i kontrol et
git branch -a
git checkout claude/dev-project-update-011CUo3BwULJ7Rmb8JqRuqhd
```

---

## 🐍 ADIM 3: Virtual Environment Oluştur

```powershell
# 1. Virtual environment oluştur
python -m venv venv

# 2. Aktif et
.\venv\Scripts\Activate.ps1

# Eğer hata alırsanız (Execution Policy):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Sonra tekrar deneyin:
.\venv\Scripts\Activate.ps1

# 3. Doğrula (venv) yazısı görünmeli
# Prompt: (venv) PS C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin>
```

---

## 📦 ADIM 4: Dependencies Yükle

```powershell
# 1. pip'i güncelle
python -m pip install --upgrade pip

# 2. Tüm gereksinimleri yükle
pip install -r requirements.txt

# Bu 2-3 dakika sürebilir...

# 3. Önemli paketleri kontrol et
pip list | Select-String -Pattern "streamlit|gate-api|plotly"

# Görmelisiniz:
# streamlit        1.29.0
# gate-api         4.32.0
# plotly           5.18.0
```

---

## 🔧 ADIM 5: Gerekli Klasörleri Oluştur

```powershell
# Otomatik oluşturulmayan klasörleri manuel oluştur
New-Item -ItemType Directory -Path "data_output" -Force
New-Item -ItemType Directory -Path "pump_alerts" -Force
New-Item -ItemType Directory -Path "Phase7_PaperTrading\data_output" -Force
New-Item -ItemType Directory -Path "Phase7_PaperTrading\logs" -Force
New-Item -ItemType Directory -Path "Phase8_FuturesTrading\data_output" -Force
New-Item -ItemType Directory -Path "Phase8_FuturesTrading\logs" -Force

Write-Host "Klasorler olusturuldu!" -ForegroundColor Green
```

---

## ✅ ADIM 6: Proje Yapısını Kontrol Et

```powershell
# Temiz proje yapısını gör
tree /F /A

# Görmelisiniz:
ClaudeCodeCoin/
├── Phase1_DataBackbone/       ✅
├── Phase6_PumpDetection/      ✅
├── Phase7_PaperTrading/       ✅
├── Phase8_FuturesTrading/     ✅ (ANA SISTEM)
├── data_output/               ✅ (boş - dolacak)
├── pump_alerts/               ✅ (boş - dolacak)
├── .env.example               ✅
├── .gitignore                 ✅
├── README.md                  ✅
├── requirements.txt           ✅
├── START_SYSTEM.ps1           ✅
├── START_FUTURES_SYSTEM.ps1   ✅
├── CLEANUP_PROJECT.ps1        ✅
└── venv/                      ✅

# SİLİNMİŞ (artık yok):
❌ Phase2_AlphaEngine/
❌ Phase3_RiskManagement/
❌ Phase4_OrderExecution/
❌ Phase5_Analytics/
❌ test_*.py (root'ta)
```

---

## 🚀 ADIM 7: Sistemleri Başlat

### 7a. Ana Sistemi Başlat

```powershell
# Terminal 1 (mevcut terminal)
.\START_SYSTEM.ps1
```

4 yeni terminal açacak:
1. Data Collector
2. Pump Scanner
3. Paper Trading (eski - ignore)
4. Dashboard (eski - ignore)

**2-3 DAKİKA BEKLEYİN** - Veri toplanması gerekiyor!

### 7b. Futures Sistemini Başlat

**YENİ bir PowerShell terminali açın:**

```powershell
# 1. Proje klasörüne git
cd C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin

# 2. Virtual environment aktif et
.\venv\Scripts\Activate.ps1

# 3. Futures sistemini başlat
.\START_FUTURES_SYSTEM.ps1

# Mod seçimi:
Select mode (1-3): 1

# 1 = Paper Trading (güvenli test modu)
```

---

## 📊 ADIM 8: Dashboard'ları Aç

Tarayıcınızda:

### Yeni Futures Dashboard:
```
http://localhost:8502
```

**Göreceksiniz:**
```
Balance: $1,000.00          ✅ TEMİZ BAŞLANGIÇ!
Total Trades: 0             ✅ HİÇ ESKİ VERİ YOK!
Open Positions: 0/10
Total P&L: $0.00
```

### Eski Paper Trading Dashboard:
```
http://localhost:8501
```
(Bunu ignore edebilirsiniz - eski sistem)

---

## 🎯 ADIM 9: İlk Sinyalleri Bekle

**İlk 2-3 Dakika:**
- Data Collector: Veri topluyor
- Pump Scanner: Coin'leri tarıyor
- Dashboard: "Waiting for signals..."

**5-10 Dakika Sonra:**
- İlk pump sinyalleri gelecek
- Futures engine sinyalleri filtreleyecek
- İlk pozisyon açılacak!

**Dashboard'da göreceksiniz:**
```
Balance: $1,000.00
Open Positions: 1/10
┌──────────┬──────────┬─────────┬─────────┬──────────┐
│ Symbol   │ Entry    │ Current │ P&L     │ Liq Dist │
├──────────┼──────────┼─────────┼─────────┼──────────┤
│ BTC_USDT │ $50,000  │ $50,075 │ +$2.50  │ 32% 🟢   │
└──────────┴──────────┴─────────┴─────────┴──────────┘
```

---

## 🔍 ADIM 10: Sistem Sağlığını Kontrol Et

```powershell
# Python processleri çalışıyor mu?
Get-Process python | Format-Table Id, StartTime, CPU

# Görmelisiniz: 10-14 Python process

# Database oluştu mu?
Test-Path data_output\binance_data.db
# True döndürmeli (2-3 dakika sonra)

# Pump alerts geliyor mu?
$today = Get-Date -Format "yyyyMMdd"
Test-Path "pump_alerts\pump_alerts_$today.json"
# True döndürmeli

# Futures log oluştu mu?
Test-Path Phase8_FuturesTrading\logs\futures_trading.log
# True döndürmeli
```

---

## ✅ Başarı Kontrol Listesi

Clone sonrası kontrol edin:

- [ ] ✅ Virtual environment aktif (`(venv)` yazıyor)
- [ ] ✅ Dependencies yüklü (`pip list` kontrol)
- [ ] ✅ Klasörler oluşturuldu
- [ ] ✅ Ana sistem başlatıldı (4 terminal açık)
- [ ] ✅ 2-3 dakika beklendi
- [ ] ✅ Futures başlatıldı (paper mode)
- [ ] ✅ Dashboard açıldı (http://localhost:8502)
- [ ] ✅ Balance $1,000 (temiz başlangıç)
- [ ] ✅ Total Trades: 0 (hiç eski veri yok)
- [ ] ✅ Python processleri çalışıyor
- [ ] ✅ Database oluştu
- [ ] ✅ İlk sinyaller gelmeye başladı

---

## 🎉 Tebrikler!

Temiz proje kurulumu tamamlandı! Artık:

✅ Eski veriler yok
✅ Gereksiz Phase'ler yok
✅ Sadece çalışan sistem var
✅ Fresh start ile test edebilirsiniz

**Şimdi sistemi 30-60 dakika izleyin ve performansı görün!**

---

## ⚠️ Sorun Giderme

### Sorun 1: "cannot be loaded because running scripts is disabled"

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Sorun 2: "Database not found"

Ana sistemi başlatıp 2-3 dakika bekleyin:
```powershell
.\START_SYSTEM.ps1
# 2-3 dakika bekle...
# Sonra futures'ı başlat
```

### Sorun 3: "No module named 'streamlit'"

Dependencies tekrar yükleyin:
```powershell
pip install -r requirements.txt --force-reinstall
```

### Sorun 4: "Port already in use"

Tüm streamlit'leri kapatın:
```powershell
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Sorun 5: Dashboard boş görünüyor

Normal! İlk pozisyon açılana kadar bekleyin (5-10 dakika).
"Auto-refresh" açık olduğu için otomatik güncellenecek.

---

## 📞 Yardım

Sorun devam ederse:

1. Tüm terminalleri kapatın
2. PowerShell'i yeniden başlatın
3. Adım 1'den tekrar başlayın

---

**İyi tradeler! 🚀💰**

*Son güncelleme: 2025-11-07*
