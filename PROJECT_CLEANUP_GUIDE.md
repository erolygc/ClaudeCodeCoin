# 🧹 ClaudeCodeCoin - Proje Temizlik Rehberi

## 📋 Hızlı Başlangıç

### Windows PowerShell:
```powershell
# Önce test modu (silmez, sadece gösterir)
.\CLEANUP_PROJECT.ps1 -DryRun

# Gerçek temizlik
.\CLEANUP_PROJECT.ps1

# Derin temizlik (backup'lar dahil)
.\CLEANUP_PROJECT.ps1 -Deep
```

### Linux/Mac:
```bash
# Manuel temizlik
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -name "*.log" -mtime +7 -delete
```

---

## 🎯 Ne Temizleniyor?

### 1. ✅ Otomatik Temizlenir
- **Python Cache**: `__pycache__/`, `*.pyc`
- **Eski Loglar**: 7 günden eski `*.log` dosyaları
- **Eski Pump Alerts**: Bugünkü hariç
- **Geçici DB**: `*.db.bak`, `*.db-journal`
- **Windows Dosyaları**: `Thumbs.db`, `desktop.ini`
- **Boş Klasörler**: İçi boş dizinler

### 2. ⚠️ Sadece Deep Mode ile Silinir
- **Backup Klasörleri**: `backup_old_data/`, `backup*/`

### 3. ❌ Asla Silinmez (Korunur)
- **Aktif Veritabanları**: `binance_data.db`, `futures_trading.db`
- **Bugünkü Pump Alerts**: `pump_alerts_YYYYMMDD.json`
- **Config Dosyaları**: `*.py`, `.env`
- **Kaynak Kod**: Tüm Python dosyaları

---

## 🗂️ .gitignore Güncellemeleri

`.gitignore` dosyası şu öğeleri repoda tutmaz:

### ❌ Git'e Gönderilmeyecekler:
```
# Database dosyaları
*.db
*.sqlite

# Log dosyaları
logs/
*.log

# Pump alerts
pump_alerts/*.json

# Backup klasörleri
backup*/

# Test dosyaları (root)
/test_*.py
/TEST_*.py

# Python cache
__pycache__/
*.pyc
```

### ✅ Git'e Gönderilecekler:
```
# Kaynak kod
*.py (kod dosyaları)

# Config templates
.env.example
config_*.py

# Documentation
*.md
README.md

# Startup scripts
*.ps1
*.sh
```

---

## 📦 Kullanılmayan Phase'ler

Detaylar için: [UNUSED_PHASES.md](UNUSED_PHASES.md)

**Kullanılmayan ama korunan:**
- `Phase2_AlphaEngine/` (69KB)
- `Phase3_RiskManagement/` (13KB)
- `Phase4_OrderExecution/` (11KB)
- `Phase5_Analytics/` (24KB)

**Toplam**: ~117KB (çok az, silinmese de olur)

**Tavsiye**: Şimdilik saklayın, gelecekte kullanabilirsiniz.

---

## 🔄 Git'ten Visual Studio Code'a Temiz Clone

### Adım 1: Fresh Clone
```bash
# Yeni bir klasöre clone
git clone https://github.com/erolygc/ClaudeCodeCoin.git ClaudeCodeCoin-Fresh
cd ClaudeCodeCoin-Fresh
```

### Adım 2: Otomatik Temizlik
```powershell
# Windows
.\CLEANUP_PROJECT.ps1

# Linux/Mac
chmod +x CLEANUP_PROJECT.sh
./CLEANUP_PROJECT.sh
```

### Adım 3: VS Code'da Aç
```bash
code .
```

**VS Code otomatik olarak şunları ignore eder:**
- `.gitignore` dosyasındaki her şey
- `__pycache__/` klasörleri
- `*.pyc` dosyaları
- `.venv/` sanal ortamı

---

## 📊 Disk Kullanımı Analizi

### Önce (Temizlik öncesi):
```
Project Total: ~500 MB
├── data_output/      280 MB (database)
├── venv/             150 MB (python packages)
├── logs/             30 MB  (eski loglar)
├── backup_old_data/  20 MB  (yedekler)
├── pump_alerts/      15 MB  (eski alerts)
└── source code/      5 MB   (kod)
```

### Sonra (Temizlik sonrası):
```
Project Total: ~435 MB (-65 MB)
├── data_output/      280 MB (database) ✅
├── venv/             150 MB (packages) ✅
├── source code/      5 MB   (kod) ✅
├── logs/             0 MB   (temizlendi) 🧹
├── backup_old_data/  0 MB   (silindi) 🧹
└── pump_alerts/      <1 MB  (bugünkü) 🧹
```

---

## 🛡️ Güvenli Temizlik Kontrol Listesi

Temizlik yapmadan önce:

- [ ] **Sistemleri durdurun**: Tüm Python processlerini kapatın
- [ ] **Önemli verileri yedekleyin**: Database'leri başka yere kopyalayın
- [ ] **Git commit yapın**: Son değişiklikleri commit edin
- [ ] **DryRun yapın**: `.\CLEANUP_PROJECT.ps1 -DryRun`
- [ ] **Sonuçları kontrol edin**: Nelerin silineceğini görün

Temizlik sonrası:

- [ ] **Sistemi test edin**: `.\START_SYSTEM.ps1` çalışıyor mu?
- [ ] **Database kontrol edin**: Veriler kaybolmadı mı?
- [ ] **Logs kontrol edin**: Yeni loglar oluşuyor mu?

---

## 🔧 Manuel Temizlik Komutları

### Windows PowerShell:

```powershell
# Python cache temizle
Get-ChildItem -Recurse __pycache__ | Remove-Item -Recurse -Force

# Eski logları sil (7 günden eski)
$sevenDaysAgo = (Get-Date).AddDays(-7)
Get-ChildItem -Recurse *.log | Where-Object { $_.LastWriteTime -lt $sevenDaysAgo } | Remove-Item

# Backup klasörlerini sil
Remove-Item -Recurse -Force backup*

# Eski pump alerts
$today = Get-Date -Format "yyyyMMdd"
Get-ChildItem pump_alerts\*.json | Where-Object { $_.Name -notmatch $today } | Remove-Item
```

### Linux/Mac Bash:

```bash
# Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Eski loglar (7 gün)
find . -name "*.log" -mtime +7 -delete

# Backup klasörleri
rm -rf backup*/

# Eski pump alerts
today=$(date +%Y%m%d)
find pump_alerts -name "*.json" ! -name "*$today*" -delete
```

---

## 📁 Temiz Proje Yapısı

Temizlik sonrası ideal yapı:

```
ClaudeCodeCoin/
├── Phase1_DataBackbone/       # ✅ Aktif
│   └── collectors/
├── Phase6_PumpDetection/      # ✅ Aktif
│   └── realtime_pump_scanner.py
├── Phase7_PaperTrading/       # ⚠️ Legacy
│   └── paper_trading_engine.py
├── Phase8_FuturesTrading/     # ✅ Aktif (Ana)
│   ├── config_futures.py
│   ├── futures_trading_engine.py
│   └── futures_dashboard.py
├── data_output/               # ✅ Veritabanı
│   └── binance_data.db
├── pump_alerts/               # ✅ Bugünkü alerts
│   └── pump_alerts_20251107.json
├── .env                       # ✅ Gizli
├── .gitignore                 # ✅ Güncel
├── requirements.txt           # ✅ Dependencies
├── START_SYSTEM.ps1           # ✅ Başlatma
├── START_FUTURES_SYSTEM.ps1   # ✅ Futures başlatma
└── CLEANUP_PROJECT.ps1        # ✅ Temizlik scripti
```

**Silinmiş/Ignore edilen:**
- ❌ `__pycache__/` klasörleri
- ❌ `*.pyc` dosyaları
- ❌ `logs/*.log` (eski loglar)
- ❌ `backup_old_data/`
- ❌ Eski pump alerts
- ❌ Test dosyaları (root)

---

## 🚀 VS Code İçin Öneriler

### Önerilen Eklentiler:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "donjayamanne.githistory",
    "eamodio.gitlens",
    "gruntfuggly.todo-tree"
  ]
}
```

### workspace settings.json:
```json
{
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/backup*": true,
    "**/*.log": true
  },
  "search.exclude": {
    "**/venv": true,
    "**/node_modules": true,
    "**/*.db": true
  }
}
```

---

## ❓ Sık Sorulan Sorular

### 1. "Backup klasörleri silinmeli mi?"
**Cevap**: Eğer veritabanı yedekleriniz başka yerde varsa, evet silebilirsiniz. `-Deep` parametresi kullanın.

### 2. "Test dosyalarını silebilir miyim?"
**Cevap**: Root'taki `test_*.py` dosyaları silinebilir. `tests/` klasöründekiler korunmalı.

### 3. "Phase2-5'i silsem sorun olur mu?"
**Cevap**: Hayır, şu an kullanılmıyorlar. Ama gelecekte lazım olabilir, şimdilik saklayın.

### 4. "Veritabanı dosyaları neden ignore ediliyor?"
**Cevap**: Çok büyük (280MB) ve kişisel trading verileri içeriyor. GitHub'a yüklenmesin.

### 5. "Temizlik sonrası sistem çalışmıyor!"
**Cevap**:
- Veritabanını silmediyseniz sorun yok
- `data_output/binance_data.db` var mı kontrol edin
- Sistemleri yeniden başlatın

---

## 📞 Yardım

Sorun olursa:
1. `.\CLEANUP_PROJECT.ps1 -DryRun` çalıştırın
2. `.gitignore` dosyasını kontrol edin
3. `git status` ile değişiklikleri görün
4. Issue açın: https://github.com/erolygc/ClaudeCodeCoin/issues

---

*Son güncelleme: 2025-11-07*
