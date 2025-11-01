@echo off
echo ======================================================================
echo 📊 ClaudeCodeCoin - Quick Data Collection (1 Hour)
echo ======================================================================
echo.
echo This script will collect data for 1 hour to get ~60 bars
echo (minimum for basic backtesting with 14-period indicators)
echo.
echo Both Binance and Gate.io collectors will run simultaneously.
echo.
echo IMPORTANT: Keep this window open for at least 1 hour!
echo You can stop anytime with Ctrl+C
echo.
echo ======================================================================
echo.

set START_TIME=%TIME%
echo Started at: %START_TIME%
echo Target duration: 1 hour (3600 seconds)
echo.
echo Press Ctrl+C to stop early, or close this window when done.
echo.

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Run both collectors in background
echo Starting Binance collector...
start /B cmd /c "python Phase1_DataBackbone/collectors/standalone_binance_collector.py > logs/binance_collector.log 2>&1"

echo Starting Gate.io collector...
start /B cmd /c "python Phase1_DataBackbone/collectors/standalone_gateio_collector.py > logs/gateio_collector.log 2>&1"

echo.
echo ✅ Both collectors started!
echo.
echo Monitor progress:
echo   - Check logs/ folder for collector outputs
echo   - Run CHECK_DATA_STATUS.bat to see bar counts
echo.
echo Collecting data for 1 hour...
echo (You can stop anytime with Ctrl+C)
echo.

REM Wait for 1 hour (3600 seconds)
timeout /t 3600 /nobreak

echo.
echo ======================================================================
echo Data collection completed!
echo ======================================================================
echo.
echo Run CHECK_DATA_STATUS.bat to see how much data was collected.
echo Then run TEST_OPTIMIZER_GATEIO.bat to test optimization.
echo.
pause
