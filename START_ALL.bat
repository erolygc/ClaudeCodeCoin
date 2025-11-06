@echo off
REM ClaudeCodeCoin - Master Launcher (Windows)
REM Tum sistemi tek komutla baslatir

echo ================================================================================
echo                    CLAUDECODECOIN - MASTER LAUNCHER
echo ================================================================================
echo.
echo Tum sistem baslatiliyor...
echo   [1] Gate.io Data Collector (550 coins)
echo   [2] Realtime Pump Scanner
echo   [3] Paper Trading Engine
echo.
echo Her component ayri bir pencerede acilacak.
echo Durdurmak icin her pencerede Ctrl+C basin.
echo ================================================================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python bulunamadi! Lutfen Python yukleyin.
    pause
    exit /b 1
)

REM Gerekli paketleri kontrol et
echo [CHECK] Python paketleri kontrol ediliyor...
python -c "import websockets, gate_api" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Bazi paketler eksik olabilir. Yukleniyor...
    pip install websockets gate-api loguru python-dotenv >nul 2>&1
)

REM 1. Gate.io Collector'i yeni pencerede baslat
echo [1/3] Gate.io Collector baslatiliyor...
start "Gate.io Collector - 550 Coins" cmd /k "python Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py"
timeout /t 3 /nobreak >nul

REM 2. Pump Scanner'i yeni pencerede baslat
echo [2/3] Pump Scanner baslatiliyor...
start "Pump Scanner - Real-time" cmd /k "python Phase6_PumpDetection/realtime_pump_scanner.py"
timeout /t 3 /nobreak >nul

REM 3. Paper Trading'i yeni pencerede baslat
echo [3/3] Paper Trading baslatiliyor...
start "Paper Trading Engine" cmd /k "python Phase7_PaperTrading/paper_trading_engine.py"
timeout /t 2 /nobreak >nul

echo.
echo ================================================================================
echo [SUCCESS] Tum componentler baslatildi!
echo ================================================================================
echo.
echo 3 yeni pencere acildi:
echo   - Gate.io Collector (550 coins veri toplama)
echo   - Pump Scanner (Pump tespit sistemi)
echo   - Paper Trading (Sanal trading motoru)
echo.
echo Her pencereyi kapatmak icin Ctrl+C + Y kullanin.
echo.
echo Sistem saglik kontrolu icin: python SYSTEM_HEALTH_CHECK.py
echo ================================================================================
echo.
pause
