@echo off
echo ============================================================
echo  STARTING ALL BINANCE COLLECTORS (1000 COIN SYSTEM)
echo  Total: 5 Instances for 550 Binance Coins
echo ============================================================
echo.
echo This will open 5 separate windows:
echo   Instance 1: Top 100 Coins
echo   Instance 2: Meme + Layer 2
echo   Instance 3: AI + Gaming + DeFi
echo   Instance 4: Mid-Cap Altcoins
echo   Instance 5: Small Cap + Experimental
echo.
echo Press any key to continue...
pause >nul

start "Binance Instance 1" cmd /k START_BINANCE_COLLECTOR_INSTANCE_1.bat
timeout /t 2 /nobreak >nul

start "Binance Instance 2" cmd /k START_BINANCE_COLLECTOR_INSTANCE_2.bat
timeout /t 2 /nobreak >nul

start "Binance Instance 3" cmd /k START_BINANCE_COLLECTOR_INSTANCE_3.bat
timeout /t 2 /nobreak >nul

start "Binance Instance 4" cmd /k START_BINANCE_COLLECTOR_INSTANCE_4.bat
timeout /t 2 /nobreak >nul

start "Binance Instance 5" cmd /k START_BINANCE_COLLECTOR_INSTANCE_5.bat

echo.
echo ============================================================
echo  ALL INSTANCES STARTED!
echo  Check each window for status
echo ============================================================
echo.
echo Press any key to exit...
pause >nul
