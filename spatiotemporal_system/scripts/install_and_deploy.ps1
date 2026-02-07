# 時空系統完整安裝與部署腳本
# 包含依賴安裝、授權設定、AI 小 J 整合

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "時空系統完整安裝與部署" -ForegroundColor Cyan
Write-Host "AI 小 J 整合流程" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 步驟 1: 安裝依賴
Write-Host "`n[步驟 1/4] 安裝依賴套件..." -ForegroundColor Yellow
$installScript = Join-Path $PSScriptRoot "install_dependencies.ps1"
if (Test-Path $installScript) {
    & $installScript
} else {
    Write-Host "✗ 安裝腳本不存在: $installScript" -ForegroundColor Red
}

# 步驟 2: 設定授權
Write-Host "`n[步驟 2/4] 設定 AI 小 J 完整授權..." -ForegroundColor Yellow
$authScript = Join-Path $PSScriptRoot "setup_full_authorization.ps1"
if (Test-Path $authScript) {
    & $authScript -EnableCloudCompute -FullAccess
} else {
    Write-Host "✗ 授權腳本不存在: $authScript" -ForegroundColor Red
}

# 步驟 3: 部署到 AI 小 J
Write-Host "`n[步驟 3/4] 部署時空能力到 AI 小 J..." -ForegroundColor Yellow
$deployScript = Join-Path $PSScriptRoot "deploy_to_ai_j.py"
if (Test-Path $deployScript) {
    python $deployScript
} else {
    Write-Host "✗ 部署腳本不存在: $deployScript" -ForegroundColor Red
}

# 步驟 4: 驗證安裝
Write-Host "`n[步驟 4/4] 驗證安裝..." -ForegroundColor Yellow
try {
    python -c "from spatiotemporal_system.core.spatiotemporal import SpatiotemporalSystem; print('✓ 時空系統模組載入成功')"
    python -c "from spatiotemporal_system.core.ai_agent import AIAgent; print('✓ AI 代理模組載入成功')"
    python -c "from spatiotemporal_system.applications.community_service import CommunityService; print('✓ 社區服務模組載入成功')"
    Write-Host "✓ 所有模組驗證通過" -ForegroundColor Green
} catch {
    Write-Host "✗ 模組驗證失敗: $_" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "安裝與部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n後續步驟:" -ForegroundColor Yellow
Write-Host "1. 設定雲端算力 API Key（如需要）:" -ForegroundColor White
Write-Host "   - OPENAI_API_KEY" -ForegroundColor Gray
Write-Host "   - ANTHROPIC_API_KEY" -ForegroundColor Gray
Write-Host "   - GOOGLE_API_KEY" -ForegroundColor Gray
Write-Host "2. 重新啟動 AI 小 J 以載入時空能力" -ForegroundColor White
Write-Host "3. 測試時空功能:" -ForegroundColor White
Write-Host "   python -c `"from spatiotemporal_system.config.ai_j_integration import get_ai_j_spatiotemporal; st = get_ai_j_spatiotemporal(); print(st.get_capabilities())`"" -ForegroundColor Gray
