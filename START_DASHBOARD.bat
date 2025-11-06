@echo off
REM ClaudeCodeCoin - Dashboard Launcher (Windows)

echo ================================================================================
echo                    CLAUDECODECOIN - TRADING DASHBOARD
echo ================================================================================
echo.
echo Professional trading dashboard baslatiliyor...
echo.
echo Dashboard ozellikleri:
echo   - Gercek zamanli fiyat grafikleri (Candlestick)
echo   - Acik pozisyonlar tablosu
echo   - P^&L grafikleri
echo   - Portfolio ozeti
echo   - Son pump alertleri
echo.
echo ================================================================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python bulunamadi!
    pause
    exit /b 1
)

REM Streamlit kontrolu ve yukle
echo [CHECK] Streamlit kontrol ediliyor...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INSTALL] Streamlit yukleniyor...
    pip install streamlit plotly
)

echo.
echo [START] Dashboard baslatiliyor...
echo [INFO] Tarayiciniz otomatik acilacak
echo [INFO] URL: http://localhost:8501
echo.
echo [STOP] Durdurmak icin: Ctrl+C
echo ================================================================================
echo.

REM Dashboard'u baslat
streamlit run dashboard.py

pause
