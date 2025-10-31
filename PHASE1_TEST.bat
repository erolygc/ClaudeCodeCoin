@echo off
echo ======================================================================
echo Phase 1 - Data Backbone Test Suite
echo ======================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

echo [1/3] Testing Data Quality Validator...
echo.
python Phase1_DataBackbone\validators\data_quality.py
echo.

echo [2/3] Calculating Technical Indicators...
echo.
python Phase1_DataBackbone\indicators\indicator_engine.py
echo.

echo [3/3] Running Exchange Comparison...
echo.
python Phase1_DataBackbone\collectors\compare_exchanges.py
echo.

echo ======================================================================
echo Phase 1 Tests Complete!
echo ======================================================================
pause
