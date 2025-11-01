@echo off
echo ======================================================================
echo 🔥 ClaudeCodeCoin - Pump Detection Test
echo ======================================================================
echo.
echo Bu test pump ve dump tespit motorunu calistiracak.
echo Veritabanimzdaki sembolleri analiz edecek ve pump sinyalleri arayacak.
echo.
echo ======================================================================
echo.

python -c "from Phase6_PumpDetection.pump_detection_engine import test_pump_detection; test_pump_detection()"

echo.
echo ======================================================================
echo Test tamamlandi!
echo ======================================================================
pause
