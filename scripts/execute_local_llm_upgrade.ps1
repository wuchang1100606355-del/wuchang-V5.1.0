# 本地 LLM 模型升級執行腳本
# 功能：升級本地 Ollama 模型從 qwen2:0.5b 到 qwen2:7b

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "本地 LLM 模型升級工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Ollama 容器
Write-Host "🔍 檢查 Ollama 容器狀態..." -ForegroundColor Yellow

# 嘗試找出 Ollama 容器名稱
$ollamaContainers = docker ps --format "{{.Names}}" | Select-String -Pattern "ollama"

if (-not $ollamaContainers) {
    # 檢查所有容器（包括停止的）
    $allContainers = docker ps -a --format "{{.Names}}" | Select-String -Pattern "ollama"
    
    if ($allContainers) {
        Write-Host "⚠️ 發現 Ollama 容器但未運行：" -ForegroundColor Yellow
        $allContainers | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
        Write-Host ""
        Write-Host "請先啟動容器：" -ForegroundColor Yellow
        $containerName = $allContainers[0].ToString().Trim()
        Write-Host "  docker start $containerName" -ForegroundColor Cyan
        exit 1
    } else {
        Write-Host "❌ 未找到 Ollama 容器" -ForegroundColor Red
        Write-Host "請確認 Ollama 容器已建立並運行" -ForegroundColor Yellow
        exit 1
    }
}

$containerName = $ollamaContainers[0].ToString().Trim()
Write-Host "✅ 找到 Ollama 容器: $containerName" -ForegroundColor Green
Write-Host ""

# 檢查當前已安裝的模型
Write-Host "📋 檢查當前已安裝的模型..." -ForegroundColor Yellow
docker exec $containerName ollama list
Write-Host ""

# 推薦模型選項
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "推薦模型選項" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. qwen2:1.5b - 輕量級升級 (約 1GB, 記憶體需求: 4-6GB)" -ForegroundColor White
Write-Host "2. qwen2:7b - 推薦升級 (約 4-5GB, 記憶體需求: 12-16GB) ⭐" -ForegroundColor Yellow
Write-Host "3. llama3.1:8b - Llama 系列 (約 4.5GB, 記憶體需求: 12-16GB)" -ForegroundColor White
Write-Host "4. mistral:7b - Mistral 系列 (約 4GB, 記憶體需求: 12-16GB)" -ForegroundColor White
Write-Host ""

# 預設選擇 qwen2:7b（推薦）
$modelChoice = Read-Host "請選擇要下載的模型 (1-4, 預設: 2)"

switch ($modelChoice) {
    "1" { $modelName = "qwen2:1.5b" }
    "2" { $modelName = "qwen2:7b" }
    "3" { $modelName = "llama3.1:8b" }
    "4" { $modelName = "mistral:7b" }
    "" { $modelName = "qwen2:7b" }
    default { $modelName = "qwen2:7b" }
}

Write-Host ""
Write-Host "📥 準備下載模型: $modelName" -ForegroundColor Yellow
Write-Host "這可能需要一些時間，請耐心等待..." -ForegroundColor Gray
Write-Host ""

# 確認下載
$confirm = Read-Host "確認下載? (Y/N, 預設: Y)"
if ($confirm -ne "Y" -and $confirm -ne "y" -and $confirm -ne "") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔄 開始下載模型..." -ForegroundColor Cyan
Write-Host ""

# 執行下載（顯示進度）
docker exec -i $containerName ollama pull $modelName

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ 模型下載成功: $modelName" -ForegroundColor Green
    Write-Host ""
    
    # 測試模型
    Write-Host "🧪 測試模型..." -ForegroundColor Yellow
    docker exec $containerName ollama run $modelName "Hello"
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ 模型升級完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 下一步：更新系統配置" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "需要更新的檔案：" -ForegroundColor White
    Write-Host "  1. config/ai_agents/double_j_appearance.json" -ForegroundColor Gray
    Write-Host "     將 'local': 'qwen2:0.5b' 改為 'local': '$modelName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. config/ai_agents/double_j_appearance.yaml" -ForegroundColor Gray
    Write-Host "     將 local: qwen2:0.5b 改為 local: $modelName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. wuchang_os/addons/wuchang_core/data/system_params.xml" -ForegroundColor Gray
    Write-Host "     更新 wuchang.ollama_model 參數" -ForegroundColor Gray
    Write-Host ""
    Write-Host "詳細指南：reports/LOCAL_LLM_UPGRADE_GUIDE.md" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ 模型下載失敗" -ForegroundColor Red
    Write-Host "請檢查：" -ForegroundColor Yellow
    Write-Host "  - 網路連線是否正常" -ForegroundColor Gray
    Write-Host "  - 儲存空間是否充足" -ForegroundColor Gray
    Write-Host "  - 容器是否有足夠資源" -ForegroundColor Gray
    exit 1
}
