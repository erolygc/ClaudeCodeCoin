@echo off
title ClaudeCodeCoin - Paper Trading Engine
echo ================================================================================
echo  PAPER TRADING ENGINE
echo ================================================================================
echo Starting trading engine...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

python Phase8_FuturesTrading\paper_trading_futures_engine.py

echo.
echo Trading engine stopped.
pause
