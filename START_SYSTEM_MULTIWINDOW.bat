@echo off
chcp 65001 >nul
title ClaudeCodeCoin - System Launcher

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║     ClaudeCodeCoin - Multi-Window Automated Trading System            ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo Sistem Özellikleri:
echo   💰 Başlangıç Bakiyesi: $10,000
echo   📊 Pozisyon Boyutu: Max %%10 (portföy)
echo   🎯 Max Açık Pozisyon: 15
echo   🛑 Stop Loss: %%5
echo   ✅ Take Profit: %%10-25
echo   📈 Min Confidence: %%50
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo [1/5] Virtual environment hazırlanıyor...
call venv\Scripts\activate.bat

echo [2/5] Dashboard başlatılıyor (Pencere 1)...
start "📊 Dashboard - ClaudeCodeCoin" cmd /k "title 📊 Dashboard - ClaudeCodeCoin && echo. && echo ═════════════════════════════════════════ && echo    📊 DASHBOARD BAŞLATILIYOR && echo ═════════════════════════════════════════ && echo. && echo Dashboard URL: http://localhost:8501 && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && streamlit run dashboard.py"

timeout /t 3 >nul

echo [3/5] Hybrid Scanner başlatılıyor (Pencere 2)...
start "🔍 Hybrid Scanner - ClaudeCodeCoin" cmd /k "title 🔍 Hybrid Scanner - ClaudeCodeCoin && color 0A && echo. && echo ═════════════════════════════════════════ && echo    🔍 HYBRID PUMP SCANNER && echo ═════════════════════════════════════════ && echo. && echo Tarama aralığı: 30 saniye && echo Minimum confidence: %%50 && echo Volume spike threshold: 0%% && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && python Phase6_PumpDetection/realtime_hybrid_scanner.py --interval 30"

timeout /t 3 >nul

echo [4/5] Paper Trading Engine başlatılıyor (Pencere 3)...
start "💰 Trading Engine - ClaudeCodeCoin" cmd /k "title 💰 Trading Engine - ClaudeCodeCoin && color 0B && echo. && echo ═════════════════════════════════════════ && echo    💰 PAPER TRADING ENGINE && echo ═════════════════════════════════════════ && echo. && echo Başlangıç bakiyesi: $10,000 && echo Max pozisyon: 15 && echo Stop Loss: %%5 && echo Take Profit: %%10-25 && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && python Phase7_PaperTrading/paper_trading_engine.py"

timeout /t 3 >nul

echo [5/5] Real-time Monitor başlatılıyor (Pencere 4)...
start "📈 System Monitor - ClaudeCodeCoin" cmd /k "title 📈 System Monitor - ClaudeCodeCoin && color 0E && echo. && echo ═════════════════════════════════════════ && echo    📈 REAL-TIME SYSTEM MONITOR && echo ═════════════════════════════════════════ && echo. && echo 30 saniyede bir otomatik güncelleme && echo. && echo Bu pencereyi KAPATMAYIN! && echo ═════════════════════════════════════════ && echo. && cd /d C:\Users\Botai\Desktop\Projeler\ClaudeCodeCoin && venv\Scripts\activate.bat && python REAL_TIME_MONITOR.py"

timeout /t 2 >nul

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo ✅ TÜM SİSTEMLER BAŞLATILDI!
echo.
echo Açılan Pencereler:
echo   📊 Pencere 1: Dashboard (http://localhost:8501)
echo   🔍 Pencere 2: Hybrid Scanner (Yeşil)
echo   💰 Pencere 3: Paper Trading Engine (Mavi)
echo   📈 Pencere 4: Real-time Monitor (Sarı)
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
