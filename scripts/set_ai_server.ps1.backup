# 設置 AI 伺服器端點
# 將 Ollama 端點設為 http://host.docker.internal:11434

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  設置 AI 伺服器端點" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$aiServerUrl = "http://host.docker.internal:11434"
$aiServerHost = "host.docker.internal:11434"

Write-Host "目標端點: $aiServerUrl" -ForegroundColor Yellow
Write-Host ""

# 通過 Odoo shell 設置參數
Write-Host "[1/3] 設置 wuchang.llm_base_url..." -ForegroundColor Cyan
docker-compose exec -T wuchang-web odoo shell -d odoo --no-http `
    -c "env['ir.config_parameter'].sudo().set_param('wuchang.llm_base_url', '$aiServerUrl')" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 已設置 wuchang.llm_base_url = $aiServerUrl" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 設置失敗，請檢查 Odoo 服務狀態" -ForegroundColor Yellow
}

Write-Host ""

Write-Host "[2/3] 設置 wuchang.llm.host..." -ForegroundColor Cyan
docker-compose exec -T wuchang-web odoo shell -d odoo --no-http `
    -c "env['ir.config_parameter'].sudo().set_param('wuchang.llm.host', '$aiServerHost')" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 已設置 wuchang.llm.host = $aiServerHost" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 設置失敗，請檢查 Odoo 服務狀態" -ForegroundColor Yellow
}

Write-Host ""

Write-Host "[3/3] 確保 AI 模式為 local_ollama..." -ForegroundColor Cyan
docker-compose exec -T wuchang-web odoo shell -d odoo --no-http `
    -c "env['ir.config_parameter'].sudo().set_param('wuchang.ai_mode', 'local_ollama')" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 已確保 AI 模式為 local_ollama" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 設置失敗，請檢查 Odoo 服務狀態" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ AI 伺服器設置完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "配置摘要:" -ForegroundColor Yellow
Write-Host "  - LLM 基礎 URL: $aiServerUrl" -ForegroundColor White
Write-Host "  - LLM 主機: $aiServerHost" -ForegroundColor White
Write-Host "  - AI 模式: local_ollama" -ForegroundColor White
Write-Host ""
Write-Host "💡 提示: 請確保 Ollama 服務運行在 http://host.docker.internal:11434" -ForegroundColor Cyan
