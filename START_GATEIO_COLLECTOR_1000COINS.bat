@echo off
title Gate.io Collector (550 Coins - 1000 Coin System)

echo ============================================================
echo  GATE.IO COLLECTOR - 1000 COIN SYSTEM
echo  Monitoring: 550 Gate.io USDT Pairs
echo ============================================================
echo.

cd Phase1_DataBackbone\collectors
python multi_coin_gateio_collector_1000coins.py

pause
