@echo off
title ClaudeCodeCoin - Master Controller
echo ================================================================================
echo  CLAUDECODECOIN - AUTOMATED TRADING SYSTEM (MULTI-WINDOW)
echo ================================================================================
echo.
echo Starting all components in separate windows...
echo.

REM Start Hybrid Scanner in new window
echo Starting Hybrid Scanner...
start "Hybrid Scanner" cmd /k run_scanner.bat

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Start Paper Trading Engine in new window
echo Starting Paper Trading Engine...
start "Paper Trading Engine" cmd /k run_trading_engine.bat

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Start Trading Dashboard in new window
echo Starting Trading Dashboard...
start "Trading Dashboard" cmd /k run_dashboard.bat

REM Wait 3 seconds for dashboard to initialize
timeout /t 3 /nobreak >nul

REM Open dashboard in browser
echo Opening dashboard in browser...
start http://localhost:8501

echo.
echo ================================================================================
echo  ALL SYSTEMS STARTED IN SEPARATE WINDOWS
echo ================================================================================
echo.
echo You should now see:
echo   1. Window: Hybrid Scanner
echo   2. Window: Paper Trading Engine
echo   3. Window: Trading Dashboard (Streamlit)
echo   4. Browser: Dashboard at http://localhost:8501
echo.
echo Monitor:
echo   - Logs: logs\
echo   - Signals: Phase6_PumpDetection\signals\
echo   - Performance: paper_trading_performance.db
echo.
echo To stop the system:
echo   - Close each window manually
echo   - Or press Ctrl+C in each window
echo.
echo ================================================================================
echo.
echo Press any key to show log monitoring options...
pause >nul

echo.
echo ================================================================================
echo  LOG MONITORING OPTIONS
echo ================================================================================
echo.
echo Option 1: Watch Trading Logs (PowerShell)
echo   .\watch_logs.ps1 logs\paper_trading.log
echo.
echo Option 2: Watch Scanner Logs (PowerShell)
echo   .\watch_logs.ps1 logs\realtime_hybrid_scanner.log
echo.
echo Option 3: Manual tail (PowerShell)
echo   Get-Content logs\paper_trading.log -Wait -Tail 20
echo.
echo Option 4: View signals
echo   dir Phase6_PumpDetection\signals\
echo.
echo Option 5: Query database
echo   sqlite3 paper_trading_performance.db "SELECT * FROM positions LIMIT 5"
echo.
echo ================================================================================
echo.
echo Press any key to exit this window...
pause >nul
