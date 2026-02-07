#!/usr/bin/env pwsh
<#
.SYNOPSIS
    智能合併 UI 檔案衝突
.DESCRIPTION
    對於有差異的檔案，提供互動式合併或自動策略
#>

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$ServerUser = "wuchang",
    [string]$ServerPath = "/home/wuchang/wuchang-v5.1.0",
    [string]$LocalPath = "$PSScriptRoot",
    [string]$ReportFile = "$PSScriptRoot\ui_file_comparison_report.json",
    [ValidateSet("local", "server", "newer", "interactive")]
    [string]$Strategy = "interactive"
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "`n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err }
function II($m) { Write-Host "  [INFO] $m" -f $colors.info }

H "UI 檔案衝突合併工具"
II "合併策略: $Strategy"

# 讀取比對報告
if (-not (Test-Path $ReportFile)) {
    EE "找不到比對報告: $ReportFile"
    II "請先執行: pwsh -File .\compare_ui_files.ps1"
    exit 1
}

$report = Get-Content $ReportFile -Raw | ConvertFrom-Json
$conflicts = $report.Details | Where-Object { $_.Status -eq "DIFFERENT" }

if ($conflicts.Count -eq 0) {
    OK "沒有衝突的檔案"
    exit 0
}

WW "發現 $($conflicts.Count) 個檔案有差異"

# 建立合併目錄
$mergeDir = "$PSScriptRoot\.ui_merge"
if (-not (Test-Path $mergeDir)) {
    New-Item -ItemType Directory -Path $mergeDir -Force | Out-Null
}

H "處理衝突"

$resolved = 0
$skipped = 0

foreach ($conflict in $conflicts) {
    Write-Host "`n$('─'*70)" -f $colors.info
    Write-Host "  檔案: $($conflict.File)" -f $colors.header
    Write-Host "  本機: $($conflict.LocalHash.Substring(0,12))... | $($conflict.LocalSize) bytes | $($conflict.LocalModified)" -f $colors.info
    Write-Host "  伺服器: $($conflict.ServerHash.Substring(0,12))..." -f $colors.info
    
    $localFile = Join-Path $LocalPath $conflict.File
    $serverFile = "$ServerPath/$($conflict.File)"
    $mergedFile = Join-Path $mergeDir $conflict.File
    
    # 下載伺服器版本
    $serverLocalCopy = "$mergeDir\server_$($conflict.File.Replace('/', '_'))"
    try {
        scp "${ServerUser}@${ServerIP}:$serverFile" "$serverLocalCopy" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            WW "無法下載伺服器版本，跳過"
            $skipped++
            continue
        }
    } catch {
        WW "下載失敗: $_"
        $skipped++
        continue
    }
    
    $decision = $null
    
    switch ($Strategy) {
        "local" {
            $decision = "keep-local"
            II "策略: 保留本機版本"
        }
        "server" {
            $decision = "keep-server"
            II "策略: 使用伺服器版本"
        }
        "newer" {
            # 比較修改時間 (需從伺服器取得)
            $serverMtime = ssh "$ServerUser@$ServerIP" "stat -c %Y '$serverFile'" 2>&1
            $localMtime = (Get-Item $localFile).LastWriteTime.ToFileTimeUtc()
            
            if ($serverMtime -gt $localMtime) {
                $decision = "keep-server"
                II "策略: 伺服器版本較新"
            } else {
                $decision = "keep-local"
                II "策略: 本機版本較新"
            }
        }
        "interactive" {
            Write-Host ""
            Write-Host "  選項:" -f $colors.warn
            Write-Host "    1) 保留本機版本" -f $colors.info
            Write-Host "    2) 使用伺服器版本" -f $colors.info
            Write-Host "    3) 顯示差異" -f $colors.info
            Write-Host "    4) 跳過此檔案" -f $colors.info
            Write-Host "    5) 使用外部編輯器合併" -f $colors.info
            
            $choice = Read-Host "`n  請選擇 (1-5)"
            
            switch ($choice) {
                "1" { $decision = "keep-local" }
                "2" { $decision = "keep-server" }
                "3" {
                    # 顯示差異
                    II "本機版本前 20 行:"
                    Get-Content $localFile -TotalCount 20 | ForEach-Object { Write-Host "    $_" -f $colors.info }
                    
                    II "`n伺服器版本前 20 行:"
                    Get-Content $serverLocalCopy -TotalCount 20 | ForEach-Object { Write-Host "    $_" -f $colors.info }
                    
                    # 再次詢問
                    $choice = Read-Host "`n  保留本機(1)或伺服器(2)? (1/2/s=skip)"
                    if ($choice -eq "1") { $decision = "keep-local" }
                    elseif ($choice -eq "2") { $decision = "keep-server" }
                    else { $decision = "skip" }
                }
                "4" { $decision = "skip" }
                "5" {
                    # 開啟編輯器
                    II "開啟檔案進行手動合併..."
                    II "本機: $localFile"
                    II "伺服器: $serverLocalCopy"
                    
                    if (Get-Command code -ErrorAction SilentlyContinue) {
                        & code --diff "$localFile" "$serverLocalCopy"
                    } elseif (Get-Command notepad++ -ErrorAction SilentlyContinue) {
                        & notepad++ "$localFile" "$serverLocalCopy"
                    } else {
                        & notepad "$localFile"
                    }
                    
                    $choice = Read-Host "`n  完成後，保留本機版本? (y/N)"
                    if ($choice -eq "y" -or $choice -eq "Y") {
                        $decision = "keep-local"
                    } else {
                        $decision = "skip"
                    }
                }
                default { $decision = "skip" }
            }
        }
    }
    
    # 執行決策
    switch ($decision) {
        "keep-local" {
            OK "保留本機版本並上傳到伺服器"
            $serverDir = Split-Path $serverFile -Parent
            ssh "$ServerUser@$ServerIP" "mkdir -p '$serverDir'" 2>$null
            scp "$localFile" "${ServerUser}@${ServerIP}:$serverFile" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                OK "已同步"
                $resolved++
            } else {
                EE "上傳失敗"
                $skipped++
            }
        }
        "keep-server" {
            OK "使用伺服器版本並下載到本機"
            $localDir = Split-Path $localFile -Parent
            if (-not (Test-Path $localDir)) {
                New-Item -ItemType Directory -Path $localDir -Force | Out-Null
            }
            Copy-Item $serverLocalCopy $localFile -Force
            OK "已同步"
            $resolved++
        }
        "skip" {
            WW "跳過此檔案"
            $skipped++
        }
    }
    
    # 清理臨時檔案
    if (Test-Path $serverLocalCopy) {
        Remove-Item $serverLocalCopy -Force
    }
}

# 結果摘要
H "合併結果"
Write-Host ""
Write-Host "  已處理: $resolved" -f $colors.ok
Write-Host "  已跳過: $skipped" -f $colors.warn
Write-Host ""

if ($resolved -gt 0) {
    OK "合併完成"
    II "建議重新比對: pwsh -File .\compare_ui_files.ps1"
}
