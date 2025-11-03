@echo off
:: VERIFY STARTUP - Collectors'in dogru basladigini dogrula

echo.
echo ================================================================================
echo   COLLECTOR STARTUP VERIFICATION
echo ================================================================================
echo.
echo Bu script Collectors'in dogru coin sayisiyla basladigini kontrol eder.
echo.

python VERIFY_COLLECTOR_STARTUP.py

echo.
echo ================================================================================
echo.
pause
