@echo off
title Binance Collector Instance 5 (Small Cap + Experimental)

echo ============================================================
echo  BINANCE COLLECTOR INSTANCE 5
echo  Monitoring: Small Cap + Experimental
echo ============================================================
echo.

cd Phase1_DataBackbone\collectors
python multi_instance_binance_collector.py --instance 5

pause
