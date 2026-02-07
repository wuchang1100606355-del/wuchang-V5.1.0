#!/usr/bin/env pwsh
<#
.SYNOPSIS
    自動檢查並部署 UI 變更
.DESCRIPTION
    定期比對檔案、自動同步、重啟服務
#>

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$ServerUser = "wuchang",
    [string]$ServerPath = "/home/wuchang/wuchang-v5.1.0",
    [string]$LocalPath = "$PSScriptRoot",
    [string]$LogFile = "$PSScriptRoot\auto_deploy_ui.log",
    [switch]$RestartServices,
    [switch]$DryRun
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "`n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok; Log-Message "OK: $m" }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn; Log-Message "WARN: $m" }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err; Log-Message "ERR: $m" }
function II($m) { Write-Host "  [INFO] $m" -f $colors.info; Log-Message "INFO: $m" }

function Log-Message {
    param([string]$msg)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] $msg" | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

H "UI 自動部署工具"
II "執行時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# 步驟 1: 比對檔案
H "步驟 1: 檔案比對"
try {
    & "$PSScriptRoot\compare_ui_files.ps1" -ServerIP $ServerIP -ServerUser $ServerUser -ServerPath $ServerPath -LocalPath $LocalPath
    if ($LASTEXITCODE -ne 0) {
        EE "檔案比對失敗"
        exit 1
    }
    OK "比對完成"
} catch {
    EE "比對錯誤: $_"
    exit 1
}

# 讀取比對結果
$reportFile = "$PSScriptRoot\ui_file_comparison_report.json"
if (-not (Test-Path $reportFile)) {
    EE "找不到比對報告"
    exit 1
}

$report = Get-Content $reportFile -Raw | ConvertFrom-Json

$needSync = $report.Summary.Different + $report.Summary.LocalOnly
if ($needSync -eq 0) {
    OK "沒有需要同步的檔案"
    II "所有檔案已是最新"
    exit 0
}

WW "發現 $needSync 個檔案需要同步"

# 步驟 2: 備份伺服器端檔案
H "步驟 2: 伺服器端備份"
$backupName = "ui_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$backupCmd = "cd '$ServerPath' && tar -czf /tmp/$backupName.tar.gz *.html *.css *.js 2>/dev/null && echo 'Backup created'"

if (-not $DryRun) {
    try {
        $backupResult = ssh "$ServerUser@$ServerIP" $backupCmd 2>&1
        if ($backupResult -match "Backup created") {
            OK "備份已建立: /tmp/$backupName.tar.gz"
        } else {
            WW "備份可能失敗，但繼續執行"
        }
    } catch {
        WW "無法建立備份: $_"
    }
} else {
    II "[DRY RUN] 跳過備份"
}

# 步驟 3: 同步檔案
H "步驟 3: 同步檔案"
$syncArgs = @(
    "-ServerIP", $ServerIP,
    "-ServerUser", $ServerUser,
    "-ServerPath", $ServerPath,
    "-LocalPath", $LocalPath,
    "-Direction", "push",
    "-Force"
)

if ($DryRun) {
    $syncArgs += "-DryRun"
}

try {
    & "$PSScriptRoot\sync_ui_files.ps1" @syncArgs
    if ($LASTEXITCODE -ne 0) {
        EE "同步失敗"
        exit 1
    }
    OK "同步完成"
} catch {
    EE "同步錯誤: $_"
    exit 1
}

# 步驟 4: 重啟服務 (可選)
if ($RestartServices -and -not $DryRun) {
    H "步驟 4: 重啟服務"
    
    II "重啟 Caddy 容器..."
    try {
        $restartCmd = "cd '$ServerPath' && docker-compose restart caddy 2>&1"
        $restartResult = ssh "$ServerUser@$ServerIP" $restartCmd
        
        if ($LASTEXITCODE -eq 0) {
            OK "Caddy 已重啟"
        } else {
            WW "Caddy 重啟可能失敗: $restartResult"
        }
    } catch {
        WW "無法重啟 Caddy: $_"
    }
    
    II "等待服務啟動..."
    Start-Sleep -Seconds 5
    
    # 測試服務
    try {
        $testResult = Invoke-WebRequest -Uri "http://$ServerIP" -TimeoutSec 5 -UseBasicParsing -Method Head -ErrorAction SilentlyContinue
        if ($testResult.StatusCode -eq 200) {
            OK "服務運行正常"
        } else {
            WW "服務狀態異常: $($testResult.StatusCode)"
        }
    } catch {
        WW "無法連接服務: $_"
    }
} else {
    II "跳過服務重啟 (使用 -RestartServices 啟用)"
}

# 步驟 5: 驗證部署
H "步驟 5: 驗證部署"
II "重新比對檔案..."

Start-Sleep -Seconds 2

try {
    & "$PSScriptRoot\compare_ui_files.ps1" -ServerIP $ServerIP -ServerUser $ServerUser -ServerPath $ServerPath -LocalPath $LocalPath
    $verifyReport = Get-Content $reportFile -Raw | ConvertFrom-Json
    
    if ($verifyReport.Summary.Different -eq 0 -and $verifyReport.Summary.LocalOnly -eq 0) {
        OK "驗證成功 - 所有檔案已同步"
    } else {
        WW "驗證發現 $($verifyReport.Summary.Different + $verifyReport.Summary.LocalOnly) 個檔案仍有差異"
    }
} catch {
    WW "無法驗證: $_"
}

# 結果摘要
H "部署完成"
II "執行時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
II "日誌檔案: $LogFile"

if ($DryRun) {
    WW "DRY RUN 模式 - 未實際變更任何檔案"
}

OK "部署流程結束"
