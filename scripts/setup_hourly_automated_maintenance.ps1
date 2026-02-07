# 設定每小時自動維護任務
# 功能：建立 Windows Task Scheduler 任務，每小時執行一次系統維護

function Log-Message {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    $icons = @{
        "INFO" = "ℹ️"
        "OK" = "✅"
        "WARN" = "⚠️"
        "ERROR" = "❌"
        "PROGRESS" = "🔄"
    }
    $icon = $icons.($Level)
    Write-Host "$icon [$Level] $Message"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "設定每小時自動維護任務" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Log-Message "檢查管理員權限..." "INFO"
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Log-Message "此腳本需要管理員權限才能建立排程任務" "ERROR"
    Log-Message "請以管理員身份重新執行此腳本" "INFO"
    exit 1
}
Log-Message "✓ 已具備管理員權限" "OK"

Write-Host ""
Log-Message "設定自動維護任務..." "PROGRESS"

# 取得腳本目錄
$scriptDir = Split-Path $MyInvocation.MyCommand.Path
$maintenanceScript = Join-Path $scriptDir "double_j_maintenance_workflow.py"

if (-not (Test-Path $maintenanceScript)) {
    Log-Message "維護腳本不存在: $maintenanceScript" "ERROR"
    exit 1
}

# Python 路徑（需要根據實際環境調整）
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    $pythonPath = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $pythonPath) {
    Log-Message "未找到 Python 解釋器" "ERROR"
    exit 1
}

Log-Message "Python 路徑: $pythonPath" "INFO"

# 任務名稱
$taskName = "雙J系統每小時維護"

# 刪除現有任務（如果存在）
Log-Message "檢查現有任務..." "INFO"
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Log-Message "刪除現有任務..." "INFO"
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Log-Message "✓ 已刪除現有任務" "OK"
}

# 建立新任務
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$maintenanceScript`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "雙J工作小組每小時自動維護任務"
    Log-Message "✓ 自動維護任務已建立" "OK"
    Log-Message "任務名稱: $taskName" "INFO"
    Log-Message "執行頻率: 每小時一次" "INFO"
} catch {
    Log-Message "建立任務失敗: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-Host ""
Log-Message "========================================" -ForegroundColor Green
Write-Host "✅ 自動維護任務設定完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Log-Message "驗證任務..." "INFO"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    Log-Message "✓ 任務驗證成功" "OK"
    Write-Host ""
    Write-Host "任務資訊：" -ForegroundColor Cyan
    Write-Host "  名稱: $($task.TaskName)" -ForegroundColor White
    Write-Host "  狀態: $($task.State)" -ForegroundColor White
    Write-Host "  下次執行: $((Get-ScheduledTaskInfo -TaskName $taskName).NextRunTime)" -ForegroundColor White
}
