@echo off
REM ClaudeCodeCoin - Gate.io Only Collector
REM Sadece Gate.io'dan 550 coin için veri toplar

title ClaudeCodeCoin - Gate.io Collector

echo ======================================================================
echo 🚀 ClaudeCodeCoin - Gate.io Data Collector
echo ======================================================================
echo.
echo 📊 Gate.io'dan 550 coin için veri toplama başlatılıyor...
echo.
echo Özellikler:
echo   ✓ 550 USDT trading pairs
echo   ✓ 1 dakikalık candlestick verisi
echo   ✓ SQLite database
echo   ✓ Otomatik reconnect
echo.
echo ======================================================================
echo.

REM Gerekli dizinleri oluştur
if not exist data_output mkdir data_output
if not exist logs mkdir logs
if not exist pump_alerts mkdir pump_alerts

REM Python paketi kontrolü
echo 📦 Python paketleri kontrol ediliyor...

python -c "import websockets" 2>nul
if errorlevel 1 (
    echo ⚠️  websockets paketi yüklü değil, yükleniyor...
    pip install -q websockets
)

python -c "import sqlite3" 2>nul
if errorlevel 1 (
    echo ❌ SQLite3 modülü bulunamadı!
    pause
    exit /b 1
)

echo ✅ Tüm paketler hazır
echo.

REM Gate.io collector'ı başlat
echo 🟢 Gate.io Collector başlatılıyor...
echo.
echo ⏹️  Durdurmak için: Ctrl+C
echo 📊 Log dosyası: logs\gateio_collector_1000coins.log
echo 💾 Database: data_output\binance_data.db
echo.
echo ======================================================================
echo.

python Phase1_DataBackbone\collectors\multi_coin_gateio_collector_1000coins.py

echo.
echo ======================================================================
echo ⏹️  Gate.io Collector durduruldu
echo ======================================================================
echo.
pause
