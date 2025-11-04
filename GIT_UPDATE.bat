@echo off
REM ClaudeCodeCoin - GitHub Güncelleme Scripti (Windows)

echo ======================================================================
echo 🔄 ClaudeCodeCoin - GitHub Güncelleme
echo ======================================================================
echo.

REM Mevcut branch'i al
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo 📍 Mevcut branch: %CURRENT_BRANCH%
echo.

REM Working tree temiz mi kontrol et
git status -s > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  UYARI: Working tree'de değişiklikler var!
    echo.
    git status -s
    echo.
    set /p CONTINUE="Devam etmek istiyor musunuz? (Y/N): "
    if /i not "%CONTINUE%"=="Y" (
        echo ❌ İptal edildi
        exit /b 1
    )
)

echo 📥 Remote'dan güncellemeler getiriliyor...
git fetch origin

echo.
echo 🔍 Yeni commit'ler kontrol ediliyor...

REM Yeni commit'leri kontrol et
git log HEAD..origin/%CURRENT_BRANCH% --oneline > temp_commits.txt
set /p NEW_COMMITS=<temp_commits.txt

if "%NEW_COMMITS%"=="" (
    echo ✅ Yeni güncelleme yok - Her şey güncel!
    del temp_commits.txt
) else (
    echo 📋 Yeni commit'ler bulundu:
    type temp_commits.txt
    del temp_commits.txt
    echo.
    set /p PULL="Güncellemeleri çekmek istiyor musunuz? (Y/N): "
    if /i "%PULL%"=="Y" (
        echo ⬇️  Güncellemeler çekiliyor...

        REM Pull with retry logic
        set MAX_RETRIES=4
        set RETRY_COUNT=0
        set DELAY=2

        :retry_loop
        if %RETRY_COUNT% lss %MAX_RETRIES% (
            git pull origin %CURRENT_BRANCH%
            if %errorlevel% equ 0 (
                echo ✅ Güncelleme başarılı!
                goto :success
            ) else (
                set /a RETRY_COUNT+=1
                if %RETRY_COUNT% lss %MAX_RETRIES% (
                    echo ⚠️  Hata oluştu, tekrar deneniyor (%RETRY_COUNT%/%MAX_RETRIES%)...
                    timeout /t %DELAY% /nobreak > nul
                    set /a DELAY*=2
                    goto :retry_loop
                )
            )
        )

        echo ❌ Güncelleme başarısız! Manuel kontrol gerekli.
        exit /b 1

        :success
    ) else (
        echo ❌ Güncelleme iptal edildi
    )
)

echo.
echo ======================================================================
echo.
pause
