# 啟動 AI 總成小 J 開發者 UI

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI 總成小 J - 最高權限開發者 UI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$supervisorRoot = Split-Path -Parent $scriptPath
$apiScript = Join-Path $supervisorRoot "api\supervisor_api.py"

if (Test-Path $apiScript) {
    Write-Host "`n啟動開發者 UI 服務..." -ForegroundColor Green
    Write-Host "訪問: http://localhost:8888/developer-ui" -ForegroundColor Yellow
    Write-Host "`n按 Ctrl+C 停止服務`n" -ForegroundColor Gray
    
    python $apiScript
} else {
    Write-Host "✗ API 腳本不存在: $apiScript" -ForegroundColor Red
}
