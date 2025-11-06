#!/bin/bash
# ClaudeCodeCoin - Master Startup Script (Linux/Mac)
# Tüm sistemi başlatır ve kontrol eder

echo "================================================================================"
echo "  CLAUDECODECOIN - MASTER STARTUP SCRIPT"
echo "================================================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ============================================================================
# STEP 1: GIT PULL (Get latest updates)
# ============================================================================

echo "[STEP 1] Git Pull - Getting latest updates..."
if git pull origin claude/dev-project-update-011CUo3BwULJ7Rmb8JqRuqhd 2>&1; then
    echo "[OK] Git pull successful"
else
    echo "[WARN] Git pull had issues (might already be up to date)"
fi

echo ""

# ============================================================================
# STEP 2: VERIFY CONFIG
# ============================================================================

echo "[STEP 2] Verifying configuration..."

CONFIG_FILE="Phase7_PaperTrading/config.py"
if [ -f "$CONFIG_FILE" ]; then
    echo "[OK] Config file exists"

    CONFIG_CONTENT=$(grep "MIN_VOLUME_SPIKE" "$CONFIG_FILE")
    echo "     Current setting: $CONFIG_CONTENT"

    if echo "$CONFIG_CONTENT" | grep -q "MIN_VOLUME_SPIKE = 0.0"; then
        echo "[OK] Volume filter disabled (TEST MODE)"
    else
        echo "[WARN] Volume filter still active - may block trades!"
    fi
else
    echo "[ERROR] Config file not found!"
    exit 1
fi

echo ""

# ============================================================================
# STEP 3: CHECK DATABASE
# ============================================================================

echo "[STEP 3] Checking database..."

DB_FILE="data_output/binance_data.db"
if [ -f "$DB_FILE" ]; then
    DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
    echo "[OK] Database exists ($DB_SIZE)"
else
    echo "[ERROR] Database not found! Collector needs to run first."
    echo "     Run: python Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py"
    exit 1
fi

echo ""

# ============================================================================
# STEP 4: CHECK PUMP ALERTS
# ============================================================================

echo "[STEP 4] Checking pump alerts..."

ALERTS_DIR="pump_alerts"
if [ -d "$ALERTS_DIR" ]; then
    TODAY=$(date +%Y%m%d)
    ALERT_FILE="$ALERTS_DIR/pump_alerts_$TODAY.json"

    if [ -f "$ALERT_FILE" ]; then
        ALERT_COUNT=$(python3 -c "import json; data=json.load(open('$ALERT_FILE')); print(len(data))" 2>/dev/null || echo "0")
        echo "[OK] Alert file exists: $ALERT_COUNT alerts today"
    else
        echo "[WARN] No alert file for today - pump scanner needs to run"
    fi
else
    echo "[WARN] Alerts directory not found - will be created on first run"
fi

echo ""

# ============================================================================
# STEP 5: CHECK DEPENDENCIES
# ============================================================================

echo "[STEP 5] Checking dashboard dependencies..."

if python3 -c "import streamlit, plotly" 2>/dev/null; then
    echo "[OK] Dashboard dependencies installed"
else
    echo "[WARN] Installing dashboard dependencies..."
    pip3 install streamlit plotly --quiet
fi

echo ""

# ============================================================================
# STEP 6: START SYSTEMS
# ============================================================================

echo "[STEP 6] Ready to start systems!"
echo ""
echo "================================================================================"
echo "  STARTUP INSTRUCTIONS"
echo "================================================================================"
echo ""

echo "The system will launch 4 components in separate terminal windows:"
echo ""
echo "  1. Data Collector (Gate.io WebSocket)"
echo "  2. Pump Scanner (Alert generation)"
echo "  3. Paper Trading Engine (Auto-trading)"
echo "  4. Dashboard (Web UI on http://localhost:8501)"
echo ""
echo "Press ENTER to auto-start all components, or Ctrl+C to exit..."
read -r

# ============================================================================
# AUTO START ALL COMPONENTS
# ============================================================================

echo ""
echo "[AUTO-START] Launching all components..."
echo ""

# Start Data Collector
echo "[1/4] Starting Data Collector..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR'; python3 Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -hold -e "cd '$SCRIPT_DIR'; python3 Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py" &
else
    echo "  [INFO] No terminal emulator found. Run manually:"
    echo "    python3 Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py"
fi
sleep 2

# Start Pump Scanner
echo "[2/4] Starting Pump Scanner..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/Phase6_PumpDetection'; python3 realtime_pump_scanner.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -hold -e "cd '$SCRIPT_DIR/Phase6_PumpDetection'; python3 realtime_pump_scanner.py" &
else
    echo "  [INFO] Run manually: cd Phase6_PumpDetection && python3 realtime_pump_scanner.py"
fi
sleep 2

# Start Paper Trading
echo "[3/4] Starting Paper Trading..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/Phase7_PaperTrading'; python3 paper_trading_engine.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -hold -e "cd '$SCRIPT_DIR/Phase7_PaperTrading'; python3 paper_trading_engine.py" &
else
    echo "  [INFO] Run manually: cd Phase7_PaperTrading && python3 paper_trading_engine.py"
fi
sleep 2

# Start Dashboard
echo "[4/4] Starting Dashboard (Web UI)..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR'; streamlit run dashboard.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -hold -e "cd '$SCRIPT_DIR'; streamlit run dashboard.py" &
else
    echo "  [INFO] Run manually: streamlit run dashboard.py"
fi

echo ""
echo "================================================================================"
echo "  ALL SYSTEMS LAUNCHED!"
echo "================================================================================"
echo ""
echo "✅ Data Collector: Running in terminal 1"
echo "✅ Pump Scanner: Running in terminal 2"
echo "✅ Paper Trading: Running in terminal 3"
echo "✅ Dashboard: Opening at http://localhost:8501"
echo ""
echo "Wait 2-3 minutes for first trades to open."
echo ""
echo "Dashboard should auto-open in browser. If not, open manually:"
echo "  http://localhost:8501"
echo ""
echo "Press Ctrl+C to exit this window (components will keep running)"
echo ""

# Try to open browser
sleep 3
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8501 2>/dev/null &
elif command -v open &> /dev/null; then
    open http://localhost:8501 2>/dev/null &
fi

# Keep script running
while true; do
    sleep 60
done
