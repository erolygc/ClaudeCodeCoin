# ClaudeCodeCoin - Show Running Systems
# Displays all running trading system components

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " CLAUDECODECOIN - RUNNING SYSTEMS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Get all Python processes
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "🐍 Python Processes:" -ForegroundColor Green
    Write-Host ""

    $pythonProcesses | ForEach-Object {
        $processId = $_.Id
        $processName = $_.ProcessName
        $startTime = $_.StartTime
        $cpuTime = $_.CPU
        $memoryMB = [math]::Round($_.WorkingSet64 / 1MB, 2)

        # Try to get command line
        try {
            $commandLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $processId").CommandLine

            # Identify component
            $component = "Unknown"
            if ($commandLine -like "*realtime_hybrid_scanner*") {
                $component = "Hybrid Scanner"
                Write-Host "  🔍 $component" -ForegroundColor Yellow
            }
            elseif ($commandLine -like "*paper_trading_futures_engine*") {
                $component = "Paper Trading Engine"
                Write-Host "  💰 $component" -ForegroundColor Green
            }
            elseif ($commandLine -like "*streamlit*" -or $commandLine -like "*dashboard*") {
                $component = "Trading Dashboard"
                Write-Host "  📊 $component" -ForegroundColor Magenta
            }
            else {
                Write-Host "  ❓ Other Python Process" -ForegroundColor Gray
            }

            Write-Host "     PID: $processId" -ForegroundColor White
            Write-Host "     Started: $startTime" -ForegroundColor Gray
            Write-Host "     CPU Time: $([math]::Round($cpuTime, 2))s" -ForegroundColor Gray
            Write-Host "     Memory: ${memoryMB} MB" -ForegroundColor Gray
            Write-Host "     Command: $commandLine" -ForegroundColor DarkGray
            Write-Host ""
        }
        catch {
            Write-Host "  ❓ Python Process (PID: $processId)" -ForegroundColor Gray
            Write-Host "     Memory: ${memoryMB} MB" -ForegroundColor Gray
            Write-Host ""
        }
    }

    Write-Host "Total Python Processes: $($pythonProcesses.Count)" -ForegroundColor Cyan
}
else {
    Write-Host "❌ No Python processes running" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " DASHBOARD STATUS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Streamlit dashboard is accessible
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Dashboard is RUNNING at http://localhost:8501" -ForegroundColor Green
}
catch {
    Write-Host "❌ Dashboard is NOT accessible" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " QUICK ACTIONS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Stop all Python processes:" -ForegroundColor Yellow
Write-Host "  Stop-Process -Name python -Force" -ForegroundColor White
Write-Host ""

Write-Host "Watch logs:" -ForegroundColor Yellow
Write-Host "  .\watch_logs.ps1 logs\paper_trading.log" -ForegroundColor White
Write-Host "  .\watch_logs.ps1 logs\realtime_hybrid_scanner.log" -ForegroundColor White
Write-Host ""

Write-Host "Open dashboard:" -ForegroundColor Yellow
Write-Host "  start http://localhost:8501" -ForegroundColor White
Write-Host ""

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
