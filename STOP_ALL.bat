@echo off
REM ClaudeCodeCoin - Stop All Components (Windows)

echo ================================================================================
echo                    CLAUDECODECOIN - STOP ALL
echo ================================================================================
echo.
echo Tum Python process'leri durduruluyor...
echo.

REM Tüm Python process'lerini listele ve kullanıcıya sor
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I /N "python.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo [WARNING] Asagidaki Python process'leri bulundu:
    tasklist /FI "IMAGENAME eq python.exe"
    echo.
    echo Tum Python process'lerini durdurmak ister misiniz? (E/H)
    set /p choice=Seciminiz:

    if /I "%choice%"=="E" (
        echo.
        echo [STOP] Tum Python process'leri durduruluyor...
        taskkill /F /IM python.exe /T >nul 2>&1
        echo [OK] Tum process'ler durduruldu.
    ) else (
        echo.
        echo [CANCEL] Islem iptal edildi.
    )
) else (
    echo [INFO] Calisan Python process bulunamadi.
)

echo.
echo ================================================================================
echo [DONE] Islem tamamlandi
echo ================================================================================
echo.
pause
