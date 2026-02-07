# 完整容器卸載腳本
# 功能：安全卸載所有容器，保留數據和配置

Write-Host "========================================" -ForegroundColor Red
Write-Host "完整容器卸載工具" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "⚠️  警告：此操作將停止並移除所有容器" -ForegroundColor Yellow
Write-Host "⚠️  數據和配置檔案將被保留" -ForegroundColor Yellow
Write-Host ""

# 確認執行
$confirm = Read-Host "確認要卸載所有容器? (輸入 'YES' 確認)"
if ($confirm -ne "YES") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "📋 步驟 1：備份重要數據..." -ForegroundColor Cyan

# 建立備份目錄
$backupDir = "backups\container_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "✓ 備份目錄已建立: $backupDir" -ForegroundColor Green

# 備份資料庫（如果容器運行中）
Write-Host ""
Write-Host "📦 步驟 2：備份資料庫..." -ForegroundColor Cyan
$dbContainer = docker ps --format "{{.Names}}" | Select-String -Pattern "db|postgres"
if ($dbContainer) {
    $dbName = $dbContainer[0].ToString().Trim()
    Write-Host "找到資料庫容器: $dbName" -ForegroundColor Gray
    
    # 建立資料庫備份
    $dbBackupFile = "$backupDir\database_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    docker exec $dbName pg_dumpall -U odoo > $dbBackupFile 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 資料庫備份完成: $dbBackupFile" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 資料庫備份失敗（可能容器已停止）" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ 未找到資料庫容器" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 步驟 3：列出所有容器..." -ForegroundColor Cyan
$allContainers = docker ps -a --format "{{.Names}}"
if ($allContainers) {
    Write-Host "找到以下容器：" -ForegroundColor Gray
    $allContainers | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
} else {
    Write-Host "未找到任何容器" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🛑 步驟 4：停止所有容器..." -ForegroundColor Cyan
$stopped = 0
$allContainers | ForEach-Object {
    $containerName = $_.ToString().Trim()
    Write-Host "停止容器: $containerName" -ForegroundColor Gray
    docker stop $containerName 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $stopped++
        Write-Host "  ✓ 已停止" -ForegroundColor Green
    }
}
Write-Host "✓ 已停止 $stopped 個容器" -ForegroundColor Green

Write-Host ""
Write-Host "🗑️  步驟 5：移除所有容器..." -ForegroundColor Cyan
$removed = 0
$allContainers | ForEach-Object {
    $containerName = $_.ToString().Trim()
    Write-Host "移除容器: $containerName" -ForegroundColor Gray
    docker rm $containerName 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $removed++
        Write-Host "  ✓ 已移除" -ForegroundColor Green
    }
}
Write-Host "✓ 已移除 $removed 個容器" -ForegroundColor Green

Write-Host ""
Write-Host "🧹 步驟 6：清理未使用的資源..." -ForegroundColor Cyan

# 清理未使用的網路
docker network prune -f 2>$null | Out-Null
Write-Host "✓ 已清理未使用的網路" -ForegroundColor Green

# 清理未使用的映像檔（可選）
Write-Host ""
$cleanImages = Read-Host "是否要清理未使用的映像檔? (Y/N, 預設: N)"
if ($cleanImages -eq "Y" -or $cleanImages -eq "y") {
    docker image prune -f 2>$null | Out-Null
    Write-Host "✓ 已清理未使用的映像檔" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 容器卸載完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 統計：" -ForegroundColor Cyan
Write-Host "  - 停止容器: $stopped 個" -ForegroundColor White
Write-Host "  - 移除容器: $removed 個" -ForegroundColor White
Write-Host "  - 備份位置: $backupDir" -ForegroundColor White
Write-Host ""
Write-Host "📝 下一步：" -ForegroundColor Cyan
Write-Host "  1. 檢查備份檔案" -ForegroundColor Gray
Write-Host "  2. 執行重新部署腳本" -ForegroundColor Gray
Write-Host "  3. 恢復數據（如需要）" -ForegroundColor Gray
Write-Host ""
Write-Host "重新部署腳本: scripts\redeploy_containers.ps1" -ForegroundColor Yellow
