#!/bin/bash
# ClaudeCodeCoin - Master Launcher (Linux/Mac)
# Tum sistemi tek komutla baslatir

echo "================================================================================"
echo "                   CLAUDECODECOIN - MASTER LAUNCHER"
echo "================================================================================"
echo ""
echo "Tum sistem baslatiliyor..."
echo "  [1] Gate.io Data Collector (550 coins)"
echo "  [2] Realtime Pump Scanner"
echo "  [3] Paper Trading Engine"
echo ""
echo "Her component arka planda calistirilacak."
echo "Durdurmak icin: ./STOP_ALL.sh"
echo "================================================================================"
echo ""

# Python kontrolu
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 bulunamadi! Lutfen Python3 yukleyin."
    exit 1
fi

# Gerekli paketleri kontrol et
echo "[CHECK] Python paketleri kontrol ediliyor..."
python3 -c "import websockets, gate_api" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARN] Bazi paketler eksik olabilir. Yukleniyor..."
    pip3 install websockets gate-api loguru python-dotenv
fi

# PID dosyalarini saklamak icin dizin olustur
mkdir -p .pids

# 1. Gate.io Collector'i baslat
echo "[1/3] Gate.io Collector baslatiliyor..."
nohup python3 Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py > logs/collector.out 2>&1 &
echo $! > .pids/collector.pid
sleep 3

# 2. Pump Scanner'i baslat
echo "[2/3] Pump Scanner baslatiliyor..."
nohup python3 Phase6_PumpDetection/realtime_pump_scanner.py > logs/pump_scanner.out 2>&1 &
echo $! > .pids/pump_scanner.pid
sleep 3

# 3. Paper Trading'i baslat
echo "[3/3] Paper Trading baslatiliyor..."
nohup python3 Phase7_PaperTrading/paper_trading_engine.py > logs/paper_trading.out 2>&1 &
echo $! > .pids/paper_trading.pid
sleep 2

echo ""
echo "================================================================================"
echo "[SUCCESS] Tum componentler baslatildi!"
echo "================================================================================"
echo ""
echo "Process ID'ler:"
echo "  - Gate.io Collector: $(cat .pids/collector.pid)"
echo "  - Pump Scanner: $(cat .pids/pump_scanner.pid)"
echo "  - Paper Trading: $(cat .pids/paper_trading.pid)"
echo ""
echo "Log dosyalari:"
echo "  - Collector: logs/collector.out"
echo "  - Pump Scanner: logs/pump_scanner.out"
echo "  - Paper Trading: logs/paper_trading.out"
echo ""
echo "Durum kontrol: python3 SYSTEM_HEALTH_CHECK.py"
echo "Durdurmak icin: ./STOP_ALL.sh"
echo "================================================================================"
echo ""
