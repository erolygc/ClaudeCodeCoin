@echo off
echo ======================================================================
echo 🚀 ClaudeCodeCoin - Tüm Sistemleri Başlat
echo ======================================================================
echo.
echo Bu script tüm ClaudeCodeCoin bileşenlerini başlatacak:
echo.
echo   1️⃣  Binance Data Collector
echo   2️⃣  Gate.io Data Collector
echo   3️⃣  Real-Time Pump Scanner
echo   4️⃣  Monitoring Dashboard
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
echo 🚀 Sistemler Başlatılıyor...
echo ======================================================================
echo.

REM Gerekli klasörleri oluştur
if not exist logs mkdir logs
if not exist pump_alerts mkdir pump_alerts

REM 1. Binance Collector
echo 1️⃣  Binance Collector başlatılıyor...
start "ClaudeCodeCoin - Binance Collector" cmd /k "call venv\Scripts\activate && python Phase1_DataBackbone\collectors\standalone_binance_collector.py"
timeout /t 2 >nul

REM 2. Gate.io Collector
echo 2️⃣  Gate.io Collector başlatılıyor...
start "ClaudeCodeCoin - Gate.io Collector" cmd /k "call venv\Scripts\activate && python Phase1_DataBackbone\collectors\standalone_gateio_collector.py"
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
echo ✅ Tüm Sistemler Başlatıldı!
echo ======================================================================
echo.
echo 📊 Açılan Pencereler:
echo.
echo   ✅ Pencere 1: Binance Collector
echo      └── Binance'den gerçek zamanlı veri topluyor
echo.
echo   ✅ Pencere 2: Gate.io Collector
echo      └── Gate.io'dan gerçek zamanlı veri topluyor
echo.
echo   ✅ Pencere 3: Pump Scanner
echo      └── Her 60 saniyede tüm coinleri tarayıp pump tespit ediyor
echo.
echo   ✅ Pencere 4: Dashboard
echo      └── http://localhost:8501 adresinde açılacak
echo.
echo ======================================================================
echo.
echo 💡 İpuçları:
echo.
echo   📊 Dashboard'u görüntülemek için:
echo      http://localhost:8501
echo.
echo   🔍 Sistem durumunu kontrol etmek için:
echo      CHECK_SYSTEM_STATUS.bat
echo.
echo   📈 Veri durumunu kontrol etmek için:
echo      CHECK_DATA_STATUS.bat
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
pause
