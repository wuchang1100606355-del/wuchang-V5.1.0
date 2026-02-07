# ============================================
# 五常系統 - 移除開機自動啟動
# ============================================
# 此腳本用於移除已註冊的開機自動啟動任務
#
# 使用方式：
#   1. 以系統管理員身份執行 PowerShell
#   2. 執行: .\remove_auto_start.ps1
# ============================================

# 檢查是否以管理員身份執行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[錯誤] 此腳本需要以系統管理員身份執行" -ForegroundColor Red
    Write-Host "[提示] 請右鍵點擊 PowerShell，選擇「以系統管理員身份執行」" -ForegroundColor Yellow
    pause
    exit 1
}

# 任務名稱
$taskName = "五常系統-開機自動啟動服務器"

# 檢查任務是否存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if (-not $existingTask) {
    Write-Host "[提示] 未找到名為 '$taskName' 的任務" -ForegroundColor Yellow
    Write-Host "[提示] 可能尚未註冊自動啟動，或任務名稱不同" -ForegroundColor Yellow
    pause
    exit 0
}

# 確認刪除
Write-Host "[警告] 即將移除開機自動啟動任務: $taskName" -ForegroundColor Yellow
$confirm = Read-Host "確定要移除嗎？(Y/N)"

if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "[取消] 操作已取消" -ForegroundColor Cyan
    pause
    exit 0
}

# 移除任務
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "[成功] 任務已成功移除" -ForegroundColor Green
    Write-Host ""
    Write-Host "[提示] 系統開機時將不再自動啟動服務器" -ForegroundColor Yellow
    Write-Host "[提示] 您仍可以手動執行 start_servers.bat 或 server_auto_deploy.py 來啟動服務器" -ForegroundColor Cyan
} catch {
    Write-Host "[錯誤] 移除任務時發生錯誤: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "移除完成！" -ForegroundColor Green
pause
