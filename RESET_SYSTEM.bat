@echo off
chcp 65001 >nul
title ClaudeCodeCoin - System Reset

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║        ClaudeCodeCoin - Sistemi Sıfırla                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo UYARI: Bu işlem tüm trading geçmişini silecek!
echo.
echo Silinecek veriler:
echo   - Tüm açık ve kapalı pozisyonlar
echo   - Bakiye geçmişi (10,000 USD'ye dönecek)
echo   - Pump alert dosyaları
echo   - Log dosyaları
echo   - Performans metrikleri
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

set /p confirm="Devam etmek istediğinizden emin misiniz? (E/H): "
if /i not "%confirm%"=="E" (
    echo.
    echo İşlem iptal edildi.
    pause
    exit /b
)

echo.
echo [1/6] Çalışan süreçler durduruluyor...
taskkill /F /FI "WINDOWTITLE eq *ClaudeCodeCoin*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Dashboard*" >nul 2>&1
timeout /t 2 >nul

echo [2/6] Veritabanları temizleniyor...
if exist "Phase7_PaperTrading\data_output\paper_trading.db" (
    del /F /Q "Phase7_PaperTrading\data_output\paper_trading.db"
    echo    ✓ Paper trading database silindi
)

if exist "Phase8_FuturesTrading\data_output\paper_trading.db" (
    del /F /Q "Phase8_FuturesTrading\data_output\paper_trading.db"
    echo    ✓ Futures trading database silindi
)

if exist "paper_trading_performance.db" (
    del /F /Q "paper_trading_performance.db"
    echo    ✓ Performance database silindi
)

echo [3/6] Pump alerts temizleniyor...
if exist "pump_alerts\" (
    del /F /Q "pump_alerts\*.json" >nul 2>&1
    echo    ✓ Pump alerts silindi
)

echo [4/6] Log dosyaları temizleniyor...
if exist "logs\" (
    del /F /Q "logs\*.log" >nul 2>&1
    echo    ✓ Log dosyaları silindi
)

echo [5/6] Signal dosyaları temizleniyor...
if exist "Phase6_PumpDetection\signals\" (
    del /F /Q "Phase6_PumpDetection\signals\*.json" >nul 2>&1
    echo    ✓ Signal dosyaları silindi
)

echo [6/6] Gerekli klasörler yeniden oluşturuluyor...
if not exist "Phase7_PaperTrading\data_output" mkdir "Phase7_PaperTrading\data_output"
if not exist "Phase8_FuturesTrading\data_output" mkdir "Phase8_FuturesTrading\data_output"
if not exist "logs" mkdir "logs"
if not exist "pump_alerts" mkdir "pump_alerts"
if not exist "Phase6_PumpDetection\signals" mkdir "Phase6_PumpDetection\signals"
echo    ✓ Klasörler oluşturuldu

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  ✅ SİSTEM SIFIRLANDI                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Sistem temiz durumda. Şimdi:
echo   1. START_AUTO_TRADING_SIMPLE.bat ile sistemi başlatın
echo   2. Veya manuel olarak bileşenleri başlatın
echo.

pause
