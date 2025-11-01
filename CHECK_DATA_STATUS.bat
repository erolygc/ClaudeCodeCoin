@echo off
echo ======================================================================
echo 📊 ClaudeCodeCoin - Database Data Status Check
echo ======================================================================
echo.

python -c "import sqlite3; import os; from datetime import datetime; db = 'data_output/binance_data.db'; conn = sqlite3.connect(db) if os.path.exists(db) else None; print('=== BINANCE DATA ==='); print(f'Database: {db}'); print(f'Exists: {os.path.exists(db)}'); cursor = conn.cursor() if conn else None; cursor.execute('SELECT symbol, exchange, COUNT(*) as count, MIN(datetime) as first, MAX(datetime) as last FROM klines GROUP BY symbol, exchange ORDER BY exchange, symbol') if cursor else None; rows = cursor.fetchall() if cursor else []; [print(f'{row[0]:12} ({row[1]:8}): {row[2]:4} bars | {row[3]} -> {row[4]}') for row in rows] if rows else print('No data'); conn.close() if conn else None"

echo.
echo ======================================================================
echo Press any key to exit...
pause > nul
