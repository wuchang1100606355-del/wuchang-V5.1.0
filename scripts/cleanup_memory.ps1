# Docker 記憶體清理腳本
# 清理未使用的 Docker 資源以釋放記憶體

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker 記憶體清理工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步驟 1：清理未使用的容器
Write-Host "🧹 步驟 1：清理未使用的容器..." -ForegroundColor Yellow
$stoppedContainers = docker ps -a --filter "status=created" --filter "status=exited" --format "{{.Names}}"
if ($stoppedContainers) {
    Write-Host "找到未使用的容器：" -ForegroundColor Gray
    $stoppedContainers | ForEach-Object {
        Write-Host "  - $_" -ForegroundColor Gray
        docker rm $_ 2>$null | Out-Null
    }
    Write-Host "✓ 已清理未使用的容器" -ForegroundColor Green
} else {
    Write-Host "✓ 沒有未使用的容器" -ForegroundColor Green
}

# 步驟 2：清理未使用的映像檔
Write-Host ""
Write-Host "🧹 步驟 2：清理未使用的映像檔..." -ForegroundColor Yellow
$danglingImages = docker images -f "dangling=true" -q
if ($danglingImages) {
    Write-Host "找到未使用的映像檔：" -ForegroundColor Gray
    docker rmi $danglingImages 2>$null | Out-Null
    Write-Host "✓ 已清理未使用的映像檔" -ForegroundColor Green
} else {
    Write-Host "✓ 沒有未使用的映像檔" -ForegroundColor Green
}

# 步驟 3：清理未使用的網路
Write-Host ""
Write-Host "🧹 步驟 3：清理未使用的網路..." -ForegroundColor Yellow
docker network prune -f 2>$null | Out-Null
Write-Host "✓ 已清理未使用的網路" -ForegroundColor Green

# 步驟 4：清理構建快取
Write-Host ""
Write-Host "🧹 步驟 4：清理構建快取..." -ForegroundColor Yellow
docker builder prune -f 2>$null | Out-Null
Write-Host "✓ 已清理構建快取" -ForegroundColor Green

# 步驟 5：清理未使用的映像檔（保留正在使用的）
Write-Host ""
Write-Host "🧹 步驟 5：清理未使用的映像檔（深度清理）..." -ForegroundColor Yellow
Write-Host "⚠️  這將刪除所有未使用的映像檔（保留正在運行容器使用的映像檔）" -ForegroundColor Yellow
docker image prune -a -f 2>$null | Out-Null
Write-Host "✓ 已清理未使用的映像檔" -ForegroundColor Green

# 顯示清理後的資源使用情況
Write-Host ""
Write-Host "📊 清理後的資源使用情況：" -ForegroundColor Cyan
docker system df

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 記憶體清理完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
