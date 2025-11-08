# ClaudeCodeCoin - Project Cleanup Script
# Cleans temporary files, old logs, and unused data

param(
    [switch]$DryRun,  # Sadece göster, silme
    [switch]$Deep     # Derin temizlik (backup klasörleri dahil)
)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  CLAUDECODECOIN - PROJECT CLEANUP" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n[DRY RUN MODE] Silme islemi yapilmayacak, sadece listeleme" -ForegroundColor Yellow
}

$totalCleaned = 0
$filesRemoved = 0

# ============================================================================
# 1. PYTHON CACHE DOSYALARI
# ============================================================================

Write-Host "`n[1/8] Python cache dosyalari temizleniyor..." -ForegroundColor Yellow

$pycacheItems = Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
$pycFiles = Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue

$cacheCount = $pycacheItems.Count + $pycFiles.Count

if ($cacheCount -gt 0) {
    Write-Host "  Bulundu: $cacheCount cache dosyasi/klasoru" -ForegroundColor White

    if (-not $DryRun) {
        $pycacheItems | Remove-Item -Recurse -Force
        $pycFiles | Remove-Item -Force
        Write-Host "  ✓ Python cache temizlendi" -ForegroundColor Green
        $filesRemoved += $cacheCount
    }
} else {
    Write-Host "  ✓ Python cache temiz" -ForegroundColor Green
}

# ============================================================================
# 2. ESKI LOG DOSYALARI (>7 gün)
# ============================================================================

Write-Host "`n[2/8] Eski log dosyalari temizleniyor..." -ForegroundColor Yellow

$sevenDaysAgo = (Get-Date).AddDays(-7)
$oldLogs = Get-ChildItem -Path . -Recurse -File -Filter "*.log" -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt $sevenDaysAgo }

if ($oldLogs.Count -gt 0) {
    $logSize = ($oldLogs | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  Bulundu: $($oldLogs.Count) eski log dosyasi ($([math]::Round($logSize, 2)) MB)" -ForegroundColor White

    if (-not $DryRun) {
        $oldLogs | Remove-Item -Force
        Write-Host "  ✓ Eski loglar silindi" -ForegroundColor Green
        $filesRemoved += $oldLogs.Count
        $totalCleaned += $logSize
    }
} else {
    Write-Host "  ✓ Eski log yok" -ForegroundColor Green
}

# ============================================================================
# 3. ESKI PUMP ALERTS (Bugünkü hariç)
# ============================================================================

Write-Host "`n[3/8] Eski pump alerts temizleniyor..." -ForegroundColor Yellow

$today = Get-Date -Format "yyyyMMdd"
$alertsPath = "pump_alerts"

if (Test-Path $alertsPath) {
    $oldAlerts = Get-ChildItem "$alertsPath\*.json" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notmatch $today }

    if ($oldAlerts.Count -gt 0) {
        $alertSize = ($oldAlerts | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  Bulundu: $($oldAlerts.Count) eski alert dosyasi ($([math]::Round($alertSize, 2)) MB)" -ForegroundColor White

        if (-not $DryRun) {
            $oldAlerts | Remove-Item -Force
            Write-Host "  ✓ Eski alerts silindi (bugunki korundu)" -ForegroundColor Green
            $filesRemoved += $oldAlerts.Count
            $totalCleaned += $alertSize
        }
    } else {
        Write-Host "  ✓ Eski alert yok (bugunki korundu)" -ForegroundColor Green
    }
}

# ============================================================================
# 4. BACKUP KLASÖRLERI (Sadece Deep mode)
# ============================================================================

Write-Host "`n[4/8] Backup klasorleri kontrol ediliyor..." -ForegroundColor Yellow

$backupDirs = Get-ChildItem -Path . -Directory -Filter "backup*" -ErrorAction SilentlyContinue

if ($backupDirs.Count -gt 0) {
    $backupSize = 0
    foreach ($dir in $backupDirs) {
        $backupSize += (Get-ChildItem -Path $dir.FullName -Recurse -File -ErrorAction SilentlyContinue |
            Measure-Object -Property Length -Sum).Sum
    }
    $backupSize = $backupSize / 1MB

    Write-Host "  Bulundu: $($backupDirs.Count) backup klasoru ($([math]::Round($backupSize, 2)) MB)" -ForegroundColor White

    if ($Deep) {
        if (-not $DryRun) {
            $backupDirs | Remove-Item -Recurse -Force
            Write-Host "  ✓ Backup klasorleri silindi" -ForegroundColor Green
            $filesRemoved += $backupDirs.Count
            $totalCleaned += $backupSize
        }
    } else {
        Write-Host "  ⊘ Atlandı (Deep mode gerekli: -Deep)" -ForegroundColor Yellow
    }
}

# ============================================================================
# 5. TEST DOSYALARI (Root'ta)
# ============================================================================

Write-Host "`n[5/8] Test dosyalari kontrol ediliyor..." -ForegroundColor Yellow

$testFiles = Get-ChildItem -Path . -File -Filter "test_*.py" -ErrorAction SilentlyContinue
$testFiles += Get-ChildItem -Path . -File -Filter "TEST_*.py" -ErrorAction SilentlyContinue

if ($testFiles.Count -gt 0) {
    Write-Host "  Bulundu: $($testFiles.Count) test dosyasi (root'ta)" -ForegroundColor White
    Write-Host "  ⊘ Korundu (tests/ klasorune tasinabilir)" -ForegroundColor Yellow

    # Test dosyalarını silmiyoruz, sadece bilgi veriyoruz
    Write-Host "  Tavsiye: Bu dosyalari tests/ klasorune tasiyin" -ForegroundColor Cyan
}

# ============================================================================
# 6. GEÇİCİ VERİTABANLARI
# ============================================================================

Write-Host "`n[6/8] Gecici veritabanlari kontrol ediliyor..." -ForegroundColor Yellow

$tempDbs = @(
    "Phase7_PaperTrading\data_output\paper_trading.db.bak",
    "Phase8_FuturesTrading\data_output\futures_trading.db.bak"
)

$foundTempDbs = $tempDbs | Where-Object { Test-Path $_ }

if ($foundTempDbs.Count -gt 0) {
    Write-Host "  Bulundu: $($foundTempDbs.Count) gecici veritabani" -ForegroundColor White

    if (-not $DryRun) {
        $foundTempDbs | ForEach-Object { Remove-Item $_ -Force }
        Write-Host "  ✓ Gecici veritabanlari silindi" -ForegroundColor Green
        $filesRemoved += $foundTempDbs.Count
    }
} else {
    Write-Host "  ✓ Gecici veritabani yok" -ForegroundColor Green
}

# ============================================================================
# 7. WINDOWS ÖZEL DOSYALAR
# ============================================================================

Write-Host "`n[7/8] Windows ozel dosyalari temizleniyor..." -ForegroundColor Yellow

$winFiles = @()
$winFiles += Get-ChildItem -Path . -Recurse -File -Filter "Thumbs.db" -ErrorAction SilentlyContinue
$winFiles += Get-ChildItem -Path . -Recurse -File -Filter "desktop.ini" -ErrorAction SilentlyContinue
$winFiles += Get-ChildItem -Path . -Recurse -File -Filter "*.tmp" -ErrorAction SilentlyContinue

if ($winFiles.Count -gt 0) {
    Write-Host "  Bulundu: $($winFiles.Count) Windows ozel dosyasi" -ForegroundColor White

    if (-not $DryRun) {
        $winFiles | Remove-Item -Force
        Write-Host "  ✓ Windows dosyalari silindi" -ForegroundColor Green
        $filesRemoved += $winFiles.Count
    }
} else {
    Write-Host "  ✓ Windows ozel dosyasi yok" -ForegroundColor Green
}

# ============================================================================
# 8. BOŞ KLASÖRLER
# ============================================================================

Write-Host "`n[8/8] Bos klasorler kontrol ediliyor..." -ForegroundColor Yellow

$emptyDirs = Get-ChildItem -Path . -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object {
        $_.GetFiles().Count -eq 0 -and
        $_.GetDirectories().Count -eq 0 -and
        $_.Name -ne ".git"
    }

if ($emptyDirs.Count -gt 0) {
    Write-Host "  Bulundu: $($emptyDirs.Count) bos klasor" -ForegroundColor White

    if (-not $DryRun) {
        $emptyDirs | Remove-Item -Force
        Write-Host "  ✓ Bos klasorler silindi" -ForegroundColor Green
        $filesRemoved += $emptyDirs.Count
    }
} else {
    Write-Host "  ✓ Bos klasor yok" -ForegroundColor Green
}

# ============================================================================
# ÖZET
# ============================================================================

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "  TEMIZLIK TAMAMLANDI!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n[DRY RUN] Gercek temizlik yapmak icin:" -ForegroundColor Yellow
    Write-Host "  .\CLEANUP_PROJECT.ps1" -ForegroundColor White
    Write-Host "  .\CLEANUP_PROJECT.ps1 -Deep  (backup'lari da sil)" -ForegroundColor White
} else {
    Write-Host "`nDosya Sayisi: $filesRemoved" -ForegroundColor Cyan
    Write-Host "Toplam Alan: $([math]::Round($totalCleaned, 2)) MB" -ForegroundColor Cyan

    if ($filesRemoved -eq 0) {
        Write-Host "`nProje zaten temiz! ✓" -ForegroundColor Green
    }
}

Write-Host "`nTavsiyeler:" -ForegroundColor Yellow
Write-Host "  - Test dosyalarini tests/ klasorune tasiyin" -ForegroundColor White
Write-Host "  - Eski veritabanlarini yedekleyin" -ForegroundColor White
Write-Host "  - Git commit yapmadan once kontrol edin" -ForegroundColor White

Write-Host ""
