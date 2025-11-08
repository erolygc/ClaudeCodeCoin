# Watch Logs - Windows PowerShell Script
# Usage: .\watch_logs.ps1 [log_file]

param(
    [string]$LogFile = "logs\paper_trading.log"
)

Write-Host "📊 Watching: $LogFile" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Get initial file size
if (Test-Path $LogFile) {
    $lastSize = (Get-Item $LogFile).Length
} else {
    Write-Host "⚠️  Log file not found yet. Waiting..." -ForegroundColor Yellow
    $lastSize = 0
}

# Watch for changes
while ($true) {
    if (Test-Path $LogFile) {
        $currentSize = (Get-Item $LogFile).Length

        if ($currentSize -gt $lastSize) {
            # Read new content
            $content = Get-Content $LogFile -Tail 20
            $content | ForEach-Object {
                if ($_ -match "ERROR") {
                    Write-Host $_ -ForegroundColor Red
                } elseif ($_ -match "WARNING") {
                    Write-Host $_ -ForegroundColor Yellow
                } elseif ($_ -match "✅|SUCCESS") {
                    Write-Host $_ -ForegroundColor Green
                } else {
                    Write-Host $_
                }
            }

            $lastSize = $currentSize
        }
    }

    Start-Sleep -Seconds 2
}
