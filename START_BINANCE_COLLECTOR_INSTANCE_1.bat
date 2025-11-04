@echo off
title Binance Collector Instance 1 (Top 100 Coins)

echo ============================================================
echo  BINANCE COLLECTOR INSTANCE 1
echo  Monitoring: Top 100 Market Cap + High Volume
echo ============================================================
echo.

cd Phase1_DataBackbone\collectors
python multi_instance_binance_collector.py --instance 1

pause
