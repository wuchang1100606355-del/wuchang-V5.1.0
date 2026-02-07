# 使用 Docker 執行 Cloudflare Tunnel 設定腳本
# 不需要安裝 cloudflared，直接使用 Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "使用 Docker 設定 Cloudflare Tunnel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "這會使用 Docker 容器執行 cloudflared 命令" -ForegroundColor Yellow
Write-Host "不需要在系統上安裝 cloudflared" -ForegroundColor Green
Write-Host ""

# 檢查 Docker 是否可用
Write-Host "[檢查] Docker 是否可用..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] Docker 可用: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "[✗] Docker 不可用" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[✗] Docker 未安裝或無法使用" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步驟 1: 登入 Cloudflare" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "這會開啟瀏覽器讓您登入 Cloudflare" -ForegroundColor Yellow
Write-Host "請選擇網域: wuchang.org.tw" -ForegroundColor Yellow
Write-Host ""

$login = Read-Host "按 Enter 開始登入 (或輸入 'skip' 跳過)"
if ($login -ne "skip") {
    Write-Host "[執行] cloudflared tunnel login..." -ForegroundColor Yellow
    docker run --rm -it `
        -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
        cloudflare/cloudflared:latest tunnel login
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] 登入成功" -ForegroundColor Green
    } else {
        Write-Host "[✗] 登入失敗" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步驟 2: 建立命名隧道" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "建立隧道: wuchang-tunnel" -ForegroundColor Yellow
Write-Host ""

$create = Read-Host "按 Enter 建立隧道 (或輸入 'skip' 跳過)"
if ($create -ne "skip") {
    Write-Host "[執行] cloudflared tunnel create wuchang-tunnel..." -ForegroundColor Yellow
    docker run --rm -it `
        -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
        cloudflare/cloudflared:latest tunnel create wuchang-tunnel
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] 隧道建立成功" -ForegroundColor Green
        Write-Host ""
        Write-Host "重要：請記下產生的 Tunnel ID！" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "[✗] 建立隧道失敗（可能已存在）" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步驟 3: 列出隧道（確認 Tunnel ID）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[執行] 列出所有隧道..." -ForegroundColor Yellow
docker run --rm `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel list

Write-Host ""
$tunnelId = Read-Host "請輸入 Tunnel ID（例如: abc123-4567-8901-2345-6789abcdef12）"

if ([string]::IsNullOrWhiteSpace($tunnelId)) {
    Write-Host "[⚠] 未輸入 Tunnel ID，請手動查看並記錄" -ForegroundColor Yellow
} else {
    Write-Host "[✓] 已記錄 Tunnel ID: $tunnelId" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步驟 4: 配置 DNS 路由" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[執行] 配置 DNS 路由..." -ForegroundColor Yellow

$domains = @(
    "app.wuchang.org.tw",
    "ai.wuchang.org.tw",
    "admin.wuchang.org.tw",
    "monitor.wuchang.org.tw"
)

foreach ($domain in $domains) {
    Write-Host "  配置: $domain..." -ForegroundColor Yellow
    docker run --rm `
        -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
        cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel $domain
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    [✓] $domain 配置成功" -ForegroundColor Green
    } else {
        Write-Host "    [⚠] $domain 配置可能有問題" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步驟 5: 複製憑證檔案" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$credentialPath = "${env:USERPROFILE}\.cloudflared\$tunnelId.json"
$targetPath = "cloudflared\credentials.json"

Write-Host "[檢查] 憑證檔案是否存在..." -ForegroundColor Yellow

if (Test-Path $credentialPath) {
    Write-Host "[✓] 找到憑證檔案: $credentialPath" -ForegroundColor Green
    
    # 確保目標目錄存在
    if (-not (Test-Path "cloudflared")) {
        New-Item -ItemType Directory -Path "cloudflared" -Force | Out-Null
    }
    
    Copy-Item $credentialPath $targetPath -Force
    Write-Host "[✓] 憑證檔案已複製到: $targetPath" -ForegroundColor Green
} else {
    Write-Host "[✗] 憑證檔案不存在: $credentialPath" -ForegroundColor Red
    Write-Host "[提示] 請檢查憑證檔案位置或手動複製" -ForegroundColor Yellow
    Write-Host "    來源: $credentialPath" -ForegroundColor Yellow
    Write-Host "    目標: $targetPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步驟 6: 更新配置檔案" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ([string]::IsNullOrWhiteSpace($tunnelId)) {
    Write-Host "[⚠] 未輸入 Tunnel ID，請手動編輯 cloudflared\config.yml" -ForegroundColor Yellow
    Write-Host "    將 <tunnel-id> 替換為實際的 Tunnel ID" -ForegroundColor Yellow
} else {
    $configFile = "cloudflared\config.yml"
    if (Test-Path $configFile) {
        Write-Host "[更新] 配置檔案中的 Tunnel ID..." -ForegroundColor Yellow
        (Get-Content $configFile -Encoding UTF8) -replace '<tunnel-id>', $tunnelId | Set-Content $configFile -Encoding UTF8
        Write-Host "[✓] 配置檔案已更新" -ForegroundColor Green
    } else {
        Write-Host "[✗] 配置檔案不存在: $configFile" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步驟 7: 重啟容器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$restart = Read-Host "是否現在重啟 Cloudflare Tunnel 容器？(y/n)"
if ($restart -eq "y" -or $restart -eq "Y") {
    Write-Host "[執行] 重啟容器..." -ForegroundColor Yellow
    docker restart wuchangv510-cloudflared-1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] 容器已重啟" -ForegroundColor Green
        Write-Host ""
        Write-Host "[查看] 容器日誌..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        docker logs wuchangv510-cloudflared-1 --tail 10
    } else {
        Write-Host "[✗] 重啟容器失敗" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "設定完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 執行: python check_dns_status.py 驗證設定" -ForegroundColor White
Write-Host "  2. 等待 DNS 傳播（可能需要幾分鐘）" -ForegroundColor White
Write-Host "  3. 訪問 https://app.wuchang.org.tw 測試" -ForegroundColor White
Write-Host ""
