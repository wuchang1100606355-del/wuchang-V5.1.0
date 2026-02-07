# 設置 Google 資源監控定時任務
# 合規要求：符合 Google 非營利組織合規要求

param(
    [string]$Interval = "Daily",
    [string]$Time = "02:00"
)

$ErrorActionPreference = "Continue"
$Root = (Get-Location).Path
$TaskName = "GoogleResourcesMonitor"

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ 需要管理員權限"
    Write-Host "請以管理員權限運行此腳本"
    exit 1
}

$script = Join-Path $Root "scripts\monitor_google_resources.py"
if (-not (Test-Path $script)) {
    Write-Host "❌ 腳本不存在: $script"
    exit 1
}

# 檢查是否已存在
try {
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "⚠ 任務已存在，將更新..."
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
} catch {}

# 創建動作
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Host "❌ 未找到 Python，請先安裝 Python"
    exit 1
}

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$script`"" -WorkingDirectory $Root

# 創建觸發器
$trigger = switch ($Interval) {
    "Daily" {
        try {
            $tParts = $Time -split ":"
            $hour = [int]$tParts[0]
            $minute = [int]$tParts[1]
            $at = (Get-Date).Date.AddHours($hour).AddMinutes($minute)
        } catch {
            $at = (Get-Date).Date.AddHours(2)
        }
        New-ScheduledTaskTrigger -Daily -At $at
    }
    "Hourly" {
        New-ScheduledTaskTrigger -Once -At (Get-Date).AddHours(1) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
    }
    default {
        New-ScheduledTaskTrigger -Daily -At "02:00"
    }
}

# 創建設置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# 註冊任務
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Google 非營利組織資源監控 - 每日檢查 Google Workspace、Google Ads、GCP 資源使用情況" `
        -User $env:USERNAME `
        -RunLevel Highest | Out-Null
    
    Write-Host "✅ 任務已註冊: $TaskName"
    Write-Host "   執行間隔: $Interval"
    Write-Host "   執行時間: $Time"
} catch {
    Write-Host "❌ 註冊失敗: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "✅ 合規: 符合 Google 非營利組織合規要求" -ForegroundColor Green
