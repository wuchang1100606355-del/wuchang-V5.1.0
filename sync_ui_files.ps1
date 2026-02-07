#!/usr/bin/env pwsh
<#
.SYNOPSIS
    批次同步 UI 檔案到伺服器或從伺服器拉取
.DESCRIPTION
    根據比對報告，批次上傳/下載檔案
#>

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$ServerUser = "wuchang",
    [string]$ServerPath = "/home/wuchang/wuchang-v5.1.0",
    [string]$LocalPath = "$PSScriptRoot",
    [ValidateSet("push", "pull", "sync")]
    [string]$Direction = "push",
    [string]$ReportFile = "$PSScriptRoot\ui_file_comparison_report.json",
    [switch]$DryRun,
    [switch]$Force
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "`n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err }
function II($m) { Write-Host "  [INFO] $m" -f $colors.info }

H "UI 檔案批次同步工具 - $Direction"

# 讀取比對報告
if (-not (Test-Path $ReportFile)) {
    EE "找不到比對報告: $ReportFile"
    II "請先執行: pwsh -File .\compare_ui_files.ps1"
    exit 1
}

$report = Get-Content $ReportFile -Raw | ConvertFrom-Json
II "載入比對報告: $($report.Timestamp)"

$syncList = @()

switch ($Direction) {
    "push" {
        # 上傳：LOCAL_ONLY + DIFFERENT (本機為主)
        $syncList = $report.Details | Where-Object { 
            $_.Status -eq "LOCAL_ONLY" -or ($_.Status -eq "DIFFERENT" -and -not $Force)
        }
        if ($Force) {
            $syncList = $report.Details | Where-Object { 
                $_.Status -eq "LOCAL_ONLY" -or $_.Status -eq "DIFFERENT"
            }
        }
        II "準備上傳 $($syncList.Count) 個檔案到伺服器"
    }
    "pull" {
        # 下載：SERVER_ONLY + DIFFERENT (伺服器為主)
        $syncList = $report.Details | Where-Object { 
            $_.Status -eq "SERVER_ONLY" -or ($_.Status -eq "DIFFERENT" -and -not $Force)
        }
        if ($Force) {
            $syncList = $report.Details | Where-Object { 
                $_.Status -eq "SERVER_ONLY" -or $_.Status -eq "DIFFERENT"
            }
        }
        II "準備從伺服器下載 $($syncList.Count) 個檔案"
    }
    "sync" {
        # 雙向同步：以較新的為準
        $syncList = $report.Details | Where-Object { 
            $_.Status -ne "IDENTICAL"
        }
        II "準備雙向同步 $($syncList.Count) 個檔案"
    }
}

if ($syncList.Count -eq 0) {
    OK "沒有需要同步的檔案"
    exit 0
}

# 顯示同步清單
H "同步清單"
$syncList | Select-Object -First 20 | ForEach-Object {
    $statusColor = switch ($_.Status) {
        "DIFFERENT" { $colors.warn }
        "LOCAL_ONLY" { $colors.info }
        "SERVER_ONLY" { $colors.info }
        default { $colors.info }
    }
    Write-Host "  [$($_.Status)] $($_.File)" -f $statusColor
}
if ($syncList.Count -gt 20) {
    II "... 還有 $($syncList.Count - 20) 個檔案"
}

if ($DryRun) {
    WW "DRY RUN 模式 - 不會實際傳輸檔案"
} else {
    Write-Host ""
    if (-not $Force) {
        $confirm = Read-Host "確定要同步這些檔案? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            II "已取消"
            exit 0
        }
    }
}

# 執行同步
H "開始同步"
$success = 0
$failed = 0
$skipped = 0

foreach ($item in $syncList) {
    $localFile = Join-Path $LocalPath $item.File
    $serverFile = "$ServerPath/$($item.File)"
    
    try {
        if ($Direction -eq "push" -or ($Direction -eq "sync" -and $item.Status -eq "LOCAL_ONLY")) {
            # 上傳到伺服器
            Write-Host "`n  上傳: $($item.File)" -f $colors.info
            
            if (-not (Test-Path $localFile)) {
                WW "本機檔案不存在，跳過"
                $skipped++
                continue
            }
            
            if ($DryRun) {
                II "[DRY RUN] scp '$localFile' '$ServerUser@${ServerIP}:$serverFile'"
                $success++
            } else {
                # 確保伺服器端目錄存在
                $serverDir = Split-Path $serverFile -Parent
                ssh "$ServerUser@$ServerIP" "mkdir -p '$serverDir'" 2>$null
                
                # 上傳
                scp "$localFile" "${ServerUser}@${ServerIP}:$serverFile" 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    OK "上傳成功"
                    $success++
                } else {
                    EE "上傳失敗"
                    $failed++
                }
            }
        }
        elseif ($Direction -eq "pull" -or ($Direction -eq "sync" -and $item.Status -eq "SERVER_ONLY")) {
            # 從伺服器下載
            Write-Host "`n  下載: $($item.File)" -f $colors.info
            
            if ($DryRun) {
                II "[DRY RUN] scp '$ServerUser@${ServerIP}:$serverFile' '$localFile'"
                $success++
            } else {
                # 確保本機目錄存在
                $localDir = Split-Path $localFile -Parent
                if (-not (Test-Path $localDir)) {
                    New-Item -ItemType Directory -Path $localDir -Force | Out-Null
                }
                
                # 下載
                scp "${ServerUser}@${ServerIP}:$serverFile" "$localFile" 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    OK "下載成功"
                    $success++
                } else {
                    EE "下載失敗"
                    $failed++
                }
            }
        }
        elseif ($item.Status -eq "DIFFERENT") {
            # 處理衝突檔案
            if ($Direction -eq "sync") {
                WW "檔案有差異，需要手動處理: $($item.File)"
                $skipped++
            } elseif ($Direction -eq "push") {
                Write-Host "`n  強制上傳: $($item.File)" -f $colors.warn
                if (-not $DryRun) {
                    $serverDir = Split-Path $serverFile -Parent
                    ssh "$ServerUser@$ServerIP" "mkdir -p '$serverDir'" 2>$null
                    scp "$localFile" "${ServerUser}@${ServerIP}:$serverFile" 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) { OK "上傳成功"; $success++ } else { EE "上傳失敗"; $failed++ }
                } else {
                    $success++
                }
            } elseif ($Direction -eq "pull") {
                Write-Host "`n  強制下載: $($item.File)" -f $colors.warn
                if (-not $DryRun) {
                    $localDir = Split-Path $localFile -Parent
                    if (-not (Test-Path $localDir)) { New-Item -ItemType Directory -Path $localDir -Force | Out-Null }
                    scp "${ServerUser}@${ServerIP}:$serverFile" "$localFile" 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) { OK "下載成功"; $success++ } else { EE "下載失敗"; $failed++ }
                } else {
                    $success++
                }
            }
        }
    } catch {
        EE "錯誤: $_"
        $failed++
    }
}

# 結果摘要
H "同步結果"
Write-Host ""
Write-Host "  成功: $success" -f $colors.ok
Write-Host "  失敗: $failed" -f $colors.err
Write-Host "  跳過: $skipped" -f $colors.warn
Write-Host ""

if ($failed -eq 0) {
    OK "同步完成！"
    if (-not $DryRun) {
        II "建議重新執行比對: pwsh -File .\compare_ui_files.ps1"
    }
} else {
    WW "部分檔案同步失敗，請檢查錯誤訊息"
}
