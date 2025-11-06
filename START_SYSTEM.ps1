# ClaudeCodeCoin - Master Startup Script
# Tüm sistemi başlatır ve kontrol eder

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  CLAUDECODECOIN - MASTER STARTUP SCRIPT" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# ============================================================================
# STEP 1: GIT PULL (Get latest updates)
# ============================================================================

Write-Host "[STEP 1] Git Pull - Getting latest updates..." -ForegroundColor Yellow
try {
    $gitOutput = git pull origin claude/dev-project-update-011CUo3BwULJ7Rmb8JqRuqhd 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Git pull successful" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Git pull had issues: $gitOutput" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARN] Git pull failed: $_" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 2: VERIFY CONFIG
# ============================================================================

Write-Host "[STEP 2] Verifying configuration..." -ForegroundColor Yellow

$configFile = "Phase7_PaperTrading\config.py"
if (Test-Path $configFile) {
    $configContent = Get-Content $configFile | Select-String -Pattern "MIN_VOLUME_SPIKE"
    Write-Host "[OK] Config file exists" -ForegroundColor Green
    Write-Host "     Current setting: $configContent" -ForegroundColor Gray

    if ($configContent -match "MIN_VOLUME_SPIKE = 0\.0") {
        Write-Host "[OK] Volume filter disabled (TEST MODE)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Volume filter still active - may block trades!" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] Config file not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 3: CHECK DATABASE
# ============================================================================

Write-Host "[STEP 3] Checking database..." -ForegroundColor Yellow

$dbFile = "data_output\binance_data.db"
if (Test-Path $dbFile) {
    $dbSize = (Get-Item $dbFile).Length / 1MB
    Write-Host "[OK] Database exists ($($dbSize.ToString('N2')) MB)" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Database not found! Collector needs to run first." -ForegroundColor Red
    Write-Host "     Run: python Phase1_DataBackbone\collectors\multi_coin_gateio_collector_1000coins.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 4: CHECK PUMP ALERTS
# ============================================================================

Write-Host "[STEP 4] Checking pump alerts..." -ForegroundColor Yellow

$alertsDir = "pump_alerts"
if (Test-Path $alertsDir) {
    $today = Get-Date -Format "yyyyMMdd"
    $alertFile = "$alertsDir\pump_alerts_$today.json"

    if (Test-Path $alertFile) {
        $alertContent = Get-Content $alertFile -Raw | ConvertFrom-Json
        $alertCount = $alertContent.Count
        Write-Host "[OK] Alert file exists: $alertCount alerts today" -ForegroundColor Green

        # Check recent alerts
        $recent = $alertContent | Where-Object {
            $alertTime = [DateTime]::Parse($_.timestamp)
            (Get-Date) - $alertTime -lt [TimeSpan]::FromMinutes(30)
        }

        if ($recent.Count -gt 0) {
            Write-Host "[OK] Recent alerts: $($recent.Count) in last 30 minutes" -ForegroundColor Green
        } else {
            Write-Host "[WARN] No recent alerts - market may be calm" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[WARN] No alert file for today - pump scanner needs to run" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARN] Alerts directory not found - will be created on first run" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 5: START SYSTEMS
# ============================================================================

Write-Host "[STEP 5] Ready to start systems!" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  STARTUP INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Open 3 separate PowerShell terminals and run:" -ForegroundColor White
Write-Host ""

Write-Host "TERMINAL 1 - Data Collector:" -ForegroundColor Yellow
Write-Host "  cd $scriptDir" -ForegroundColor Gray
Write-Host "  python Phase1_DataBackbone\collectors\multi_coin_gateio_collector_1000coins.py" -ForegroundColor White
Write-Host ""

Write-Host "TERMINAL 2 - Pump Scanner:" -ForegroundColor Yellow
Write-Host "  cd $scriptDir\Phase6_PumpDetection" -ForegroundColor Gray
Write-Host "  python realtime_pump_scanner.py" -ForegroundColor White
Write-Host ""

Write-Host "TERMINAL 3 - Paper Trading:" -ForegroundColor Yellow
Write-Host "  cd $scriptDir\Phase7_PaperTrading" -ForegroundColor Gray
Write-Host "  python paper_trading_engine.py" -ForegroundColor White
Write-Host ""

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  MONITORING" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Check system status anytime:" -ForegroundColor Yellow
Write-Host "  python SYSTEM_HEALTH_CHECK.py" -ForegroundColor White
Write-Host ""

Write-Host "Check positions:" -ForegroundColor Yellow
Write-Host "  cd Phase7_PaperTrading" -ForegroundColor Gray
Write-Host '  python -c "from paper_trading_engine import PaperTradingEngine; e = PaperTradingEngine(); e.print_status()"' -ForegroundColor White
Write-Host ""

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  PRESS ANY KEY TO AUTO-START (or Ctrl+C to exit)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# ============================================================================
# AUTO START ALL COMPONENTS
# ============================================================================

Write-Host ""
Write-Host "[AUTO-START] Launching all components..." -ForegroundColor Green
Write-Host ""

# Start Data Collector
Write-Host "[1/3] Starting Data Collector..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; python Phase1_DataBackbone\collectors\multi_coin_gateio_collector_1000coins.py"
Start-Sleep -Seconds 3

# Start Pump Scanner
Write-Host "[2/3] Starting Pump Scanner..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\Phase6_PumpDetection'; python realtime_pump_scanner.py"
Start-Sleep -Seconds 3

# Start Paper Trading
Write-Host "[3/3] Starting Paper Trading..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\Phase7_PaperTrading'; python paper_trading_engine.py"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "  ALL SYSTEMS LAUNCHED!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Check the 3 new terminal windows for live status." -ForegroundColor White
Write-Host ""
Write-Host "Wait 2-3 minutes for first trades to open." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
