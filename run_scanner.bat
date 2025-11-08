@echo off
title ClaudeCodeCoin - Hybrid Scanner
echo ================================================================================
echo  HYBRID PUMP SCANNER
echo ================================================================================
echo Starting scanner...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

python Phase6_PumpDetection\realtime_hybrid_scanner.py --interval 30

echo.
echo Scanner stopped.
pause
