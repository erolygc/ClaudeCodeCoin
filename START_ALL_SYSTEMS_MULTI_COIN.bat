@echo off
echo ======================================================================
echo 🚀 ClaudeCodeCoin - Tüm Sistemleri Başlat (MULTI-COIN)
echo ======================================================================
echo.
echo Bu script 186 COIN için tüm bileşenleri başlatacak:
echo.
echo   1️⃣  Binance Multi-Coin Collector (94 coins)
echo   2️⃣  Gate.io Multi-Coin Collector (92 coins)
echo   3️⃣  Real-Time Pump Scanner
echo   4️⃣  Monitoring Dashboard
echo.
echo TOPLAM: 186 Cryptocurrency izlenecek!
echo.
echo Her bileşen ayrı bir pencerede açılacak.
echo.
echo ======================================================================
echo.

REM Önce mevcut işlemleri kontrol et
echo 🔍 Mevcut durum kontrol ediliyor...
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ⚠️  UYARI: Python işlemleri zaten çalışıyor!
    echo.
    choice /C YN /M "Mevcut işlemleri durdurup yeniden başlatmak ister misiniz?"

    if errorlevel 2 (
        echo.
        echo ❌ İşlem iptal edildi
        pause
        exit /b
    )

    echo.
    echo 🛑 Mevcut işlemler durduruluyor...
    call STOP_ALL_SYSTEMS.bat
    timeout /t 3 >nul
)

echo.
echo ======================================================================
echo 🚀 Sistemler Başlatılıyor (MULTI-COIN MODE)...
echo ======================================================================
echo.

REM Gerekli klasörleri oluştur
if not exist logs mkdir logs
if not exist pump_alerts mkdir pump_alerts
if not exist config mkdir config

REM Config dosyasını kontrol et
if not exist config\trading_pairs.py (
    echo ⚠️  config\trading_pairs.py bulunamadı!
    echo.
    echo Git pull yapın:
    echo git pull origin claude/crypto-quant-fund-architecture-011CUez7v2mujBBJSFQkeihx
    echo.
    pause
    exit /b
)

REM 1. Binance Multi-Coin Collector
echo 1️⃣  Binance Multi-Coin Collector başlatılıyor (94 coins)...
start "ClaudeCodeCoin - Binance Multi-Coin Collector" cmd /k "call venv\Scripts\activate && python Phase1_DataBackbone\collectors\multi_coin_binance_collector.py"
timeout /t 2 >nul

REM 2. Gate.io Multi-Coin Collector
echo 2️⃣  Gate.io Multi-Coin Collector başlatılıyor (92 coins)...
start "ClaudeCodeCoin - Gate.io Multi-Coin Collector" cmd /k "call venv\Scripts\activate && python Phase1_DataBackbone\collectors\multi_coin_gateio_collector.py"
timeout /t 2 >nul

REM 3. Pump Scanner
echo 3️⃣  Pump Scanner başlatılıyor...
start "ClaudeCodeCoin - Pump Scanner" cmd /k "call venv\Scripts\activate && python Phase6_PumpDetection\realtime_pump_scanner.py"
timeout /t 2 >nul

REM 4. Dashboard
echo 4️⃣  Dashboard başlatılıyor...
echo    (Browser'da http://localhost:8501 açılacak)
start "ClaudeCodeCoin - Dashboard" cmd /k "call venv\Scripts\activate && streamlit run Dashboard\monitoring_dashboard.py"
timeout /t 3 >nul

echo.
echo ======================================================================
echo ✅ Tüm Sistemler Başlatıldı! (MULTI-COIN MODE)
echo ======================================================================
echo.
echo 📊 Açılan Pencereler:
echo.
echo   ✅ Pencere 1: Binance Multi-Coin Collector
echo      └── 94 USDT pairs (BTC, ETH, SOL, SHIB, PEPE, MEME, WIF, AI tokens, DeFi, Gaming, etc.)
echo.
echo   ✅ Pencere 2: Gate.io Multi-Coin Collector
echo      └── 92 USDT pairs (BTC, ETH, SOL, meme coins, DeFi, Gaming, L2, AI, etc.)
echo.
echo   ✅ Pencere 3: Pump Scanner
echo      └── 186 coin taranıyor, pump detection aktif
echo.
echo   ✅ Pencere 4: Dashboard
echo      └── http://localhost:8501 adresinde açılacak
echo.
echo ======================================================================
echo.
echo 💡 İpuçları:
echo.
echo   📊 Toplam coin sayısı: 186 cryptocurrency
echo.
echo   🔥 Yüksek pump potansiyeli (36 öncelikli coin):
echo      - Meme coins: SHIB, PEPE, FLOKI, BONK, WIF, MEME
echo      - New L1/L2: ARB, OP, SUI, SEI, TIA, APT
echo      - AI tokens: WLD, FET, AGIX, ARKM, RENDER
echo      - Gaming: GALA, SAND, AXS, APE, GMT, BLUR
echo      - DeFi: YFI, 1INCH, SUSHI, CRV
echo      - Low cap gems: JASMY, ONE, CKB, HOT, IOTX
echo.
echo   📈 Veri toplama:
echo      - İlk 30 dakika: Veri birikiyor
echo      - 1 saat sonra: Pump detection aktif
echo      - 6 saat sonra: Çok güvenilir analiz
echo.
echo   🔍 Pump Scanner:
echo      - Her 60 saniyede TÜM coinleri tarar
echo      - High pump potential coinlere öncelik verir
echo      - Alert'ler pump_alerts/ klasörüne kaydedilir
echo.
echo   📊 Dashboard'da görmek için:
echo      http://localhost:8501
echo.
echo   🛑 Tüm sistemleri durdurmak için:
echo      STOP_ALL_SYSTEMS.bat
echo.
echo   ⚠️  NOT: Pencereleri kapatmayın! Sistemler çalışmaya devam etsin.
echo.
echo ======================================================================
echo.
echo 🎯 Sistem 5 saniye içinde Dashboard'u açacak...
echo.
timeout /t 5 >nul

REM Browser'da Dashboard aç
start http://localhost:8501

echo.
echo ✅ Dashboard açıldı!
echo.
echo Bu pencereyi kapatabilirsiniz.
echo Sistemler arka planda çalışmaya devam edecek.
echo.
echo ======================================================================
echo 🔥 186 COIN İZLENİYOR - PUMP ALERT BEKLENİYOR!
echo ======================================================================
echo.
pause
