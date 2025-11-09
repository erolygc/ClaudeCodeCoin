@echo off
chcp 65001 >nul
title ClaudeCodeCoin - System Launcher

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║     ClaudeCodeCoin - Multi-Window Automated Trading System            ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo Sistem Özellikleri (TEST MODE - Demo için):
echo   💰 Başlangıç Bakiyesi: $10,000
echo   📊 Pozisyon Boyutu: Max %%10 (portföy)
echo   🎯 Max Açık Pozisyon: 15
echo   🛑 Stop Loss: %%3 (TEST)
echo   ✅ Take Profit: %%5-10 (TEST - Hızlı kapanma)
echo   📈 Min Confidence: %%30 (TEST - Maksimum sinyal)
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo [1/6] Virtual environment hazırlanıyor...
call venv\Scripts\activate.bat

echo [2/6] Data Collector başlatılıyor (Pencere 1)...
start "📡 Data Collector - ClaudeCodeCoin" cmd /k "title 📡 Data Collector - ClaudeCodeCoin && color 0D && echo. && echo ═════════════════════════════════════════ && echo    📡 GATE.IO DATA COLLECTOR && echo ═════════════════════════════════════════ && echo. && echo Toplam coin: 50 && echo Güncelleme aralığı: 60 saniye && echo Exchange: Gate.io && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && python Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py --top 50"

timeout /t 3 >nul

echo [3/6] Dashboard başlatılıyor (Pencere 2)...
start "📊 Dashboard - ClaudeCodeCoin" cmd /k "title 📊 Dashboard - ClaudeCodeCoin && echo. && echo ═════════════════════════════════════════ && echo    📊 DASHBOARD BAŞLATILIYOR && echo ═════════════════════════════════════════ && echo. && echo Dashboard URL: http://localhost:8501 && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && streamlit run dashboard.py"

timeout /t 3 >nul

echo [4/6] Hybrid Scanner başlatılıyor (Pencere 3)...
start "🔍 Hybrid Scanner - ClaudeCodeCoin" cmd /k "title 🔍 Hybrid Scanner - ClaudeCodeCoin && color 0A && echo. && echo ═════════════════════════════════════════ && echo    🔍 HYBRID PUMP SCANNER && echo ═════════════════════════════════════════ && echo. && echo Tarama aralığı: 30 saniye && echo Minimum confidence: %%30 (TEST) && echo Volume spike threshold: 0%% && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && python Phase6_PumpDetection/realtime_hybrid_scanner.py --interval 30"

timeout /t 3 >nul

echo [5/6] Paper Trading Engine başlatılıyor (Pencere 4)...
start "💰 Trading Engine - ClaudeCodeCoin" cmd /k "title 💰 Trading Engine - ClaudeCodeCoin && color 0B && echo. && echo ═════════════════════════════════════════ && echo    💰 PAPER TRADING ENGINE && echo ═════════════════════════════════════════ && echo. && echo Başlangıç bakiyesi: $10,000 && echo Max pozisyon: 15 && echo Stop Loss: %%3 (TEST) && echo Take Profit: %%5-10 (TEST) && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && python Phase7_PaperTrading/paper_trading_engine.py"

timeout /t 3 >nul

echo [6/6] Real-time Monitor başlatılıyor (Pencere 5)...
start "📈 System Monitor - ClaudeCodeCoin" cmd /k "title 📈 System Monitor - ClaudeCodeCoin && color 0E && echo. && echo ═════════════════════════════════════════ && echo    📈 REAL-TIME SYSTEM MONITOR && echo ═════════════════════════════════════════ && echo. && echo 30 saniyede bir otomatik güncelleme && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && python REAL_TIME_MONITOR.py"

timeout /t 2 >nul

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo ✅ TÜM SİSTEMLER BAŞLATILDI! (5 PENCERE)
echo.
echo Açılan Pencereler:
echo   📡 Pencere 1: Data Collector (Pembe - Gate.io 50 coin)
echo   📊 Pencere 2: Dashboard (http://localhost:8501)
echo   🔍 Pencere 3: Hybrid Scanner (Yeşil - Min Conf: %%30)
echo   💰 Pencere 4: Paper Trading Engine (Mavi - TEST MODE)
echo   📈 Pencere 5: Real-time Monitor (Sarı - Auto-refresh)
echo.
echo Test Ayarları (Maksimum Sinyal İçin):
echo   • Min Confidence: %%30 (Normal: %%50)
echo   • Stop Loss: %%3 (Normal: %%5)
echo   • Take Profit: %%5-10 (Normal: %%10-25)
echo   • Volume Spike: 0%% (Filtre kapalı)
echo.
echo Sistem Kontrolleri:
echo   • CHECK_SYSTEM.bat - Sistem sağlık kontrolü
echo   • Dashboard - http://localhost:8501
echo.
echo ⚠️  Sistemi durdurmak için TÜM pencereleri kapatın
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo Bu pencereyi kapatabilirsiniz.
echo.

pause
