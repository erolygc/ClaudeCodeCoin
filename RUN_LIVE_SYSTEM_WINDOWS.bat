@echo off
REM ClaudeCodeCoin - Live Trading System Runner (Windows)
REM UTF-8 encoding ile tüm bileşenleri başlatır

echo ================================================================================
echo CLAUDECODECOIN - LIVE TRADING SYSTEM (WINDOWS)
echo ================================================================================
echo.

REM UTF-8 encoding ayarla
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

echo Starting all components...
echo.
echo Components:
echo   1. Gate.io Data Collector (550 coins)
echo   2. Pump Scanner (Real-time detection)
echo   3. Paper Trading Engine (Virtual money)
echo.
echo ================================================================================
echo.

REM Klasörleri oluştur
if not exist "data_output" mkdir data_output
if not exist "logs" mkdir logs
if not exist "pump_alerts" mkdir pump_alerts

echo How to run:
echo   [1] All in one window (sequential logs)
echo   [2] Separate windows (3 cmd windows)
echo.
set /p OPTION="Select option [1-2]: "

if "%OPTION%"=="1" goto SINGLE_WINDOW
if "%OPTION%"=="2" goto MULTI_WINDOW

echo Invalid option. Exiting.
pause
exit /b 1

:SINGLE_WINDOW
echo.
echo Running in single window mode...
echo Note: Components will run sequentially. Press Ctrl+C to stop all.
echo.

REM 1. Collector'ı başlat (background)
echo [1/3] Starting Gate.io Collector...
start /B python run_live_gateio_collector.py
timeout /t 5 /nobreak > nul

REM 2. Pump Scanner'ı başlat (background)
echo [2/3] Starting Pump Scanner...
start /B python run_live_pump_scanner.py
timeout /t 5 /nobreak > nul

REM 3. Paper Trading'i başlat (foreground)
echo [3/3] Starting Paper Trading Engine...
python run_live_paper_trading.py

goto END

:MULTI_WINDOW
echo.
echo Opening 3 separate windows...
echo.

REM 1. Data Collector Window
echo [1/3] Opening Gate.io Collector window...
start "ClaudeCodeCoin - Data Collector" cmd /k "chcp 65001 > nul && set PYTHONIOENCODING=utf-8 && python run_live_gateio_collector.py"
timeout /t 2 /nobreak > nul

REM 2. Pump Scanner Window
echo [2/3] Opening Pump Scanner window...
start "ClaudeCodeCoin - Pump Scanner" cmd /k "chcp 65001 > nul && set PYTHONIOENCODING=utf-8 && python run_live_pump_scanner.py"
timeout /t 2 /nobreak > nul

REM 3. Paper Trading Window
echo [3/3] Opening Paper Trading window...
start "ClaudeCodeCoin - Paper Trading" cmd /k "chcp 65001 > nul && set PYTHONIOENCODING=utf-8 && python run_live_paper_trading.py"

echo.
echo ================================================================================
echo 3 WINDOWS OPENED
echo ================================================================================
echo.
echo Close each window to stop components
echo Or close this window to keep them running
echo.

goto END

:END
echo.
echo Done!
pause
