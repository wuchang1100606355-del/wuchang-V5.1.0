# 設定 Odoo 中的 AI 小 J 專用金鑰
# PowerShell 腳本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI 小 J 專用金鑰設定" -ForegroundColor Cyan
Write-Host "Odoo 系統參數配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 檢查 Odoo 是否運行
$odooUrl = "http://localhost:8069"
Write-Host "`n檢查 Odoo 連線..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "$odooUrl/web/health" -Method Get -TimeoutSec 5 -ErrorAction SilentlyContinue
    Write-Host "✓ Odoo 服務運行中" -ForegroundColor Green
} catch {
    Write-Host "⚠ Odoo 服務可能未運行，將使用 Python 腳本設定" -ForegroundColor Yellow
}

# 執行 Python 腳本
$scriptPath = Join-Path $PSScriptRoot "setup_odoo_keys.py"
if (Test-Path $scriptPath) {
    Write-Host "`n執行設定腳本..." -ForegroundColor Yellow
    python $scriptPath
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "設定完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`n下一步:" -ForegroundColor Yellow
    Write-Host "1. 登入 Odoo: $odooUrl" -ForegroundColor White
    Write-Host "2. 前往: 設定 > 技術 > 參數 > 系統參數" -ForegroundColor White
    Write-Host "3. 填入以下 AI 小 J 專用金鑰:" -ForegroundColor White
    Write-Host "   - ai.j.openai.api.key" -ForegroundColor Gray
    Write-Host "   - ai.j.anthropic.api.key" -ForegroundColor Gray
    Write-Host "   - ai.j.google.api.key" -ForegroundColor Gray
} else {
    Write-Host "✗ 設定腳本不存在: $scriptPath" -ForegroundColor Red
}
