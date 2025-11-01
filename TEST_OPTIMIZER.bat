@echo off
echo ======================================================================
echo 🎯 ClaudeCodeCoin - Strategy Optimizer Test
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

echo [INFO] Running strategy optimizer...
echo.
echo This will:
echo   1. Test RSI strategy with different parameters
echo   2. Compare RSI, MACD, and Bollinger Bands strategies
echo   3. Find the best performing strategy
echo.

python Phase2_AlphaEngine\strategies\optimizer.py

echo.
echo ======================================================================
echo Optimization Complete!
echo ======================================================================
pause
