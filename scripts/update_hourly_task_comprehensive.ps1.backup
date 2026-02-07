# 更新每小時排程任務為全面檢查版本
# 包含網域部署、全球可見性和 Google 非營利組織首頁合規檢查

param(
    [Parameter(Mandatory=$false)]
    [string]$TaskName = "WuchangHourlyCheck",
    
    [Parameter(Mandatory=$false)]
    [string]$ScriptPath = "scripts\run_hourly_check.bat",
    
    [Parameter(Mandatory=$false)]
    [string]$WorkingDirectory = (Get-Location).Path,
    
    [switch]$Force = $false
)

Write-Host "=== 更新每小時排程任務為全面檢查版本 ===" -ForegroundColor Cyan

# 1. 檢查腳本檔案
Write-Host "`n[1] 檢查腳本檔案..." -ForegroundColor Yellow

$scriptFullPath = Join-Path $WorkingDirectory $ScriptPath
if (-not (Test-Path $scriptFullPath)) {
    Write-Host "  ⚠ 腳本檔案不存在: $scriptFullPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "  ✓ 腳本檔案存在: $scriptFullPath" -ForegroundColor Green

# 檢查 Python 腳本
$pythonScript = Join-Path $WorkingDirectory "scripts\comprehensive_hourly_check.py"
if (-not (Test-Path $pythonScript)) {
    Write-Host "  ⚠ Python 腳本不存在: $pythonScript" -ForegroundColor Yellow
    Write-Host "    請確認 comprehensive_hourly_check.py 已建立" -ForegroundColor Cyan
    exit 1
}

Write-Host "  ✓ Python 腳本存在: $pythonScript" -ForegroundColor Green

# 2. 檢查現有任務
Write-Host "`n[2] 檢查現有任務..." -ForegroundColor Yellow

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "  ✓ 找到現有任務: $TaskName" -ForegroundColor Green
    Write-Host "    任務狀態: $($existingTask.State)" -ForegroundColor Cyan
    
    if ($Force) {
        Write-Host "  正在刪除現有任務..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "  ✓ 現有任務已刪除" -ForegroundColor Green
    } else {
        Write-Host "  使用 -Force 參數可以刪除並重新建立任務" -ForegroundColor Cyan
        Write-Host "  或直接更新任務動作..." -ForegroundColor Yellow
        
        # 更新任務動作
        $action = New-ScheduledTaskAction -Execute $scriptFullPath -WorkingDirectory $WorkingDirectory
        Set-ScheduledTask -TaskName $TaskName -Action $action -Description "Wuchang OS 每小時全面檢查（網域部署+全球可見性+Google非營利組織首頁合規）"
        Write-Host "  ✓ 任務動作已更新" -ForegroundColor Green
        exit 0
    }
}

# 3. 建立新任務
Write-Host "`n[3] 建立新任務..." -ForegroundColor Yellow

$action = New-ScheduledTaskAction -Execute $scriptFullPath -WorkingDirectory $WorkingDirectory
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -WakeToRun:$false `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited

try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Wuchang OS 每小時全面檢查（網域部署+全球可見性+Google非營利組織首頁合規）" | Out-Null
    Write-Host "  ✓ 任務已註冊: $TaskName" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 任務註冊失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4. 顯示任務資訊
Write-Host "`n[4] 任務資訊..." -ForegroundColor Yellow

$task = Get-ScheduledTask -TaskName $TaskName
Write-Host "  任務名稱: $($task.TaskName)" -ForegroundColor Cyan
Write-Host "  任務狀態: $($task.State)" -ForegroundColor Cyan
Write-Host "  任務描述: $($task.Description)" -ForegroundColor Cyan

$taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
if ($taskInfo.NextRunTime) {
    Write-Host "  下次執行時間: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
}

Write-Host "`n=== 更新完成 ===" -ForegroundColor Green

Write-Host "`n檢查項目：" -ForegroundColor Yellow
Write-Host "  ✓ 網域部署檢查（DNS 解析）" -ForegroundColor White
Write-Host "  ✓ 全球可見性檢查（多地區訪問測試）" -ForegroundColor White
Write-Host "  ✓ Google 非營利組織首頁合規檢查" -ForegroundColor White
