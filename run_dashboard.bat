@echo off
title ClaudeCodeCoin - Dashboard
echo ================================================================================
echo  TRADING DASHBOARD (STREAMLIT)
echo ================================================================================
echo Starting dashboard...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Opening dashboard at http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run dashboard.py --server.port 8501 --server.headless true

echo.
echo Dashboard stopped.
pause
