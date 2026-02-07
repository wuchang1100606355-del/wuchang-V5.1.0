# 五常 AI - 混合智能系統啟動腳本（本地優先、雲端備援）

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🌟 五常 AI - 混合智能系統" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  🏠 本機 AI 節點（優先）" -ForegroundColor Yellow
Write-Host "  ☁️  雲端 Vertex AI（備援）" -ForegroundColor Yellow
Write-Host ""

# 切換到正確目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 檢查本機 AI 節點
Write-Host "檢查本機 AI 節點..." -ForegroundColor Yellow

$localAIAvailable = $false
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue

if ($ollamaCmd) {
    # 檢查 Ollama 服務
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $localAIAvailable = $true
            Write-Host "  ✅ Ollama 服務運行中" -ForegroundColor Green
            
            # 檢查模型
            $tags = $response.Content | ConvertFrom-Json
            $models = $tags.models | ForEach-Object { $_.name }
            
            if ($models -contains "gemma2:2b") {
                Write-Host "  ✅ 模型已安裝: gemma2:2b" -ForegroundColor Green
            } else {
                Write-Host "  ⚠️  推薦模型未安裝" -ForegroundColor Yellow
                Write-Host "     執行: ollama pull gemma2:2b" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "  ⚠️  Ollama 服務未運行" -ForegroundColor Yellow
        Write-Host "     啟動: ollama serve" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠️  Ollama 未安裝" -ForegroundColor Yellow
    Write-Host "     執行: .\setup_local_ai.ps1 安裝" -ForegroundColor Gray
}

Write-Host ""

# 檢查 Python 環境
Write-Host "檢查 Python 環境..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ 找不到 Python" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Python 環境正常" -ForegroundColor Green
Write-Host ""

# 檢查依賴
Write-Host "檢查依賴套件..." -ForegroundColor Yellow
$requiredPackages = @("aiohttp", "websockets")
$missingPackages = @()

foreach ($pkg in $requiredPackages) {
    $installed = & python -c "import $pkg" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $pkg
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "  ⚠️  安裝缺少的套件..." -ForegroundColor Yellow
    & python -m pip install -r requirements.txt --quiet
}

Write-Host "  ✅ 依賴檢查完成" -ForegroundColor Green
Write-Host ""

# 顯示系統狀態
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  系統狀態" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  本機節點: $(if ($localAIAvailable) { '🟢 可用（優先）' } else { '🔴 不可用' })" -ForegroundColor White
Write-Host "  雲端備援: 🟢 可用" -ForegroundColor White
Write-Host ""

if (-not $localAIAvailable) {
    Write-Host "💡 提示: 本機節點不可用，將全部使用雲端處理" -ForegroundColor Yellow
    Write-Host "   建議安裝 Ollama 以啟用本機優先模式" -ForegroundColor Yellow
    Write-Host ""
}

# 選擇運行模式
Write-Host "請選擇運行模式:" -ForegroundColor Cyan
Write-Host "  1. 命令行互動模式" -ForegroundColor White
Write-Host "  2. 測試本機 AI 節點" -ForegroundColor White
Write-Host "  3. 安裝本機 AI 節點" -ForegroundColor White
Write-Host ""

$mode = Read-Host "請輸入選項 (1-3)"

if ($mode -eq "1") {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  🚀 啟動混合智能系統..." -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🏠 = 本機節點處理 | ☁️ = 雲端備援處理" -ForegroundColor Gray
    Write-Host ""
    
    & python hybrid_ai_router.py
    
} elseif ($mode -eq "2") {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  🧪 測試本機 AI 節點..." -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
    
    & python local_ai_node.py
    
} elseif ($mode -eq "3") {
    Write-Host ""
    & .\setup_local_ai.ps1
    
} else {
    Write-Host "❌ 無效的選項" -ForegroundColor Red
    exit 1
}

Write-Host ""
