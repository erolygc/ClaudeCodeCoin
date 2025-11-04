@echo off
cls
echo ============================================================
echo  CLAUDECODECOIN - 1000 COIN SYSTEM
echo  STARTING ALL DATA COLLECTORS
echo ============================================================
echo.
echo This system will monitor 1,100 coins:
echo   - Binance:  550 coins (5 instances)
echo   - Gate.io:  550 coins (1 instance)
echo.
echo PRODUCTION MODE FILTERS:
echo   - Min Confidence: 70%%
echo   - Min Volume Spike: 800%%
echo   - High accuracy, quality signals only
echo.
echo ============================================================
echo.
echo This will open 6 windows:
echo   [1] Binance Instance 1 - Top 100 Coins
echo   [2] Binance Instance 2 - Meme + Layer 2
echo   [3] Binance Instance 3 - AI + Gaming + DeFi
echo   [4] Binance Instance 4 - Mid-Cap Altcoins
echo   [5] Binance Instance 5 - Small Cap + Experimental
echo   [6] Gate.io Collector  - All 550 Coins
echo.
echo Press any key to start...
pause >nul
echo.
echo Starting collectors...
echo.

start "Binance Instance 1" cmd /k START_BINANCE_COLLECTOR_INSTANCE_1.bat
echo [1/6] Binance Instance 1 started...
timeout /t 3 /nobreak >nul

start "Binance Instance 2" cmd /k START_BINANCE_COLLECTOR_INSTANCE_2.bat
echo [2/6] Binance Instance 2 started...
timeout /t 3 /nobreak >nul

start "Binance Instance 3" cmd /k START_BINANCE_COLLECTOR_INSTANCE_3.bat
echo [3/6] Binance Instance 3 started...
timeout /t 3 /nobreak >nul

start "Binance Instance 4" cmd /k START_BINANCE_COLLECTOR_INSTANCE_4.bat
echo [4/6] Binance Instance 4 started...
timeout /t 3 /nobreak >nul

start "Binance Instance 5" cmd /k START_BINANCE_COLLECTOR_INSTANCE_5.bat
echo [5/6] Binance Instance 5 started...
timeout /t 3 /nobreak >nul

start "Gate.io Collector" cmd /k START_GATEIO_COLLECTOR_1000COINS.bat
echo [6/6] Gate.io Collector started...
echo.
echo ============================================================
echo  ALL COLLECTORS STARTED!
echo ============================================================
echo.
echo Check each window for connection status.
echo All collectors should show "Connected" and start receiving data.
echo.
echo Database: data_output\binance_data.db
echo Logs: logs\
echo.
echo Press any key to exit...
pause >nul
