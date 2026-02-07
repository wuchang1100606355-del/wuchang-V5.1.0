# 五常 AI - 快速發送命令到 Server

param(
    [string]$Command = "",
    [string]$Target = "server"
)

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  📡 五常 AI - 遠端命令發送工具" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 切換到正確目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 檢查 Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ 找不到 Python" -ForegroundColor Red
    exit 1
}

# 檢查環境變數
if (-not $env:SYNC_SECRET) {
    Write-Host "⚠️  未設定 SYNC_SECRET，使用預設值" -ForegroundColor Yellow
    $env:SYNC_SECRET = "wuchang-sync-secret"
}

Write-Host "目標: $Target" -ForegroundColor White
Write-Host ""

if ($Command) {
    # 命令行模式
    Write-Host "執行命令: $Command" -ForegroundColor Yellow
    Write-Host ""
    & python send_command.py $Target $Command
} else {
    # 互動模式
    & python send_command.py
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  完成" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
