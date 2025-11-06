#!/bin/bash
# ClaudeCodeCoin - Stop All Components (Linux/Mac)

echo "================================================================================"
echo "                   CLAUDECODECOIN - STOP ALL"
echo "================================================================================"
echo ""
echo "Tum componentler durduruluyor..."
echo ""

# PID dosyalarini kontrol et
if [ ! -d ".pids" ]; then
    echo "[INFO] .pids klasoru bulunamadi. Process'ler START_ALL.sh ile baslatilmamis."
    echo ""
    echo "Manuel olarak durmamis Python process'leri aramak ister misiniz? (y/n)"
    read -r choice

    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        echo ""
        echo "[SEARCH] Python process'leri aranıyor..."
        ps aux | grep -E "gateio_collector|pump_scanner|paper_trading" | grep -v grep
        echo ""
        echo "Bu process'leri durdurmak icin: pkill -f <script_adi>"
    fi
    exit 0
fi

# Her component'i durdur
for component in collector pump_scanner paper_trading; do
    pid_file=".pids/${component}.pid"

    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")

        # Process calisiyor mu kontrol et
        if ps -p $pid > /dev/null 2>&1; then
            echo "[STOP] $component durduruluyor (PID: $pid)..."
            kill $pid 2>/dev/null

            # 5 saniye bekle
            sleep 2

            # Hala calisiyorsa force kill
            if ps -p $pid > /dev/null 2>&1; then
                echo "[FORCE] $component zorla durduruluyor..."
                kill -9 $pid 2>/dev/null
            fi

            echo "[OK] $component durduruldu"
        else
            echo "[INFO] $component zaten durmus (PID: $pid)"
        fi

        # PID dosyasini sil
        rm "$pid_file"
    else
        echo "[WARN] $component PID dosyasi bulunamadi"
    fi
done

# .pids klasorunu sil
rmdir .pids 2>/dev/null

echo ""
echo "================================================================================"
echo "[SUCCESS] Tum componentler durduruldu"
echo "================================================================================"
echo ""
