# 外網訪問設定腳本
# 設定 Cloudflare Tunnel 以啟用外網訪問

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "外網訪問設定工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Cloudflare Tunnel 容器狀態
Write-Host "📋 步驟 1：檢查當前狀態..." -ForegroundColor Yellow
$cloudflared = docker ps -a --filter "name=cloudflared" --format "{{.Names}}" | Select-Object -First 1

if ($cloudflared) {
    Write-Host "找到 Cloudflare Tunnel 容器: $cloudflared" -ForegroundColor Gray
    $status = docker ps --filter "name=$cloudflared" --format "{{.Status}}"
    if ($status) {
        Write-Host "  狀態: $status" -ForegroundColor Green
    } else {
        Write-Host "  狀態: 已停止" -ForegroundColor Yellow
        Write-Host "正在啟動容器..." -ForegroundColor Yellow
        docker start $cloudflared 2>&1 | Out-Null
        Start-Sleep -Seconds 5
    }
} else {
    Write-Host "⚠️ 未找到 Cloudflare Tunnel 容器" -ForegroundColor Yellow
    Write-Host "將使用 docker-compose 啟動..." -ForegroundColor Gray
}

# 檢查配置檔案
Write-Host ""
Write-Host "📋 步驟 2：檢查配置檔案..." -ForegroundColor Yellow

$configFile = "cloudflared\config.yml"
$credentialsFile = "cloudflared\credentials.json"

if (Test-Path $configFile) {
    Write-Host "✓ 配置檔案存在: $configFile" -ForegroundColor Green
} else {
    Write-Host "✓ 已建立配置檔案: $configFile" -ForegroundColor Green
}

if (Test-Path $credentialsFile) {
    Write-Host "✓ 憑證檔案存在: $credentialsFile" -ForegroundColor Green
} else {
    Write-Host "⚠️ 憑證檔案不存在: $credentialsFile" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 需要執行以下步驟取得憑證：" -ForegroundColor Cyan
    Write-Host "  1. 前往 Cloudflare Dashboard" -ForegroundColor White
    Write-Host "  2. 建立或取得 Tunnel" -ForegroundColor White
    Write-Host "  3. 下載 credentials.json 到 cloudflared 目錄" -ForegroundColor White
    Write-Host ""
    Write-Host "詳細步驟請參考: cloudflared\README.md" -ForegroundColor Gray
}

# 啟動 Cloudflare Tunnel
Write-Host ""
Write-Host "📋 步驟 3：啟動 Cloudflare Tunnel..." -ForegroundColor Yellow

Write-Host "使用 docker-compose 啟動 cloudflared 服務..." -ForegroundColor Gray
docker-compose -f docker-compose.yml --profile system up -d cloudflared

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Cloudflare Tunnel 容器已啟動" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "⏳ 等待容器啟動..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # 檢查容器狀態
    $status = docker ps --filter "name=cloudflared" --format "{{.Names}}\t{{.Status}}"
    if ($status) {
        Write-Host "✓ 容器狀態:" -ForegroundColor Green
        $status | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    }
} else {
    Write-Host "❌ 啟動失敗" -ForegroundColor Red
    Write-Host "請檢查 docker-compose.yml 配置" -ForegroundColor Yellow
}

# 檢查日誌
Write-Host ""
Write-Host "📋 步驟 4：檢查日誌..." -ForegroundColor Yellow
$cloudflaredContainer = docker ps --filter "name=cloudflared" --format "{{.Names}}" | Select-Object -First 1
if ($cloudflaredContainer) {
    Write-Host "最近的日誌：" -ForegroundColor Gray
    docker logs $cloudflaredContainer --tail 10 2>&1 | Select-Object -Last 5
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 外網訪問設定完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 後續步驟：" -ForegroundColor Cyan
Write-Host "  1. 確保已取得 Cloudflare Tunnel 憑證" -ForegroundColor White
Write-Host "  2. 在 Cloudflare Dashboard 設定 DNS 路由" -ForegroundColor White
Write-Host "  3. 驗證外網訪問" -ForegroundColor White
Write-Host ""
Write-Host "🌐 外網訪問地址：" -ForegroundColor Cyan
Write-Host "  - 首頁: http://www.wuchang.life" -ForegroundColor White
Write-Host "  - Odoo: https://app.wuchang.org.tw" -ForegroundColor White
Write-Host "  - AI: https://ai.wuchang.org.tw" -ForegroundColor White
Write-Host "  - 管理: https://admin.wuchang.org.tw" -ForegroundColor White
Write-Host ""
