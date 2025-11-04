@echo off
title Binance Collector Instance 4 (Mid-Cap Altcoins)

echo ============================================================
echo  BINANCE COLLECTOR INSTANCE 4
echo  Monitoring: Mid-Cap Altcoins
echo ============================================================
echo.

cd Phase1_DataBackbone\collectors
python multi_instance_binance_collector.py --instance 4

pause
