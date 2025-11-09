#!/bin/bash
# ClaudeCodeCoin - Live Trading System Runner
# Tüm bileşenleri başlatır (Linux/Mac)

echo "================================================================================"
echo "CLAUDECODECOIN - LIVE TRADING SYSTEM"
echo "================================================================================"
echo ""
echo "Starting all components..."
echo ""
echo "Components:"
echo "  1. Gate.io Data Collector (550 coins)"
echo "  2. Pump Scanner (Real-time detection)"
echo "  3. Paper Trading Engine (Virtual money)"
echo ""
echo "================================================================================"
echo ""

# Klasörleri oluştur
mkdir -p data_output
mkdir -p logs
mkdir -p pump_alerts

# Terminal sayısı
TERMINALS=3

# Kullanıcıya seçenek sun
echo "How to run:"
echo "  [1] All in one terminal (sequential logs)"
echo "  [2] Separate terminals (requires tmux)"
echo "  [3] Background processes (run with &)"
echo ""
read -p "Select option [1-3]: " OPTION

case $OPTION in
  1)
    echo ""
    echo "Running in single terminal mode..."
    echo "Note: Components will run sequentially. Press Ctrl+C to stop all."
    echo ""

    # 1. Collector'ı başlat (background)
    echo "[1/3] Starting Gate.io Collector..."
    python3 run_live_gateio_collector.py &
    COLLECTOR_PID=$!
    sleep 5

    # 2. Pump Scanner'ı başlat (background)
    echo "[2/3] Starting Pump Scanner..."
    python3 run_live_pump_scanner.py &
    SCANNER_PID=$!
    sleep 5

    # 3. Paper Trading'i başlat (foreground)
    echo "[3/3] Starting Paper Trading Engine..."
    python3 run_live_paper_trading.py

    # Cleanup
    kill $COLLECTOR_PID $SCANNER_PID 2>/dev/null
    ;;

  2)
    echo ""
    echo "Running in separate terminals (tmux)..."

    # tmux session oluştur
    tmux new-session -d -s claudecodecoin

    # Window 1: Data Collector
    tmux rename-window -t claudecodecoin:0 'Collector'
    tmux send-keys -t claudecodecoin:0 'python3 run_live_gateio_collector.py' C-m

    # Window 2: Pump Scanner
    tmux new-window -t claudecodecoin:1 -n 'Scanner'
    tmux send-keys -t claudecodecoin:1 'python3 run_live_pump_scanner.py' C-m

    # Window 3: Paper Trading
    tmux new-window -t claudecodecoin:2 -n 'Trading'
    tmux send-keys -t claudecodecoin:2 'python3 run_live_paper_trading.py' C-m

    # Attach to session
    echo ""
    echo "================================================================================"
    echo "TMUX SESSION STARTED"
    echo "================================================================================"
    echo ""
    echo "Windows:"
    echo "  0: Data Collector"
    echo "  1: Pump Scanner"
    echo "  2: Paper Trading"
    echo ""
    echo "Controls:"
    echo "  Switch windows: Ctrl+B then 0/1/2"
    echo "  Detach: Ctrl+B then D"
    echo "  Stop all: tmux kill-session -t claudecodecoin"
    echo ""
    echo "Attaching to session..."
    sleep 2
    tmux attach-session -t claudecodecoin
    ;;

  3)
    echo ""
    echo "Running as background processes..."

    # 1. Collector
    echo "[1/3] Starting Gate.io Collector (background)..."
    nohup python3 run_live_gateio_collector.py > logs/collector_bg.log 2>&1 &
    echo "  PID: $! (logs/collector_bg.log)"

    # 2. Scanner
    echo "[2/3] Starting Pump Scanner (background)..."
    nohup python3 run_live_pump_scanner.py > logs/scanner_bg.log 2>&1 &
    echo "  PID: $! (logs/scanner_bg.log)"

    # 3. Paper Trading
    echo "[3/3] Starting Paper Trading (background)..."
    nohup python3 run_live_paper_trading.py > logs/trading_bg.log 2>&1 &
    echo "  PID: $! (logs/trading_bg.log)"

    echo ""
    echo "================================================================================"
    echo "ALL COMPONENTS RUNNING IN BACKGROUND"
    echo "================================================================================"
    echo ""
    echo "Monitor logs:"
    echo "  tail -f logs/collector_bg.log"
    echo "  tail -f logs/scanner_bg.log"
    echo "  tail -f logs/trading_bg.log"
    echo ""
    echo "Stop all:"
    echo "  pkill -f 'run_live_'"
    echo ""
    ;;

  *)
    echo "Invalid option. Exiting."
    exit 1
    ;;
esac

echo ""
echo "Done!"
