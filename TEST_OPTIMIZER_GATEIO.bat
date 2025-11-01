@echo off
echo ======================================================================
echo 🎯 ClaudeCodeCoin - Strategy Optimizer Test (Gate.io Data)
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

echo [INFO] Running strategy optimizer with Gate.io data...
echo.
echo Gate.io has MORE data - using BTC_USDT from gate.io exchange
echo.

python -c "from Phase2_AlphaEngine.strategies import StrategyOptimizer; opt = StrategyOptimizer(); print('\n=== RSI Optimization ===\n'); opt.optimize_rsi('BTC_USDT', 'gate.io', [25,30,35], [65,70,75]); print('\n=== Strategy Comparison ===\n'); opt.compare_strategies('BTC_USDT', 'gate.io')"

echo.
echo ======================================================================
echo Optimization Complete!
echo ======================================================================
pause
