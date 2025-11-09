@echo off
REM Windows için UTF-8 encoding ile testleri çalıştırır
REM Emoji sorununu çözer

echo ================================================================================
echo CLAUDECODECOIN - WINDOWS TEST RUNNER
echo ================================================================================
echo.

REM UTF-8 encoding ayarla
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

echo [1/4] Test verisi olusturuluyor...
python generate_test_data.py

echo.
echo [2/4] Guclu pump verisi ekleniyor...
python generate_pump_data.py

echo.
echo [3/4] Pump scanner calistiriliyor...
python run_pump_scan_once.py

echo.
echo [4/4] Paper trading test ediliyor...
python run_paper_trading_test.py

echo.
echo ================================================================================
echo TESTLER TAMAMLANDI!
echo ================================================================================
pause
