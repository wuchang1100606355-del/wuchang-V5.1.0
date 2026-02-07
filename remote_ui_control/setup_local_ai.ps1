# 五常 AI - 本機 AI 節點安裝指南

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🏠 本機 AI 節點安裝指南" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "本機 AI 節點讓你的系統優先使用本地處理，提升速度並保護隱私" -ForegroundColor Yellow
Write-Host ""

# 選擇 AI 後端
Write-Host "請選擇本機 AI 後端:" -ForegroundColor Cyan
Write-Host "  1. Ollama（推薦，免費開源）" -ForegroundColor White
Write-Host "  2. OpenAI API（本地部署版）" -ForegroundColor White
Write-Host "  3. 稍後配置" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "請輸入選項 (1-3)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  安裝 Ollama" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 檢查是否已安裝
    $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
    
    if ($ollamaCmd) {
        Write-Host "✅ Ollama 已安裝" -ForegroundColor Green
        $ollamaVersion = & ollama --version 2>&1
        Write-Host "   版本: $ollamaVersion" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Ollama 未安裝" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "正在打開 Ollama 下載頁面..." -ForegroundColor Yellow
        Start-Process "https://ollama.ai/download"
        Write-Host ""
        Write-Host "請按照以下步驟操作:" -ForegroundColor Cyan
        Write-Host "  1. 下載並安裝 Ollama" -ForegroundColor White
        Write-Host "  2. 安裝完成後，重新執行此腳本" -ForegroundColor White
        Write-Host ""
        Read-Host "按 Enter 退出"
        exit
    }
    
    Write-Host ""
    Write-Host "正在下載推薦模型..." -ForegroundColor Yellow
    Write-Host "  模型: gemma2:2b (輕量級，適合本機運行)" -ForegroundColor Gray
    Write-Host ""
    
    # 拉取模型
    Write-Host "這可能需要幾分鐘時間..." -ForegroundColor Yellow
    & ollama pull gemma2:2b
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 模型下載完成！" -ForegroundColor Green
        Write-Host ""
        
        # 測試模型
        Write-Host "正在測試模型..." -ForegroundColor Yellow
        $testResponse = & ollama run gemma2:2b "你好，請用一句話介紹自己" --verbose 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 模型測試成功！" -ForegroundColor Green
            Write-Host ""
            Write-Host "回應: $testResponse" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "=====================================================" -ForegroundColor Cyan
        Write-Host "  🎉 安裝完成！" -ForegroundColor Green
        Write-Host "=====================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "本機 AI 節點已就緒，配置如下:" -ForegroundColor Yellow
        Write-Host "  類型: ollama" -ForegroundColor White
        Write-Host "  地址: http://localhost:11434" -ForegroundColor White
        Write-Host "  模型: gemma2:2b" -ForegroundColor White
        Write-Host ""
        Write-Host "你現在可以啟動混合 AI 系統了！" -ForegroundColor Green
        Write-Host "  執行: .\start_hybrid_ai.ps1" -ForegroundColor White
        
    } else {
        Write-Host ""
        Write-Host "❌ 模型下載失敗" -ForegroundColor Red
        Write-Host "請檢查網路連線後重試" -ForegroundColor Yellow
    }
    
} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  配置 OpenAI API" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "OpenAI API 配置資訊:" -ForegroundColor Yellow
    Write-Host "  需要在 .env 文件中設置:" -ForegroundColor White
    Write-Host "    LOCAL_AI_TYPE=openai" -ForegroundColor Gray
    Write-Host "    LOCAL_AI_HOST=http://your-api-host" -ForegroundColor Gray
    Write-Host "    LOCAL_AI_API_KEY=your-api-key" -ForegroundColor Gray
    Write-Host "    LOCAL_AI_MODEL=gpt-3.5-turbo" -ForegroundColor Gray
    Write-Host ""
    Write-Host "請手動編輯 .env 文件完成配置" -ForegroundColor Yellow
    
} else {
    Write-Host ""
    Write-Host "你可以稍後手動配置本機 AI 節點" -ForegroundColor Yellow
    Write-Host "參考文檔: README.md" -ForegroundColor White
}

Write-Host ""
