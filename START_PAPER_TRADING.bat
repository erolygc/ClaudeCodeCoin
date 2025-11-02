@echo off
echo ======================================================================
echo 🎯 ClaudeCodeCoin - Paper Trading Engine
echo ======================================================================
echo.
echo Bu sistem sanal bakiye ile gerçek sinyaller üzerinde işlem yapacak.
echo.
echo 💰 Başlangıç Bakiyesi: $10,000 USD
echo 📊 Maksimum Pozisyon: 5 adet
echo 🛡️  Stop Loss: %%5
echo 🎯 Take Profit: %%10-20 (confidence'a göre)
echo.
echo ======================================================================
echo.

REM Sanal ortamı aktive et
call venv\Scripts\activate

REM Paper trading engine'i başlat
cd Phase7_PaperTrading
python paper_trading_engine.py

pause
