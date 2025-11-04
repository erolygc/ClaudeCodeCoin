@echo off
echo ============================================================
echo  GIT PULL CONFLICT FIX
echo ============================================================
echo.
echo Fixing conflicts and pulling latest 1000-coin system...
echo.

REM Backup your local config changes
echo [1/5] Backing up your config.py changes...
copy Phase7_PaperTrading\config.py Phase7_PaperTrading\config.py.backup
echo      Config backed up to: config.py.backup

REM Remove conflicting files
echo.
echo [2/5] Removing conflicting files...
del all_trading_pairs.json 2>nul
del all_trading_pairs.py 2>nul
echo      Removed: all_trading_pairs.json, all_trading_pairs.py

REM Stash local changes
echo.
echo [3/5] Stashing local changes...
git stash
echo      Local changes stashed

REM Pull latest code
echo.
echo [4/5] Pulling latest code from remote...
git pull
echo      Pull complete!

REM Restore your production settings if needed
echo.
echo [5/5] Done!
echo.
echo ============================================================
echo  IMPORTANT NOTES:
echo ============================================================
echo.
echo - Your old config.py is backed up as: config.py.backup
echo - New production config is now active with:
echo     MIN_CONFIDENCE: 70%%
echo     MIN_VOLUME_SPIKE: 800%%
echo.
echo - If you had custom settings, you can restore them:
echo     1. Open: Phase7_PaperTrading\config.py.backup
echo     2. Copy your custom values to: config.py
echo.
echo ============================================================
echo.
echo Press any key to continue...
pause >nul
