@echo off
chcp 65001 >nul
title ClaudeCodeCoin - System Health Check

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         ClaudeCodeCoin - Sistem Sağlık Kontrolü             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Sistem kontrolleri yapılıyor...
echo.

REM Run health check
python SYSTEM_HEALTH_CHECK.py

echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause
