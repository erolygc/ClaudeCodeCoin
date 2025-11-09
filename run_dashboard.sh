#!/bin/bash
# ClaudeCodeCoin - Professional Trading Dashboard Launcher (Linux/Mac)

echo "================================================================================"
echo "CLAUDECODECOIN - PROFESSIONAL TRADING DASHBOARD"
echo "================================================================================"
echo ""
echo "Gate.io Futures Style Dashboard"
echo "Real-time Data Visualization"
echo ""
echo "================================================================================"
echo ""

echo "[1/2] Checking dependencies..."
pip install -q streamlit plotly pandas

echo "[2/2] Starting dashboard..."
echo ""
echo "================================================================================"
echo ""
echo "Dashboard will open in your browser automatically..."
echo "URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""
echo "================================================================================"
echo ""

streamlit run dashboard.py
