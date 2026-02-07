# 設定小 J 定時檢查部署狀態

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "設定小 J 定時檢查部署狀態" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Join-Path $PSScriptRoot "little_j_deployment_checker.py"
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source

if (-not $pythonPath) {
    $pythonPath = (Get-Command python3 -ErrorAction SilentlyContinue).Source
}

if (-not $pythonPath) {
    Write-Host "[✗] 未找到 Python，請先安裝 Python" -ForegroundColor Red
    exit 1
}

Write-Host "[✓] Python 路徑: $pythonPath" -ForegroundColor Green
Write-Host "[✓] 腳本路徑: $scriptPath" -ForegroundColor Green
Write-Host ""

# 檢查腳本是否存在
if (-not (Test-Path $scriptPath)) {
    Write-Host "[✗] 腳本不存在: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "請選擇檢查頻率：" -ForegroundColor Yellow
Write-Host "  1. 每小時檢查一次" -ForegroundColor White
Write-Host "  2. 每 2 小時檢查一次" -ForegroundColor White
Write-Host "  3. 每 4 小時檢查一次" -ForegroundColor White
Write-Host "  4. 每天檢查一次（建議時間：上午 8 點）" -ForegroundColor White
Write-Host "  5. 自訂間隔" -ForegroundColor White
Write-Host ""

$choice = Read-Host "請選擇 (1-5)"

$interval = 0
$intervalType = ""

switch ($choice) {
    "1" {
        $interval = 1
        $intervalType = "小時"
        $taskName = "小J_部署檢查_每小時"
    }
    "2" {
        $interval = 2
        $intervalType = "小時"
        $taskName = "小J_部署檢查_每2小時"
    }
    "3" {
        $interval = 4
        $intervalType = "小時"
        $taskName = "小J_部署檢查_每4小時"
    }
    "4" {
        $interval = 1
        $intervalType = "天"
        $taskName = "小J_部署檢查_每天"
    }
    "5" {
        $interval = Read-Host "請輸入間隔（分鐘）"
        $intervalType = "分鐘"
        $taskName = "小J_部署檢查_每${interval}分鐘"
    }
    default {
        Write-Host "[✗] 無效的選擇" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "設定任務..." -ForegroundColor Yellow

# 建立任務動作
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`"" -WorkingDirectory $PSScriptRoot

# 建立觸發器
if ($intervalType -eq "小時") {
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours $interval) -RepetitionDuration (New-TimeSpan -Days 365)
} elseif ($intervalType -eq "天") {
    $trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
} else {
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $interval) -RepetitionDuration (New-TimeSpan -Days 365)
}

# 建立設定
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 建立主體（以目前使用者執行）
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# 註冊任務
try {
    # 檢查任務是否已存在
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if ($existingTask) {
        Write-Host "[!] 任務已存在，將更新..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "小 J 定時檢查部署狀態"
    
    Write-Host "[✓] 任務已建立: $taskName" -ForegroundColor Green
    Write-Host ""
    Write-Host "檢查頻率: 每 $interval $intervalType" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor Yellow
    Write-Host "  1. 查看任務: taskschd.msc" -ForegroundColor White
    Write-Host "  2. 手動測試: python `"$scriptPath`"" -ForegroundColor White
    Write-Host "  3. 查看報告: reports\deployment_status_latest.md" -ForegroundColor White
} catch {
    Write-Host "[✗] 建立任務失敗: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能需要以管理員權限執行此腳本" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
