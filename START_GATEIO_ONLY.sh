#!/bin/bash
# ClaudeCodeCoin - Gate.io Only Collector
# Sadece Gate.io'dan 550 coin için veri toplar

echo "======================================================================"
echo "🚀 ClaudeCodeCoin - Gate.io Data Collector"
echo "======================================================================"
echo ""
echo "📊 Gate.io'dan 550 coin için veri toplama başlatılıyor..."
echo ""
echo "Özellikler:"
echo "  ✓ 550 USDT trading pairs"
echo "  ✓ 1 dakikalık candlestick verisi"
echo "  ✓ SQLite database"
echo "  ✓ Otomatik reconnect"
echo ""
echo "======================================================================"
echo ""

# Proje dizinine git
cd "$(dirname "$0")"

# Gerekli dizinleri oluştur
mkdir -p data_output
mkdir -p logs
mkdir -p pump_alerts

# Python paketi kontrolü
echo "📦 Python paketleri kontrol ediliyor..."
python3 -c "import websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  websockets paketi yüklü değil, yükleniyor..."
    pip install -q websockets
fi

python3 -c "import sqlite3" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ SQLite3 modülü bulunamadı!"
    exit 1
fi

echo "✅ Tüm paketler hazır"
echo ""

# Gate.io collector'ı başlat
echo "🟢 Gate.io Collector başlatılıyor..."
echo ""
echo "⏹️  Durdurmak için: Ctrl+C"
echo "📊 Log dosyası: logs/gateio_collector_1000coins.log"
echo "💾 Database: data_output/binance_data.db"
echo ""
echo "======================================================================"
echo ""

python3 Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py

echo ""
echo "======================================================================"
echo "⏹️  Gate.io Collector durduruldu"
echo "======================================================================"
