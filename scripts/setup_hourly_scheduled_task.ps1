# 設定每小時時間排程工作
# 使用 Windows Task Scheduler 設定每小時執行的任務

param(
    [Parameter(Mandatory=$false)]
    [string]$TaskName = "WuchangHourlyCheck",
    
    [Parameter(Mandatory=$false)]
    [string]$ScriptPath = "scripts\run_hourly_check.bat",
    
    [Parameter(Mandatory=$false)]
    [string]$WorkingDirectory = (Get-Location).Path,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

Write-Host "=== 設定每小時時間排程工作 ===" -ForegroundColor Cyan

# 1. 檢查腳本檔案
Write-Host "`n[1] 檢查腳本檔案..." -ForegroundColor Yellow

$scriptFullPath = Join-Path $WorkingDirectory $ScriptPath
if (-not (Test-Path $scriptFullPath)) {
    Write-Host "  ⚠ 腳本檔案不存在: $scriptFullPath" -ForegroundColor Yellow
    Write-Host "    請確認腳本路徑正確" -ForegroundColor Cyan
    exit 1
}

Write-Host "  ✓ 腳本檔案存在: $scriptFullPath" -ForegroundColor Green

# 2. 檢查是否已存在任務
Write-Host "`n[2] 檢查現有任務..." -ForegroundColor Yellow

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "  ⚠ 任務已存在: $TaskName" -ForegroundColor Yellow
    if ($Force) {
        Write-Host "  正在刪除現有任務..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "  ✓ 現有任務已刪除" -ForegroundColor Green
    } else {
        Write-Host "  使用 -Force 參數可以刪除並重新建立任務" -ForegroundColor Cyan
        Write-Host "  現有任務狀態: $($existingTask.State)" -ForegroundColor Gray
        exit 0
    }
} else {
    Write-Host "  ✓ 沒有現有任務" -ForegroundColor Green
}

# 3. 建立任務動作
Write-Host "`n[3] 建立任務動作..." -ForegroundColor Yellow

$action = New-ScheduledTaskAction -Execute $scriptFullPath -WorkingDirectory $WorkingDirectory
Write-Host "  ✓ 任務動作已建立" -ForegroundColor Green
Write-Host "    執行: $scriptFullPath" -ForegroundColor Cyan
Write-Host "    工作目錄: $WorkingDirectory" -ForegroundColor Cyan

# 4. 建立任務觸發器（每小時執行一次）
Write-Host "`n[4] 建立任務觸發器..." -ForegroundColor Yellow

# 從現在開始，每小時執行一次
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
Write-Host "  ✓ 任務觸發器已建立" -ForegroundColor Green
Write-Host "    執行頻率: 每小時一次" -ForegroundColor Cyan
Write-Host "    持續時間: 365 天" -ForegroundColor Cyan

# 5. 建立任務設定
Write-Host "`n[5] 建立任務設定..." -ForegroundColor Yellow

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -WakeToRun:$false `
    -MultipleInstances IgnoreNew

Write-Host "  ✓ 任務設定已建立" -ForegroundColor Green
Write-Host "    允許在電池供電時執行: 是" -ForegroundColor Cyan
Write-Host "    多個實例: 忽略新實例" -ForegroundColor Cyan

# 6. 建立任務主體
Write-Host "`n[6] 建立任務主體..." -ForegroundColor Yellow

# 使用當前使用者執行
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
Write-Host "  ✓ 任務主體已建立" -ForegroundColor Green
Write-Host "    執行使用者: $env:USERNAME" -ForegroundColor Cyan
Write-Host "    登入類型: S4U (Service-for-User)" -ForegroundColor Cyan

# 7. 註冊任務
Write-Host "`n[7] 註冊任務..." -ForegroundColor Yellow

try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Wuchang OS 每小時檢查任務" | Out-Null
    Write-Host "  ✓ 任務已註冊: $TaskName" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 任務註冊失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 8. 顯示任務資訊
Write-Host "`n[8] 任務資訊..." -ForegroundColor Yellow

$task = Get-ScheduledTask -TaskName $TaskName
Write-Host "  任務名稱: $($task.TaskName)" -ForegroundColor Cyan
Write-Host "  任務狀態: $($task.State)" -ForegroundColor Cyan
Write-Host "  任務描述: $($task.Description)" -ForegroundColor Cyan

# 顯示下次執行時間
$taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
if ($taskInfo.NextRunTime) {
    Write-Host "  下次執行時間: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
} else {
    Write-Host "  下次執行時間: 未排程" -ForegroundColor Yellow
}

Write-Host "`n=== 設定完成 ===" -ForegroundColor Green

# 9. 顯示管理命令
Write-Host "`n管理命令：" -ForegroundColor Yellow
Write-Host "  查看任務: Get-ScheduledTask -TaskName $TaskName" -ForegroundColor Cyan
Write-Host "  啟用任務: Enable-ScheduledTask -TaskName $TaskName" -ForegroundColor Cyan
Write-Host "  停用任務: Disable-ScheduledTask -TaskName $TaskName" -ForegroundColor Cyan
Write-Host "  執行任務: Start-ScheduledTask -TaskName $TaskName" -ForegroundColor Cyan
Write-Host "  刪除任務: Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false" -ForegroundColor Cyan
Write-Host "  查看任務資訊: Get-ScheduledTaskInfo -TaskName $TaskName" -ForegroundColor Cyan
