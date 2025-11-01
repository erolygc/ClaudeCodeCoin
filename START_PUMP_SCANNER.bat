@echo off
echo ======================================================================
echo 🔥 ClaudeCodeCoin - Real-Time Pump Scanner
echo ======================================================================
echo.
echo Bu scanner tum coinleri surekli tarayacak ve pump sinyalleri tespit edecek.
echo.
echo OZELLIKLER:
echo   - Her 60 saniyede tum sembolleri tarar
echo   - Hacim spike tespiti (3-10x normal hacim)
echo   - Hizli fiyat degisimleri (%10+ artis)
echo   - Volatilite spike tespiti
echo   - Koordineli alim patternleri
echo.
echo ALERTS:
echo   - Confidence ^>50%% olan sinyaller icin alert olusturulur
echo   - Ayni coin icin 5 dakika cooldown vardir
echo   - Tum alerts pump_alerts/ klasorune kaydedilir
echo.
echo DURDURMAK ICIN: Ctrl+C
echo.
echo ======================================================================
echo.

REM Alert klasorunu olustur
if not exist pump_alerts mkdir pump_alerts

echo Scanner baslatiliyor...
echo.

python Phase6_PumpDetection/realtime_pump_scanner.py

echo.
echo ======================================================================
echo Scanner durduruldu
echo ======================================================================
pause
