param(
    [string]$ServerIP = "192.168.50.84",
    [string]$ServerUser = "wuchang",
    [string]$ServerPath = "/home/wuchang/wuchang-v5.1.0",
    [string]$LocalPath = "C:\wuchang V5.1.0"
)

Write-Host "`n=== UI File Comparison ===" -ForegroundColor Cyan
Write-Host "Server: $ServerUser@$ServerIP" -ForegroundColor Gray
Write-Host "Path: $ServerPath`n" -ForegroundColor Gray

# Test SSH
Write-Host "[INFO] Testing SSH connection..." -ForegroundColor Yellow
$testSSH = ssh -o ConnectTimeout=5 -o BatchMode=yes "$ServerUser@$ServerIP" "echo OK" 2>&1
if ($testSSH -notmatch "OK") {
    Write-Host "[ERROR] Cannot connect to server" -ForegroundColor Red
    Write-Host "Run: ssh $ServerUser@$ServerIP" -ForegroundColor Gray
    exit 1
}
Write-Host "[OK] SSH connected`n" -ForegroundColor Green

# Scan local files
Write-Host "[INFO] Scanning local HTML/CSS/JS files..." -ForegroundColor Yellow
$localFiles = @()
$patterns = @("*.html", "*.css", "*.js")
$exclude = @("node_modules", ".git", "venv", "USB_DRIVE")

foreach ($pattern in $patterns) {
    Get-ChildItem -Path $LocalPath -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue | 
        Where-Object { 
            $skip = $false
            foreach ($ex in $exclude) {
                if ($_.FullName -like "*\$ex\*") { $skip = $true; break }
            }
            -not $skip
        } | ForEach-Object {
            $rel = $_.FullName.Replace($LocalPath, "").TrimStart("\", "/").Replace("\", "/")
            $hash = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash
            $localFiles += [PSCustomObject]@{
                Path = $rel
                Hash = $hash
                Size = $_.Length
            }
        }
}

Write-Host "[OK] Found $($localFiles.Count) local files`n" -ForegroundColor Green

# Compare
Write-Host "[INFO] Comparing with server..." -ForegroundColor Yellow
$report = @{
    Identical = 0
    Different = 0
    LocalOnly = 0
    Errors = 0
    Files = @()
}

foreach ($file in $localFiles) {
    $serverFile = "$ServerPath/$($file.Path)"
    Write-Host "  Checking: $($file.Path)" -NoNewline
    
    try {
        $exists = ssh "$ServerUser@$ServerIP" "test -f '$serverFile' && echo yes || echo no" 2>&1
        
        if ($exists -match "yes") {
            $serverHash = ssh "$ServerUser@$ServerIP" "sha256sum '$serverFile'" 2>&1
            $serverHash = ($serverHash -split '\s+')[0].ToUpper()
            
            if ($file.Hash -eq $serverHash) {
                Write-Host " [SAME]" -ForegroundColor Green
                $report.Identical++
                $status = "IDENTICAL"
            } else {
                Write-Host " [DIFF]" -ForegroundColor Yellow
                $report.Different++
                $status = "DIFFERENT"
            }
            
            $report.Files += [PSCustomObject]@{
                File = $file.Path
                Status = $status
                LocalHash = $file.Hash.Substring(0,12)
                ServerHash = $serverHash.Substring(0,12)
            }
        } else {
            Write-Host " [LOCAL_ONLY]" -ForegroundColor Cyan
            $report.LocalOnly++
            $report.Files += [PSCustomObject]@{
                File = $file.Path
                Status = "LOCAL_ONLY"
                LocalHash = $file.Hash.Substring(0,12)
                ServerHash = "N/A"
            }
        }
    } catch {
        Write-Host " [ERROR]" -ForegroundColor Red
        $report.Errors++
    }
}

# Save report
$reportFile = "$LocalPath\ui_comparison_report.json"
$report | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportFile -Encoding UTF8
Write-Host "`n[OK] Report saved: $reportFile" -ForegroundColor Green

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "  Total:      $($localFiles.Count)" -ForegroundColor Gray
Write-Host "  Identical:  $($report.Identical)" -ForegroundColor Green
Write-Host "  Different:  $($report.Different)" -ForegroundColor Yellow
Write-Host "  Local Only: $($report.LocalOnly)" -ForegroundColor Cyan
Write-Host "  Errors:     $($report.Errors)" -ForegroundColor Red

# Auto sync if needed
$needSync = $report.Different + $report.LocalOnly
if ($needSync -gt 0) {
    Write-Host "`n[ACTION] $needSync files need sync" -ForegroundColor Yellow
    $confirm = Read-Host "Sync to server with backup? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        # Backup first
        $backupName = "ui_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Write-Host "`n[INFO] Creating server backup..." -ForegroundColor Yellow
        ssh "$ServerUser@$ServerIP" "cd '$ServerPath' && tar -czf /tmp/$backupName.tar.gz *.html *.css *.js 2>/dev/null && echo 'Backup OK'" 2>&1 | Out-Null
        Write-Host "[OK] Backup: /tmp/$backupName.tar.gz" -ForegroundColor Green
        
        # Sync files
        Write-Host "`n[INFO] Syncing files..." -ForegroundColor Yellow
        $synced = 0
        foreach ($item in $report.Files) {
            if ($item.Status -eq "DIFFERENT" -or $item.Status -eq "LOCAL_ONLY") {
                $localFile = Join-Path $LocalPath $item.File
                $serverFile = "$ServerPath/$($item.File)"
                
                Write-Host "  Upload: $($item.File)" -NoNewline
                $serverDir = Split-Path $serverFile -Parent
                ssh "$ServerUser@$ServerIP" "mkdir -p '$serverDir'" 2>&1 | Out-Null
                scp "$localFile" "${ServerUser}@${ServerIP}:$serverFile" 2>&1 | Out-Null
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host " [OK]" -ForegroundColor Green
                    $synced++
                } else {
                    Write-Host " [FAIL]" -ForegroundColor Red
                }
            }
        }
        
        Write-Host "`n[DONE] Synced $synced/$needSync files" -ForegroundColor Green
        Write-Host "Rollback: ssh $ServerUser@$ServerIP 'cd $ServerPath && tar -xzf /tmp/$backupName.tar.gz'" -ForegroundColor Gray
    }
} else {
    Write-Host "`n[OK] All files are in sync" -ForegroundColor Green
}
