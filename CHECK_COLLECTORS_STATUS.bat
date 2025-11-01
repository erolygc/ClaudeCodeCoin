@echo off
echo ======================================================================
echo 🔍 ClaudeCodeCoin - Collector Status Check
echo ======================================================================
echo.

echo Checking for running collectors...
echo.

tasklist /FI "WINDOWTITLE eq standalone_binance_collector.py" 2>NUL | find /I "python" >NUL
if %ERRORLEVEL% EQU 0 (
    echo ✅ Binance collector is RUNNING
) else (
    echo ❌ Binance collector is NOT running
)

tasklist /FI "WINDOWTITLE eq standalone_gateio_collector.py" 2>NUL | find /I "python" >NUL
if %ERRORLEVEL% EQU 0 (
    echo ✅ Gate.io collector is RUNNING
) else (
    echo ❌ Gate.io collector is NOT running
)

echo.
echo Alternative check (all Python processes):
tasklist /FI "IMAGENAME eq python.exe" | find /I "python"

echo.
echo ======================================================================
pause
