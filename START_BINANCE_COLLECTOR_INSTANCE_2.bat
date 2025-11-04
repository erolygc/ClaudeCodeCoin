@echo off
title Binance Collector Instance 2 (Meme + Layer 2)

echo ============================================================
echo  BINANCE COLLECTOR INSTANCE 2
echo  Monitoring: Meme Coins + Layer 2
echo ============================================================
echo.

cd Phase1_DataBackbone\collectors
python multi_instance_binance_collector.py --instance 2

pause
