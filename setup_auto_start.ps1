# ============================================
# 五常系統 - 開機自動啟動設定腳本
# ============================================
# 此 PowerShell 腳本用於將服務器啟動腳本註冊到 Windows 任務計劃程序
# 執行後，系統開機時會自動啟動所有服務器
#
# 使用方式：
#   1. 以系統管理員身份執行 PowerShell
#   2. 執行: .\setup_auto_start.ps1
# ============================================

# 檢查是否以管理員身份執行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[錯誤] 此腳本需要以系統管理員身份執行" -ForegroundColor Red
    Write-Host "[提示] 請右鍵點擊 PowerShell，選擇「以系統管理員身份執行」" -ForegroundColor Yellow
    pause
    exit 1
}

# 獲取腳本所在目錄
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile = Join-Path $scriptDir "start_servers.bat"
$pythonFile = Join-Path $scriptDir "server_auto_deploy.py"

# 檢查必要檔案是否存在
if (-not (Test-Path $batFile)) {
    Write-Host "[錯誤] 找不到 start_servers.bat" -ForegroundColor Red
    exit 1
}

# 任務名稱
$taskName = "五常系統-開機自動啟動服務器"

# 檢查任務是否已存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "[提示] 發現已存在的任務，將先刪除..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 建立任務動作（執行批處理腳本）
$action = New-ScheduledTaskAction -Execute $batFile -WorkingDirectory $scriptDir

# 建立觸發器（系統啟動時）
$trigger = New-ScheduledTaskTrigger -AtStartup

# 建立設定（允許在電池供電時執行，最高權限）
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# 建立主體（以最高權限執行）
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

# 註冊任務
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "五常系統服務器開機自動啟動" `
        -Force

    Write-Host "[成功] 任務已成功註冊到任務計劃程序" -ForegroundColor Green
    Write-Host ""
    Write-Host "任務名稱: $taskName" -ForegroundColor Cyan
    Write-Host "觸發條件: 系統啟動時" -ForegroundColor Cyan
    Write-Host "執行檔案: $batFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[提示] 您可以透過以下方式管理此任務：" -ForegroundColor Yellow
    Write-Host "  1. 開啟「工作排程器」應用程式" -ForegroundColor White
    Write-Host "  2. 搜尋任務名稱: $taskName" -ForegroundColor White
    Write-Host "  3. 可以手動執行、編輯或刪除任務" -ForegroundColor White
    Write-Host ""
    Write-Host "[提示] 若要移除自動啟動，請執行：" -ForegroundColor Yellow
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "[錯誤] 註冊任務時發生錯誤: $_" -ForegroundColor Red
    exit 1
}

# 詢問是否立即測試執行
Write-Host ""
$test = Read-Host "是否立即測試執行任務？(Y/N)"
if ($test -eq "Y" -or $test -eq "y") {
    Write-Host "[執行] 啟動任務..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $taskName
    Write-Host "[完成] 任務已啟動，請檢查服務器是否正常運行" -ForegroundColor Green
    Write-Host "[提示] 本機中控台: http://127.0.0.1:8788/" -ForegroundColor Cyan
    Write-Host "[提示] Little J Hub: http://127.0.0.1:8799/" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "設定完成！" -ForegroundColor Green
pause
