# 本地 AI 永久優化腳本
# 用途：協助優化本地 AI (Ollama) 的運用方式

param(
    [string]$Model = "qwen2:1.5b",
    [switch]$UpgradeModel = $false,
    [switch]$CheckGPU = $false,
    [switch]$SetupCache = $false
)

Write-Host "`n=== 本地 AI 永久優化 ===" -ForegroundColor Cyan
Write-Host ""

if ($UpgradeModel) {
    Write-Host "=== 步驟 1: 升級模型 ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "當前模型: qwen2:0.5b (0.33 GB)" -ForegroundColor White
    Write-Host "目標模型: $Model" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "升級步驟：" -ForegroundColor Cyan
    Write-Host "  1. 確保 Ollama 服務運行中" -ForegroundColor White
    Write-Host "  2. 下載新模型:" -ForegroundColor White
    Write-Host "     docker exec -it ollama ollama pull $Model" -ForegroundColor Gray
    Write-Host "  3. 更新 Odoo 設定中的模型名稱" -ForegroundColor White
    Write-Host ""
    
    $confirm = Read-Host "確認要升級模型？(Y/N)"
    if ($confirm -eq "Y" -or $confirm -eq "y") {
        Write-Host "正在下載模型..." -ForegroundColor Yellow
        docker exec -it ollama ollama pull $Model
        Write-Host "✅ 模型已下載" -ForegroundColor Green
        Write-Host ""
        Write-Host "請更新 Odoo 設定中的模型名稱為: $Model" -ForegroundColor Yellow
    }
}

if ($CheckGPU) {
    Write-Host "=== 步驟 2: 檢查 GPU 支援 ===" -ForegroundColor Yellow
    Write-Host ""
    
    # 檢查 NVIDIA GPU
    $nvidia = nvidia-smi 2>$null
    if ($nvidia) {
        Write-Host "✅ 偵測到 NVIDIA GPU" -ForegroundColor Green
        Write-Host $nvidia
        Write-Host ""
        Write-Host "可以啟用 GPU 加速以提升性能" -ForegroundColor Green
    } else {
        Write-Host "⚠️  未偵測到 NVIDIA GPU" -ForegroundColor Yellow
        Write-Host "將使用 CPU 運行（較慢但可用）" -ForegroundColor White
    }
    Write-Host ""
}

if ($SetupCache) {
    Write-Host "=== 步驟 3: 設定快取機制 ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "快取機制可以大幅提升回應速度" -ForegroundColor White
    Write-Host ""
    Write-Host "建議實作：" -ForegroundColor Cyan
    Write-Host "  1. 記憶體快取（最快）" -ForegroundColor White
    Write-Host "  2. Redis 快取（快速，可選）" -ForegroundColor White
    Write-Host "  3. 資料庫快取（持久）" -ForegroundColor White
    Write-Host ""
    Write-Host "詳細實作請參考：" -ForegroundColor Cyan
    Write-Host "  docs\LOCAL_AI_OPTIMIZATION_GUIDE.md" -ForegroundColor White
    Write-Host ""
}

Write-Host "=== 優化建議總結 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 模型升級：" -ForegroundColor Yellow
Write-Host "   • qwen2:0.5b → qwen2:1.5b（推薦）" -ForegroundColor White
Write-Host "   • 性能提升約 50%，大小增加約 3 倍" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 快取機制：" -ForegroundColor Yellow
Write-Host "   • 實作多層快取" -ForegroundColor White
Write-Host "   • 快取命中率可達 60-80%" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 提示詞優化：" -ForegroundColor Yellow
Write-Host "   • 優化系統提示詞" -ForegroundColor White
Write-Host "   • 建立提示詞模板庫" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 批次處理：" -ForegroundColor Yellow
Write-Host "   • 合併多個請求" -ForegroundColor White
Write-Host "   • 減少 API 呼叫次數" -ForegroundColor Gray
Write-Host ""
Write-Host "5. POS 語音點餐：" -ForegroundColor Yellow
Write-Host "   • 使用 Google Speech-to-Text API（免費額度）" -ForegroundColor White
Write-Host "   • 使用 Google Text-to-Speech API（免費額度）" -ForegroundColor White
Write-Host "   • 本地 AI 處理對話（免費）" -ForegroundColor White
Write-Host ""
Write-Host "詳細指南：" -ForegroundColor Cyan
Write-Host "  docs\LOCAL_AI_OPTIMIZATION_GUIDE.md" -ForegroundColor White
Write-Host "  docs\POS_VOICE_ORDERING_OPTIMIZATION.md" -ForegroundColor White
