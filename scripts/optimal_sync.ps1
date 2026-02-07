# 最優同步腳本
# 執行最優同步策略，從 UI 筆電接收檔案

param(
    [string]$RemoteIP = "192.168.50.84",
    [string]$RemotePath = "",
    [ValidateSet("newer", "larger")]
    [string]$Strategy = "newer",
    [ValidateSet("base1", "base2", "bidirectional")]
    [string]$SyncTo = "base1",
    [switch]$DryRun = $false
)

Write-Host "=== 最優同步工具 ===" -ForegroundColor Cyan

# 1. 檢測遠端路徑
Write-Host "`n[1] 檢測遠端路徑..." -ForegroundColor Yellow

if (-not $RemotePath) {
    # 嘗試常見的共享路徑
    $shareNames = @("wuchang", "C$", "Users", "share")
    $foundPath = $null
    
    foreach ($share in $shareNames) {
        $testPath = "\\$RemoteIP\$share"
        Write-Host "  檢查 $testPath..." -ForegroundColor Gray
        if (Test-Path $testPath -ErrorAction SilentlyContinue) {
            if ($share -eq "wuchang") {
                $foundPath = $testPath
            } elseif ($share -eq "C$" -or $share -eq "Users") {
                $wuchangPath = Join-Path $testPath "wuchang"
                if (Test-Path $wuchangPath -ErrorAction SilentlyContinue) {
                    $foundPath = $wuchangPath
                }
            } else {
                $foundPath = $testPath
            }
            
            if ($foundPath) {
                Write-Host "  ✓ 找到共享路徑: $foundPath" -ForegroundColor Green
                $RemotePath = $foundPath
                break
            }
        }
    }
    
    if (-not $RemotePath) {
        Write-Host "  ❌ 未找到共享路徑" -ForegroundColor Red
        Write-Host "`n請手動指定遠端路徑：" -ForegroundColor Yellow
        Write-Host "  .\scripts\optimal_sync.ps1 -RemotePath '\\192.168.50.84\wuchang'" -ForegroundColor Cyan
        exit 1
    }
} else {
    Write-Host "  使用指定的路徑: $RemotePath" -ForegroundColor Green
}

# 2. 檢查連接性
Write-Host "`n[2] 檢查連接性..." -ForegroundColor Yellow
try {
    $result = Test-Connection -ComputerName $RemoteIP -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($result) {
        Write-Host "  ✓ 設備在線: $RemoteIP" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ 設備可能離線: $RemoteIP" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ 無法檢查連接性" -ForegroundColor Yellow
}

# 3. 執行最優同步
Write-Host "`n[3] 執行最優同步..." -ForegroundColor Yellow
Write-Host "  本地路徑: $(Get-Location)" -ForegroundColor Cyan
Write-Host "  遠端路徑: $RemotePath" -ForegroundColor Cyan
Write-Host "  同步策略: $Strategy" -ForegroundColor Cyan
Write-Host "  同步方向: $SyncTo" -ForegroundColor Cyan
Write-Host "  執行模式: $(if ($DryRun) { '預覽 (Dry-Run)' } else { '實際同步' })" -ForegroundColor Cyan

$localPath = Get-Location
$dryRunFlag = if ($DryRun) { "--dry-run" } else { "" }

Write-Host "`n  執行命令: python scripts/compare_and_sync_bases.py ..." -ForegroundColor Gray

$cmdArgs = @(
    "--base1", $localPath
    "--base2", $RemotePath
    "--base1-name", "本地基地端"
    "--base2-name", "UI筆電基地端"
    "--sync-to", $SyncTo
    "--strategy", $Strategy
)

if ($DryRun) {
    $cmdArgs += "--dry-run"
}

$output = & python scripts/compare_and_sync_bases.py $cmdArgs 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  ✓ 最優同步完成！" -ForegroundColor Green
    Write-Host $output
} else {
    Write-Host "`n  ❌ 最優同步失敗" -ForegroundColor Red
    Write-Host $output
    exit 1
}

Write-Host "`n=== 完成 ===" -ForegroundColor Cyan
