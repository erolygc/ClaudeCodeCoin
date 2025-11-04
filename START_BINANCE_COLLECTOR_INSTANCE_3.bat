@echo off
title Binance Collector Instance 3 (AI + Gaming + DeFi)

echo ============================================================
echo  BINANCE COLLECTOR INSTANCE 3
echo  Monitoring: AI + Gaming + DeFi
echo ============================================================
echo.

cd Phase1_DataBackbone\collectors
python multi_instance_binance_collector.py --instance 3

pause
