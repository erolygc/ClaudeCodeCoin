@echo off
echo ========================================
echo ClaudeCodeCoin - Auto Trading System
echo ========================================
echo.
echo Sistem baslatiliyor...
echo.

cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the trading system
python start_trading_system_windows.py --top 50

pause
