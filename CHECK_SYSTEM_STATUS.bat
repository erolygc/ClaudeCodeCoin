@echo off
echo ======================================================================
echo 🔍 ClaudeCodeCoin - Sistem Durumu
echo ======================================================================
echo.

REM Python işlemlerini kontrol et
set PYTHON_RUNNING=0

tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_RUNNING=1
)

echo 📊 Sistem Bileşenleri:
echo.

REM 1. Binance Collector (Multi-Coin or Standalone)
wmic process where "commandline like '%%multi_coin_binance_collector%%' or commandline like '%%standalone_binance_collector%%'" get processid 2>nul | find /v "ProcessId" | find /v "" >nul
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Binance Collector       : ÇALIŞIYOR
) else (
    echo   ❌ Binance Collector       : DURDURULDU
)

REM 2. Gate.io Collector (Multi-Coin or Standalone)
wmic process where "commandline like '%%multi_coin_gateio_collector%%' or commandline like '%%standalone_gateio_collector%%'" get processid 2>nul | find /v "ProcessId" | find /v "" >nul
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Gate.io Collector       : ÇALIŞIYOR
) else (
    echo   ❌ Gate.io Collector       : DURDURULDU
)

REM 3. Pump Scanner
wmic process where "commandline like '%%realtime_pump_scanner%%'" get processid 2>nul | find /v "ProcessId" | find /v "" >nul
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Pump Scanner            : ÇALIŞIYOR
) else (
    echo   ❌ Pump Scanner            : DURDURULDU
)

REM 4. Dashboard
wmic process where "commandline like '%%streamlit%%' or commandline like '%%monitoring_dashboard%%'" get processid 2>nul | find /v "ProcessId" | find /v "" >nul
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Dashboard               : ÇALIŞIYOR
    echo      └── URL: http://localhost:8501
) else (
    echo   ❌ Dashboard               : DURDURULDU
)

echo.
echo ======================================================================
echo.

REM Veri durumu
if exist data_output\binance_data.db (
    echo 📁 Veritabanı              : ✅ Mevcut

    REM Veritabanı boyutu
    for %%A in (data_output\binance_data.db) do (
        set size=%%~zA
        set /a size_mb=!size! / 1048576
        echo    └── Boyut: %%~zA bytes
    )
) else (
    echo 📁 Veritabanı              : ❌ Bulunamadı
)

echo.

REM Alert klasörü
if exist pump_alerts (
    echo 🔔 Pump Alerts Klasörü     : ✅ Mevcut

    REM Alert dosya sayısı
    dir /b pump_alerts\*.json 2>nul | find /c /v "" > temp_count.txt
    set /p alert_count=<temp_count.txt
    del temp_count.txt >nul 2>&1
    echo    └── Alert dosyası: !alert_count! adet
) else (
    echo 🔔 Pump Alerts Klasörü     : ❌ Bulunamadı
)

echo.

REM Log klasörü
if exist logs (
    echo 📋 Logs Klasörü            : ✅ Mevcut

    REM Log dosya sayısı
    dir /b logs\*.log 2>nul | find /c /v "" > temp_count.txt
    set /p log_count=<temp_count.txt
    del temp_count.txt >nul 2>&1
    echo    └── Log dosyası: !log_count! adet
) else (
    echo 📋 Logs Klasörü            : ❌ Bulunamadı
)

echo.
echo ======================================================================
echo 💡 Hızlı Komutlar:
echo ======================================================================
echo.
echo   🚀 Tüm sistemleri başlat    : START_ALL_SYSTEMS.bat
echo   🛑 Tüm sistemleri durdur    : STOP_ALL_SYSTEMS.bat
echo   📊 Veri durumunu kontrol et : CHECK_DATA_STATUS.bat
echo   🔔 Pump alert'leri gör      : Dashboard ^> Pump Signals sekmesi
echo.

REM Genel durum özeti
echo ======================================================================
echo 📊 Genel Durum Özeti:
echo ======================================================================
echo.

set RUNNING_COUNT=0

wmic process where "commandline like '%%multi_coin_binance_collector%%' or commandline like '%%standalone_binance_collector%%'" get processid 2>nul | find /v "ProcessId" | find /v "" >nul
if %ERRORLEVEL% EQU 0 set /a RUNNING_COUNT+=1

wmic process where "commandline like '%%multi_coin_gateio_collector%%' or commandline like '%%standalone_gateio_collector%%'" get processid 2>nul | find /v "ProcessId" | find /v "" >nul
if %ERRORLEVEL% EQU 0 set /a RUNNING_COUNT+=1

wmic process where "commandline like '%%realtime_pump_scanner%%'" get processid 2>nul | find /v "ProcessId" | find /v "" >nul
if %ERRORLEVEL% EQU 0 set /a RUNNING_COUNT+=1

wmic process where "commandline like '%%streamlit%%'" get processid 2>nul | find /v "ProcessId" | find /v "" >nul
if %ERRORLEVEL% EQU 0 set /a RUNNING_COUNT+=1

if %RUNNING_COUNT% EQU 4 (
    echo   🟢 Tüm sistemler çalışıyor! (4/4)
    echo   └── Sistem tam kapasitede
) else if %RUNNING_COUNT% GTR 0 (
    echo   🟡 Bazı sistemler çalışıyor (%RUNNING_COUNT%/4)
    echo   └── Eksik bileşenler var
) else (
    echo   🔴 Hiçbir sistem çalışmıyor (0/4)
    echo   └── START_ALL_SYSTEMS.bat ile başlatın
)

echo.
echo ======================================================================
pause
