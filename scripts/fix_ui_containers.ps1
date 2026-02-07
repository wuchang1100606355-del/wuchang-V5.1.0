# UI 容器修復腳本
# 自動修復常見的 UI 容器問題

param(
    [switch]$RestartAll,
    [switch]$Rebuild,
    [switch]$Clean
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "UI 容器修復工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 步驟 1: 停止所有容器
Write-Host "`n[步驟 1/5] 停止容器..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    docker-compose down
    Write-Host "✓ 容器已停止" -ForegroundColor Green
} else {
    Write-Host "⚠ docker-compose.yml 不存在" -ForegroundColor Yellow
}

# 步驟 2: 清理（如果指定）
if ($Clean) {
    Write-Host "`n[步驟 2/5] 清理容器和映像..." -ForegroundColor Yellow
    docker-compose down -v --remove-orphans
    docker system prune -f
    Write-Host "✓ 清理完成" -ForegroundColor Green
}

# 步驟 3: 重建（如果指定）
if ($Rebuild) {
    Write-Host "`n[步驟 3/5] 重建容器..." -ForegroundColor Yellow
    docker-compose build --no-cache
    Write-Host "✓ 重建完成" -ForegroundColor Green
}

# 步驟 4: 啟動容器
Write-Host "`n[步驟 4/5] 啟動容器..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    docker-compose up -d
    Write-Host "✓ 容器已啟動" -ForegroundColor Green
    
    # 等待容器啟動
    Write-Host "`n等待容器啟動（10 秒）..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
} else {
    Write-Host "✗ docker-compose.yml 不存在" -ForegroundColor Red
}

# 步驟 5: 驗證服務
Write-Host "`n[步驟 5/5] 驗證服務..." -ForegroundColor Yellow
$endpoints = @(
    @{Name="Odoo"; URL="http://localhost:8069/web/health"},
    @{Name="AI Assistant"; URL="http://localhost:8080/health"},
    @{Name="Status Dashboard"; URL="http://localhost:3001/health"}
)

$allHealthy = $true
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.URL -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✓ $($endpoint.Name) : 正常" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $($endpoint.Name) : 無回應" -ForegroundColor Red
        $allHealthy = $false
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($allHealthy) {
    Write-Host "✓ 所有服務正常" -ForegroundColor Green
} else {
    Write-Host "⚠ 部分服務異常，請檢查日誌" -ForegroundColor Yellow
    Write-Host "查看日誌: docker-compose logs -f" -ForegroundColor White
}
Write-Host "========================================" -ForegroundColor Cyan
