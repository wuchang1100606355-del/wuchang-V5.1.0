# 完整卸載並重新部署執行腳本
# 非互動模式，自動執行

param(
    [switch]$SkipConfirm = $false
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完整容器卸載與重新部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  警告：此操作將停止並移除所有容器" -ForegroundColor Yellow
Write-Host "⚠️  數據和配置檔案將被保留" -ForegroundColor Yellow
Write-Host ""

# 階段 1：卸載
Write-Host "📋 階段 1：完整卸載容器" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

# 建立備份目錄
$backupDir = "backups\container_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "✓ 備份目錄已建立: $backupDir" -ForegroundColor Green

# 檢查並備份資料庫
Write-Host ""
Write-Host "📦 備份資料庫..." -ForegroundColor Yellow
$dbContainer = docker ps --format "{{.Names}}" | Select-String -Pattern "db|postgres" | Select-Object -First 1
if ($dbContainer) {
    $dbName = $dbContainer.ToString().Trim()
    Write-Host "找到資料庫容器: $dbName" -ForegroundColor Gray
    
    $dbBackupFile = "$backupDir\database_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    docker exec $dbName pg_dumpall -U odoo 2>$null | Out-File -FilePath $dbBackupFile -Encoding utf8
    if (Test-Path $dbBackupFile -ErrorAction SilentlyContinue) {
        Write-Host "✓ 資料庫備份完成: $dbBackupFile" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 資料庫備份失敗（可能容器已停止）" -ForegroundColor Yellow
    }
}

# 停止所有容器
Write-Host ""
Write-Host "🛑 停止所有容器..." -ForegroundColor Yellow
$allContainers = docker ps -a --format "{{.Names}}"
$stopped = 0
if ($allContainers) {
    $allContainers | ForEach-Object {
        $containerName = $_.ToString().Trim()
        if ($containerName) {
            Write-Host "  停止: $containerName" -ForegroundColor Gray
            docker stop $containerName 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
                $stopped++
            }
        }
    }
}
Write-Host "✓ 已停止 $stopped 個容器" -ForegroundColor Green

# 移除所有容器
Write-Host ""
Write-Host "🗑️  移除所有容器..." -ForegroundColor Yellow
$removed = 0
if ($allContainers) {
    $allContainers | ForEach-Object {
        $containerName = $_.ToString().Trim()
        if ($containerName) {
            Write-Host "  移除: $containerName" -ForegroundColor Gray
            docker rm $containerName 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
                $removed++
            }
        }
    }
}
Write-Host "✓ 已移除 $removed 個容器" -ForegroundColor Green

# 清理未使用的資源
Write-Host ""
Write-Host "🧹 清理未使用的資源..." -ForegroundColor Yellow
docker network prune -f 2>$null | Out-Null
Write-Host "✓ 清理完成" -ForegroundColor Green

Write-Host ""
Write-Host "✅ 卸載完成！" -ForegroundColor Green
Write-Host ""

# 階段 2：重新部署
Write-Host "📋 階段 2：重新部署容器" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

# 選擇 docker-compose 檔案
$composeFile = "docker-compose.yml"
if (-not (Test-Path $composeFile)) {
    Write-Host "❌ 未找到 docker-compose.yml" -ForegroundColor Red
    exit 1
}

Write-Host "使用檔案: $composeFile" -ForegroundColor Gray
Write-Host ""

# 啟動容器
Write-Host "🚀 啟動容器（system + ui profiles）..." -ForegroundColor Yellow
docker-compose -f $composeFile --profile system --profile ui up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 容器啟動成功" -ForegroundColor Green
} else {
    Write-Host "❌ 容器啟動失敗" -ForegroundColor Red
    Write-Host "請檢查 docker-compose 檔案和日誌" -ForegroundColor Yellow
    exit 1
}

# 等待容器啟動
Write-Host ""
Write-Host "⏳ 等待容器啟動（10秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 檢查容器狀態
Write-Host ""
Write-Host "📋 檢查容器狀態..." -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}"

# 階段 3：升級 LLM 模型
Write-Host ""
Write-Host "📋 階段 3：升級 LLM 模型" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

# 查找 Ollama 容器
$ollamaContainer = docker ps --format "{{.Names}}" | Select-String -Pattern "ollama" | Select-Object -First 1
if ($ollamaContainer) {
    $containerName = $ollamaContainer.ToString().Trim()
    Write-Host "找到 Ollama 容器: $containerName" -ForegroundColor Green
    Write-Host ""
    
    # 等待 Ollama 完全啟動
    Write-Host "等待 Ollama 服務就緒（5秒）..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    Write-Host "下載 qwen2:7b 模型..." -ForegroundColor Yellow
    Write-Host "這可能需要 10-30 分鐘，請耐心等待..." -ForegroundColor Gray
    Write-Host ""
    
    docker exec $containerName ollama pull qwen2:7b
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ 模型下載成功" -ForegroundColor Green
        
        # 測試模型
        Write-Host ""
        Write-Host "🧪 測試模型..." -ForegroundColor Yellow
        docker exec $containerName ollama run qwen2:7b "Hello" 2>&1 | Select-Object -First 5
    } else {
        Write-Host ""
        Write-Host "⚠️ 模型下載失敗，請稍後手動執行" -ForegroundColor Yellow
        Write-Host "命令: docker exec $containerName ollama pull qwen2:7b" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️ 未找到 Ollama 容器" -ForegroundColor Yellow
    Write-Host "請確認容器已啟動" -ForegroundColor Gray
}

# 階段 4：更新配置
Write-Host ""
Write-Host "📋 階段 4：更新系統配置" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

if (Test-Path "scripts\update_llm_config_after_upgrade.py") {
    Write-Host "執行配置更新腳本..." -ForegroundColor Yellow
    python scripts\update_llm_config_after_upgrade.py 2>&1
} else {
    Write-Host "⚠️ 配置更新腳本不存在，請手動更新" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 重新部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 服務狀態：" -ForegroundColor Cyan
Write-Host "  - Odoo: http://localhost:8069" -ForegroundColor White
Write-Host "  - Ollama: http://localhost:11434" -ForegroundColor White
Write-Host "  - Portainer: http://localhost:9000" -ForegroundColor White
Write-Host ""
Write-Host "📝 下一步：" -ForegroundColor Cyan
Write-Host "  1. 檢查所有服務是否正常運行" -ForegroundColor Gray
Write-Host "  2. 驗證 LLM 模型升級" -ForegroundColor Gray
Write-Host "  3. 測試系統功能" -ForegroundColor Gray
Write-Host ""
