@echo off
title ClaudeCodeCoin - Hybrid Scanner
echo ================================================================================
echo  HYBRID PUMP SCANNER
echo ================================================================================
echo Starting scanner...
echo.

python Phase6_PumpDetection\realtime_hybrid_scanner.py --interval 30

echo.
echo Scanner stopped.
pause
