#!/bin/bash
# ClaudeCodeCoin - Futures Trading Startup Script (Linux/Mac)
# Starts the futures trading system and dashboard

echo "================================================================================"
echo "  CLAUDECODECOIN - FUTURES TRADING SYSTEM"
echo "================================================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ============================================================================
# STEP 1: CHECK CONFIGURATION
# ============================================================================

echo "[STEP 1] Checking configuration..."

CONFIG_FILE="Phase8_FuturesTrading/config_futures.py"
if [ -f "$CONFIG_FILE" ]; then
    echo "[OK] Config file exists"

    # Show key settings
    BALANCE=$(grep "INITIAL_BALANCE = " "$CONFIG_FILE" | grep -oP '\d+\.?\d*')
    LEVERAGE=$(grep "MAX_LEVERAGE = " "$CONFIG_FILE" | grep -oP '\d+')
    POSITION=$(grep "POSITION_SIZE_USD = " "$CONFIG_FILE" | grep -oP '\d+\.?\d*')

    echo "     Balance: \$$BALANCE USD"
    echo "     Leverage: ${LEVERAGE}x"
    echo "     Position Size: \$$POSITION USD"
else
    echo "[ERROR] Config file not found!"
    exit 1
fi

echo ""

# ============================================================================
# STEP 2: CHECK DEPENDENCIES
# ============================================================================

echo "[STEP 2] Checking dependencies..."

MISSING=()

if ! python3 -c "import streamlit" 2>/dev/null; then
    MISSING+=("streamlit")
fi

if ! python3 -c "import plotly" 2>/dev/null; then
    MISSING+=("plotly")
fi

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "[WARN] Missing dependencies: ${MISSING[*]}"
    echo "Installing..."
    pip3 install "${MISSING[@]}" --quiet
    echo "[OK] Dependencies installed"
else
    echo "[OK] All dependencies installed"
fi

echo ""

# ============================================================================
# STEP 3: CHECK DATABASE
# ============================================================================

echo "[STEP 3] Checking database..."

DB_FILE="data_output/binance_data.db"
if [ -f "$DB_FILE" ]; then
    DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
    echo "[OK] Market database exists ($DB_SIZE)"
else
    echo "[ERROR] Market database not found!"
    echo "     Run: python3 Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py"
    exit 1
fi

echo ""

# ============================================================================
# STEP 4: CHECK PUMP ALERTS
# ============================================================================

echo "[STEP 4] Checking pump scanner..."

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
# STEP 5: MODE SELECTION
# ============================================================================

echo "[STEP 5] Select trading mode..."
echo ""
echo "  1) PAPER TRADING (Safe - No real money)"
echo "  2) TESTNET (Test with fake USDT)"
echo "  3) REAL TRADING (⚠️ REAL MONEY!)"
echo ""

read -p "Select mode (1-3): " mode

ENGINE_ARGS=""
case $mode in
    1)
        echo ""
        echo "Selected: PAPER TRADING"
        ENGINE_ARGS=""
        ;;
    2)
        echo ""
        echo "Selected: TESTNET"
        echo "[INFO] Make sure you have testnet API keys in .env"
        ENGINE_ARGS="--testnet"
        ;;
    3)
        echo ""
        echo "================================================================================"
        echo "  ⚠️ WARNING: REAL TRADING MODE ⚠️"
        echo "================================================================================"
        echo ""
        echo "You are about to trade with REAL money!"
        echo "Balance: \$$BALANCE USD"
        echo "Leverage: ${LEVERAGE}x"
        echo ""
        read -p "Type 'YES I UNDERSTAND THE RISKS' to continue: " confirm

        if [ "$confirm" != "YES I UNDERSTAND THE RISKS" ]; then
            echo "Cancelled."
            exit 0
        fi

        ENGINE_ARGS="--real --mainnet"
        ;;
    *)
        echo "[ERROR] Invalid selection"
        exit 1
        ;;
esac

echo ""

# ============================================================================
# STEP 6: START SYSTEMS
# ============================================================================

echo "================================================================================"
echo "  STARTING FUTURES TRADING SYSTEM"
echo "================================================================================"
echo ""

echo "The system will launch 2 components:"
echo "  1. Futures Trading Engine (monitors pump alerts)"
echo "  2. Futures Dashboard (Web UI on http://localhost:8501)"
echo ""
read -p "Press ENTER to start..." -r

echo ""
echo "[1/2] Starting Futures Trading Engine..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/Phase8_FuturesTrading'; python3 futures_trading_engine.py $ENGINE_ARGS; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -hold -e "cd '$SCRIPT_DIR/Phase8_FuturesTrading'; python3 futures_trading_engine.py $ENGINE_ARGS" &
else
    echo "  [INFO] No terminal emulator found. Run manually:"
    echo "    cd Phase8_FuturesTrading && python3 futures_trading_engine.py $ENGINE_ARGS"
fi
sleep 2

echo "[2/2] Starting Futures Dashboard..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR'; streamlit run Phase8_FuturesTrading/futures_dashboard.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -hold -e "cd '$SCRIPT_DIR'; streamlit run Phase8_FuturesTrading/futures_dashboard.py" &
else
    echo "  [INFO] Run manually: streamlit run Phase8_FuturesTrading/futures_dashboard.py"
fi
sleep 3

echo ""
echo "================================================================================"
echo "  FUTURES SYSTEM LAUNCHED!"
echo "================================================================================"
echo ""
echo "✅ Trading Engine: Running in terminal 1"
echo "✅ Dashboard: Opening at http://localhost:8501"
echo ""
echo "Wait 1-2 minutes for first pump signals to arrive."
echo ""
echo "Dashboard should auto-open. If not, open manually:"
echo "  http://localhost:8501"
echo ""
echo "Press Ctrl+C to exit (components will keep running)"
echo ""

# Try to open browser
sleep 3
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8501 2>/dev/null &
elif command -v open &> /dev/null; then
    open http://localhost:8501 2>/dev/null &
fi

# Keep script running
echo "Monitoring system..."
while true; do
    sleep 60
done
