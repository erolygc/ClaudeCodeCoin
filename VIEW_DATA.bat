@echo off
REM ClaudeCodeCoin - Data Viewer (Windows)
REM Toplanan veriyi görüntülemek için

echo ======================================================================
echo      ClaudeCodeCoin - Toplanan Veriyi Görüntüle
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
call venv\Scripts\activate.bat

REM Check if data exists
if not exist "data_output\binance_data.db" (
    echo [UYARI] Henuz veri toplanmamis!
    echo.
    echo Once veri toplayicisini calistirin:
    echo   START_COLLECTOR.bat
    echo.
    echo veya:
    echo   python Phase1_DataBackbone\collectors\standalone_binance_collector.py
    echo.
    pause
    exit /b 0
)

echo [INFO] Veri analizi yapiliyor...
echo.
echo ======================================================================
echo.

REM Run the viewer
python Phase1_DataBackbone\collectors\view_collected_data.py

echo.
echo ======================================================================
echo.

REM Ask for CSV export
set /p EXPORT="CSV raporu olusturmak ister misiniz? (y/n): "
if /i "%EXPORT%"=="y" (
    echo.
    echo [INFO] CSV raporu olusturuluyor...
    python Phase1_DataBackbone\collectors\view_collected_data.py --export
    echo.
)

echo ======================================================================
echo.
echo Dosya konumlari:
echo   - SQLite DB: data_output\binance_data.db
echo   - CSV dosyalar: data_output\csv\
echo.
echo Bu dosyalari Excel, Python veya SQLite Browser ile acabilirsiniz.
echo.
echo ======================================================================

pause
