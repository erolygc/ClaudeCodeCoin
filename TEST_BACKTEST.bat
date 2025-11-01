@echo off
echo ======================================================================
echo 🎯 ClaudeCodeCoin - Backtesting Test
echo ======================================================================
echo.

REM Check venv
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

echo [INFO] Testing backtesting engine...
echo.

python Phase2_AlphaEngine\backtesting\backtester.py

echo.
echo ======================================================================
echo Test Complete!
echo ======================================================================
pause
