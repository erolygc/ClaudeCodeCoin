@echo off
chcp 65001 >nul
title ClaudeCodeCoin - Auto Trading System

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     ClaudeCodeCoin - Otomatik Trading Sistemi               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Sistem Özellikleri:
echo   💰 Başlangıç Bakiyesi: $10,000
echo   📊 Pozisyon Boyutu: Max %%10 (portföy)
echo   🎯 Max Açık Pozisyon: 15
echo   🛑 Stop Loss: %%5
echo   ✅ Take Profit: %%10-25
echo   📈 Min Confidence: %%50
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo [1/3] Virtual environment aktif ediliyor...
call venv\Scripts\activate.bat

echo [2/3] Dashboard başlatılıyor (yeni pencerede)...
start "Dashboard" cmd /k "venv\Scripts\activate.bat && streamlit run dashboard.py"

timeout /t 3 >nul

echo [3/3] Trading sistemi başlatılıyor...
echo.
echo ══════════════════════════════════════════════════════════════
echo   SİSTEM ÇALIŞIYOR!
echo ══════════════════════════════════════════════════════════════
echo   📊 Dashboard: http://localhost:8501
echo   💼 Trading Engine: Bu pencere
echo   🔴 Durdurmak için: CTRL+C
echo ══════════════════════════════════════════════════════════════
echo.

python start_trading_system_windows.py --top 50

pause
