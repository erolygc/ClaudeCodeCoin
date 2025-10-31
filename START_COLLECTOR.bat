@echo off
REM ClaudeCodeCoin - Standalone Collector Starter (Windows)
REM Docker olmadan veri toplamak için

echo ======================================================================
echo      ClaudeCodeCoin - Binance Veri Toplayici (Docker'siz)
echo ======================================================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [HATA] Virtual environment bulunamadi!
    echo.
    echo Lutfen once kurulum yapin:
    echo   1. python -m venv venv
    echo   2. venv\Scripts\activate
    echo   3. pip install -r requirements-minimal.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Virtual environment aktive ediliyor...
call venv\Scripts\activate.bat

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    pause
    exit /b 1
)

echo [OK] Python bulundu
echo.

REM Check if standalone_binance_collector.py exists
if not exist "Phase1_DataBackbone\collectors\standalone_binance_collector.py" (
    echo [HATA] Collector script bulunamadi!
    echo.
    echo Git pull yapin:
    echo   git pull origin claude/crypto-quant-fund-architecture-011CUez7v2mujBBJSFQkeihx
    echo.
    pause
    exit /b 1
)

echo [INFO] Veri toplayici baslatiliyor...
echo [INFO] Durdurmak icin: Ctrl+C
echo.
echo ======================================================================
echo.

REM Run the collector
python Phase1_DataBackbone\collectors\standalone_binance_collector.py

echo.
echo ======================================================================
echo [INFO] Toplayici durduruldu
echo ======================================================================
echo.

pause
