@echo off
echo ======================================================================
echo 🛑 ClaudeCodeCoin - Tüm Sistemleri Durdur
echo ======================================================================
echo.
echo Çalışan tüm ClaudeCodeCoin bileşenleri durduruluyor...
echo.

REM Python işlemlerini bul ve durdur
echo 🔍 Python işlemleri aranıyor...
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul

if %ERRORLEVEL% EQU 0 (
    echo ✅ Python işlemleri bulundu, durduruluyor...

    REM Collectors
    wmic process where "commandline like '%%standalone_binance_collector%%'" delete 2>nul
    wmic process where "commandline like '%%standalone_gateio_collector%%'" delete 2>nul

    REM Pump Scanner
    wmic process where "commandline like '%%realtime_pump_scanner%%'" delete 2>nul

    REM Dashboard
    wmic process where "commandline like '%%monitoring_dashboard%%'" delete 2>nul
    wmic process where "commandline like '%%streamlit%%'" delete 2>nul

    echo ✅ Tüm ClaudeCodeCoin işlemleri durduruldu
) else (
    echo ℹ️  Çalışan Python işlemi bulunamadı
)

echo.
echo ======================================================================
echo Sistem Durumu Kontrol Ediliyor...
echo ======================================================================
echo.

REM Durum kontrolü
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul

if %ERRORLEVEL% EQU 0 (
    echo ⚠️  Bazı Python işlemleri hala çalışıyor olabilir
    echo.
    echo Çalışan Python işlemleri:
    tasklist /FI "IMAGENAME eq python.exe"
    echo.
    echo Manuel olarak durdurmak için Task Manager kullanın
) else (
    echo ✅ Tüm sistemler başarıyla durduruldu!
)

echo.
echo ======================================================================
echo İşlem Tamamlandı
echo ======================================================================
echo.
echo Sistemi yeniden başlatmak için: START_ALL_SYSTEMS.bat
echo.
pause
