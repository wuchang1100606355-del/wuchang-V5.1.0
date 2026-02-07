# PowerShell 腳本：設置每小時檢查系統部署狀態的定時任務
# 執行此腳本將創建一個每小時運行一次的 Windows 定時任務

param(
    [string]$PythonPath = "python",
    [string]$ScriptPath = "$PSScriptRoot\hourly_deployment_check.py",
    [string]$TaskName = "WuchangHourlyDeploymentCheck",
    [string]$Description = "每小時檢查 wuchang.life 系統部署狀態並聯繫 UI 電腦",
    [int]$DelayMinutes = 60  # 首次執行延遲（分鐘）
)

Write-Host "=" * 80
Write-Host "  設置每小時系統部署檢查定時任務"
Write-Host "=" * 80
Write-Host ""

# 檢查 Python 是否可用
Write-Host "檢查 Python 環境..."
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "  ✓ Python 版本: $pythonVersion"
} catch {
    Write-Host "  ❌ 無法執行 Python，請確認 Python 已安裝並在 PATH 中"
    Write-Host "  錯誤: $_"
    exit 1
}

# 檢查腳本文件是否存在
if (-not (Test-Path $ScriptPath)) {
    Write-Host "  ❌ 腳本文件不存在: $ScriptPath"
    exit 1
}
Write-Host "  ✓ 腳本文件存在: $ScriptPath"
Write-Host ""

# 獲取當前用戶
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
Write-Host "當前用戶: $currentUser"
Write-Host ""

# 檢查任務是否已存在
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "發現已存在的定時任務: $TaskName"
    Write-Host "  選項:"
    Write-Host "    1. 刪除現有任務並重新創建"
    Write-Host "    2. 更新現有任務"
    Write-Host "    3. 取消"
    $choice = Read-Host "  請選擇 (1/2/3)"
    
    if ($choice -eq "1") {
        Write-Host "  刪除現有任務..."
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "  ✓ 已刪除現有任務"
    } elseif ($choice -eq "2") {
        Write-Host "  更新現有任務..."
        # 更新任務的操作
        $action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`""
        Set-ScheduledTask -TaskName $TaskName -Action $action
        Write-Host "  ✓ 已更新任務"
        exit 0
    } else {
        Write-Host "  已取消"
        exit 0
    }
}

# 創建任務操作
Write-Host "創建定時任務操作..."
$action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory (Split-Path -Parent $ScriptPath)

# 創建任務觸發器（每小時執行一次）
Write-Host "創建觸發器（每小時執行一次）..."
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes($DelayMinutes) `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Days 365)  # 持續一年

# 創建任務設置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# 註冊定時任務
Write-Host "註冊定時任務..."
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description $Description `
        -User $currentUser `
        -RunLevel Highest  # 以最高權限運行
    
    Write-Host "  ✓ 定時任務創建成功！"
    Write-Host ""
    Write-Host "任務詳情:"
    Write-Host "  名稱: $TaskName"
    Write-Host "  描述: $Description"
    Write-Host "  執行時間: 每小時執行一次"
    Write-Host "  首次執行: $((Get-Date).AddMinutes($DelayMinutes).ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Host "  Python: $PythonPath"
    Write-Host "  腳本: $ScriptPath"
    Write-Host ""
    
    # 顯示任務狀態
    $task = Get-ScheduledTask -TaskName $TaskName
    Write-Host "任務狀態: $($task.State)"
    Write-Host ""
    
    # 詢問是否立即測試執行
    $test = Read-Host "是否立即測試執行一次？(Y/N)"
    if ($test -eq "Y" -or $test -eq "y") {
        Write-Host ""
        Write-Host "執行測試..."
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "  ✓ 已觸發任務執行"
        Write-Host ""
        Write-Host "  查看任務執行狀態:"
        Write-Host "    Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo"
        Write-Host ""
        Write-Host "  查看任務日誌:"
        Write-Host "    Get-WinEvent -LogName Microsoft-Windows-TaskScheduler/Operational | Where-Object {$_.Message -like '*$TaskName*'}"
    }
    
} catch {
    Write-Host "  ❌ 創建定時任務失敗"
    Write-Host "  錯誤: $_"
    Write-Host ""
    Write-Host "提示: 可能需要以管理員權限運行此腳本"
    exit 1
}

Write-Host ""
Write-Host "=" * 80
Write-Host "  設置完成"
Write-Host "=" * 80
Write-Host ""
Write-Host "管理定時任務的命令:"
Write-Host "  查看任務: Get-ScheduledTask -TaskName $TaskName"
Write-Host "  啟動任務: Start-ScheduledTask -TaskName $TaskName"
Write-Host "  停止任務: Stop-ScheduledTask -TaskName $TaskName"
Write-Host "  刪除任務: Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
Write-Host "  查看執行歷史: Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo"
Write-Host ""
