#!/bin/bash
# ClaudeCodeCoin - Dashboard Launcher (Linux/Mac)

echo "================================================================================"
echo "                   CLAUDECODECOIN - TRADING DASHBOARD"
echo "================================================================================"
echo ""
echo "Professional trading dashboard baslatiliyor..."
echo ""
echo "Dashboard ozellikleri:"
echo "  - Gercek zamanli fiyat grafikleri (Candlestick)"
echo "  - Acik pozisyonlar tablosu"
echo "  - P&L grafikleri"
echo "  - Portfolio ozeti"
echo "  - Son pump alertleri"
echo "  - Trading gecmisi"
echo ""
echo "================================================================================"
echo ""

# Python kontrolu
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 bulunamadi!"
    exit 1
fi

# Streamlit kontrolu ve yukle
echo "[CHECK] Streamlit kontrol ediliyor..."
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[INSTALL] Streamlit yukleniyor..."
    pip3 install streamlit plotly
fi

echo ""
echo "[START] Dashboard baslatiliyor..."
echo "[INFO] Tarayiciniz otomatik acilacak"
echo "[INFO] URL: http://localhost:8501"
echo ""
echo "[STOP] Durdurmak icin: Ctrl+C"
echo "================================================================================"
echo ""

# Dashboard'u baslat
streamlit run dashboard.py
