@echo off
echo ======================================================================
echo 📊 ClaudeCodeCoin - Monitoring Dashboard
echo ======================================================================
echo.
echo Dashboard aciliyor...
echo.
echo Browser'inizda otomatik olarak acilacak:
echo http://localhost:8501
echo.
echo ======================================================================
echo.
echo KULLANIM:
echo   - Dashboard her 10 saniyede otomatik yenilenecek
echo   - Soldan ayarlari degistirebilirsiniz
echo   - Grafikleri yakınlastirip uzaklastirabilirsiniz
echo.
echo DURDURMAK ICIN: Ctrl+C veya bu pencereyi kapatin
echo.
echo ======================================================================
echo.

REM Gerekli paketleri kontrol et ve kur
echo Gerekli paketler kontrol ediliyor...
pip install streamlit plotly psutil > nul 2>&1

echo.
echo Dashboard baslatiliyor...
echo.

streamlit run Dashboard/monitoring_dashboard.py
