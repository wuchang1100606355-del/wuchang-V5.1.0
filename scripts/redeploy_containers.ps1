# 容器重新部署腳本
# 功能：重新部署所有容器，並配置 LLM 模型升級

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "容器重新部署工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 docker-compose 檔案
$composeFiles = @(
    "docker-compose.yml",
    "docker-compose.optimized.yml",
    "docker-compose-ai.yml"
)

$availableFiles = @()
foreach ($file in $composeFiles) {
    if (Test-Path $file) {
        $availableFiles += $file
        Write-Host "✓ 找到: $file" -ForegroundColor Green
    }
}

if ($availableFiles.Count -eq 0) {
    Write-Host "❌ 未找到 docker-compose 檔案" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 可用的 docker-compose 檔案：" -ForegroundColor Cyan
for ($i = 0; $i -lt $availableFiles.Count; $i++) {
    Write-Host "  $($i + 1). $($availableFiles[$i])" -ForegroundColor White
}

Write-Host ""
$choice = Read-Host "請選擇要使用的檔案 (1-$($availableFiles.Count), 預設: 1)"
if ([string]::IsNullOrWhiteSpace($choice)) {
    $choice = "1"
}

$selectedFile = $availableFiles[[int]$choice - 1]
Write-Host ""
Write-Host "選擇的檔案: $selectedFile" -ForegroundColor Yellow
Write-Host ""

# 確認部署
$confirm = Read-Host "確認要重新部署? (Y/N, 預設: Y)"
if ($confirm -ne "Y" -and $confirm -ne "y" -and $confirm -ne "") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🚀 步驟 1：啟動容器..." -ForegroundColor Cyan
Write-Host "使用檔案: $selectedFile" -ForegroundColor Gray
Write-Host ""

# 執行 docker-compose up（啟動所有 profiles）
Write-Host "啟動所有服務（system + ui profiles）..." -ForegroundColor Gray
docker-compose -f $selectedFile --profile system --profile ui up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ 容器啟動成功" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ 容器啟動失敗" -ForegroundColor Red
    Write-Host "請檢查 docker-compose 檔案和日誌" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "⏳ 等待容器啟動..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "📋 步驟 2：檢查容器狀態..." -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}"

Write-Host ""
Write-Host "🤖 步驟 3：升級 LLM 模型..." -ForegroundColor Cyan

# 查找 Ollama 容器
$ollamaContainer = docker ps --format "{{.Names}}" | Select-String -Pattern "ollama"
if ($ollamaContainer) {
    $containerName = $ollamaContainer[0].ToString().Trim()
    Write-Host "找到 Ollama 容器: $containerName" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "下載 qwen2:7b 模型..." -ForegroundColor Yellow
    Write-Host "這可能需要 10-30 分鐘，請耐心等待..." -ForegroundColor Gray
    Write-Host ""
    
    docker exec $containerName ollama pull qwen2:7b
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ 模型下載成功" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "🧪 測試模型..." -ForegroundColor Cyan
        docker exec $containerName ollama run qwen2:7b "Hello"
        
        Write-Host ""
        Write-Host "✓ 模型測試完成" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️ 模型下載失敗，請稍後手動執行" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ 未找到 Ollama 容器" -ForegroundColor Yellow
    Write-Host "請確認容器已啟動，或稍後手動執行模型升級" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🔧 步驟 4：更新系統配置..." -ForegroundColor Cyan

# 執行配置更新腳本
if (Test-Path "scripts\update_llm_config_after_upgrade.py") {
    Write-Host "執行配置更新腳本..." -ForegroundColor Gray
    python scripts\update_llm_config_after_upgrade.py
} else {
    Write-Host "⚠️ 配置更新腳本不存在" -ForegroundColor Yellow
    Write-Host "請手動更新配置檔案" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 重新部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 服務狀態：" -ForegroundColor Cyan
Write-Host "  - Odoo: http://localhost:8069" -ForegroundColor White
Write-Host "  - Portainer: http://localhost:9000" -ForegroundColor White
Write-Host "  - Open WebUI: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "📝 下一步：" -ForegroundColor Cyan
Write-Host "  1. 檢查所有服務是否正常運行" -ForegroundColor Gray
Write-Host "  2. 驗證 LLM 模型升級" -ForegroundColor Gray
Write-Host "  3. 測試系統功能" -ForegroundColor Gray
Write-Host ""
