# ClaudeCodeCoin - Futures Trading Startup Script (Windows)
# Starts the futures trading system and dashboard

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  CLAUDECODECOIN - FUTURES TRADING SYSTEM" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# ============================================================================
# STEP 1: CHECK CONFIGURATION
# ============================================================================

Write-Host "[STEP 1] Checking configuration..." -ForegroundColor Yellow

$CONFIG_FILE = "Phase8_FuturesTrading\config_futures.py"
if (Test-Path $CONFIG_FILE) {
    Write-Host "[OK] Config file exists" -ForegroundColor Green

    # Show key settings
    $balance = (Select-String -Path $CONFIG_FILE -Pattern "INITIAL_BALANCE = (\d+\.?\d*)").Matches.Groups[1].Value
    $leverage = (Select-String -Path $CONFIG_FILE -Pattern "MAX_LEVERAGE = (\d+)").Matches.Groups[1].Value
    $position = (Select-String -Path $CONFIG_FILE -Pattern "POSITION_SIZE_USD = (\d+\.?\d*)").Matches.Groups[1].Value

    Write-Host "     Balance: `$$balance USD" -ForegroundColor Cyan
    Write-Host "     Leverage: ${leverage}x" -ForegroundColor Cyan
    Write-Host "     Position Size: `$$position USD" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Config file not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 2: CHECK DEPENDENCIES
# ============================================================================

Write-Host "[STEP 2] Checking dependencies..." -ForegroundColor Yellow

$missing = @()

try {
    python -c "import streamlit" 2>$null
    if ($LASTEXITCODE -ne 0) { $missing += "streamlit" }
} catch {
    $missing += "streamlit"
}

try {
    python -c "import plotly" 2>$null
    if ($LASTEXITCODE -ne 0) { $missing += "plotly" }
} catch {
    $missing += "plotly"
}

if ($missing.Count -gt 0) {
    Write-Host "[WARN] Missing dependencies: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "Installing..." -ForegroundColor Yellow
    pip install $($missing -join ' ') --quiet
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[OK] All dependencies installed" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# STEP 3: CHECK DATABASE
# ============================================================================

Write-Host "[STEP 3] Checking database..." -ForegroundColor Yellow

$DB_FILE = "data_output\binance_data.db"
if (Test-Path $DB_FILE) {
    $DB_SIZE = (Get-Item $DB_FILE).Length / 1MB
    Write-Host "[OK] Market database exists ($([math]::Round($DB_SIZE, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Market database not found!" -ForegroundColor Red
    Write-Host "     Run: python Phase1_DataBackbone\collectors\multi_coin_gateio_collector_1000coins.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 4: CHECK PUMP ALERTS
# ============================================================================

Write-Host "[STEP 4] Checking pump scanner..." -ForegroundColor Yellow

$ALERTS_DIR = "pump_alerts"
if (Test-Path $ALERTS_DIR) {
    $TODAY = Get-Date -Format "yyyyMMdd"
    $ALERT_FILE = "$ALERTS_DIR\pump_alerts_$TODAY.json"

    if (Test-Path $ALERT_FILE) {
        $ALERT_COUNT = (Get-Content $ALERT_FILE | ConvertFrom-Json).Count
        Write-Host "[OK] Alert file exists: $ALERT_COUNT alerts today" -ForegroundColor Green
    } else {
        Write-Host "[WARN] No alert file for today - pump scanner needs to run" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARN] Alerts directory not found - will be created on first run" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 5: MODE SELECTION
# ============================================================================

Write-Host "[STEP 5] Select trading mode..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  1) PAPER TRADING (Safe - No real money)" -ForegroundColor Green
Write-Host "  2) TESTNET (Test with fake USDT)" -ForegroundColor Cyan
Write-Host "  3) REAL TRADING (⚠️ REAL MONEY!)" -ForegroundColor Red
Write-Host ""

$mode = Read-Host "Select mode (1-3)"

$engineArgs = ""
switch ($mode) {
    "1" {
        Write-Host ""
        Write-Host "Selected: PAPER TRADING" -ForegroundColor Green
        $engineArgs = ""
    }
    "2" {
        Write-Host ""
        Write-Host "Selected: TESTNET" -ForegroundColor Cyan
        Write-Host "[INFO] Make sure you have testnet API keys in .env" -ForegroundColor Yellow
        $engineArgs = "--testnet"
    }
    "3" {
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Red
        Write-Host "  ⚠️ WARNING: REAL TRADING MODE ⚠️" -ForegroundColor Red
        Write-Host "================================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "You are about to trade with REAL money!" -ForegroundColor Yellow
        Write-Host "Balance: `$$balance USD" -ForegroundColor Yellow
        Write-Host "Leverage: ${leverage}x" -ForegroundColor Yellow
        Write-Host ""
        $confirm = Read-Host "Type 'YES I UNDERSTAND THE RISKS' to continue"

        if ($confirm -ne "YES I UNDERSTAND THE RISKS") {
            Write-Host "Cancelled." -ForegroundColor Yellow
            exit 0
        }

        $engineArgs = "--real --mainnet"
    }
    default {
        Write-Host "[ERROR] Invalid selection" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# ============================================================================
# STEP 6: START SYSTEMS
# ============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  STARTING FUTURES TRADING SYSTEM" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "The system will launch 2 components:" -ForegroundColor Yellow
Write-Host "  1. Futures Trading Engine (monitors pump alerts)" -ForegroundColor White
Write-Host "  2. Futures Dashboard (Web UI on http://localhost:8501)" -ForegroundColor White
Write-Host ""
Write-Host "Press ENTER to start..." -ForegroundColor Yellow
Read-Host

Write-Host ""
Write-Host "[1/2] Starting Futures Trading Engine..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$SCRIPT_DIR\Phase8_FuturesTrading'; python futures_trading_engine.py $engineArgs"
Start-Sleep -Seconds 2

Write-Host "[2/2] Starting Futures Dashboard..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$SCRIPT_DIR'; streamlit run Phase8_FuturesTrading\futures_dashboard.py"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "  FUTURES SYSTEM LAUNCHED!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Trading Engine: Running in terminal 1" -ForegroundColor Green
Write-Host "✅ Dashboard: Opening at http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Wait 1-2 minutes for first pump signals to arrive." -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard should auto-open. If not, open manually:" -ForegroundColor Yellow
Write-Host "  http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to exit (components will keep running)" -ForegroundColor Yellow
Write-Host ""

# Try to open browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:8501"

# Keep script running
Write-Host "Monitoring system..." -ForegroundColor Cyan
while ($true) {
    Start-Sleep -Seconds 60
}
