# 五常 AI - 外網存取自動設定腳本

param(
    [switch]$SkipFirewall,
    [switch]$SkipNginx,
    [switch]$SkipDNS,
    [string]$Domain = "wuchang.life",
    [string]$PublicIP = ""
)

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🌐 五常 AI - 外網存取自動設定" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ 需要管理員權限" -ForegroundColor Red
    Write-Host "請以管理員身份重新執行此腳本" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 管理員權限確認" -ForegroundColor Green
Write-Host ""

# ============================================
# 1. 偵測公網 IP
# ============================================

if (-not $PublicIP) {
    Write-Host "1️⃣  偵測公網 IP..." -ForegroundColor Yellow
    try {
        $PublicIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
        Write-Host "   ✅ 公網 IP: $PublicIP" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 無法取得公網 IP" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "1️⃣  使用指定的公網 IP: $PublicIP" -ForegroundColor Green
}

Write-Host ""

# ============================================
# 2. 設定防火牆規則
# ============================================

if (-not $SkipFirewall) {
    Write-Host "2️⃣  設定防火牆規則..." -ForegroundColor Yellow
    
    # 檢查規則是否已存在
    $existingRules = Get-NetFirewallRule -ErrorAction SilentlyContinue | Where-Object {$_.DisplayName -like "Wuchang-*"}
    
    if ($existingRules) {
        Write-Host "   ⚠️  發現現有規則，是否覆蓋？(y/n)" -ForegroundColor Yellow
        $confirm = Read-Host
        if ($confirm -eq "y") {
            $existingRules | Remove-NetFirewallRule
            Write-Host "   🗑️  已移除舊規則" -ForegroundColor Gray
        }
    }
    
    # HTTPS (443)
    New-NetFirewallRule -DisplayName "Wuchang-HTTPS" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 443 -ErrorAction SilentlyContinue | Out-Null
    Write-Host "   ✅ HTTPS (443)" -ForegroundColor Green
    
    # 同步服務 (8766)
    New-NetFirewallRule -DisplayName "Wuchang-Sync" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8766 -ErrorAction SilentlyContinue | Out-Null
    Write-Host "   ✅ Sync Service (8766)" -ForegroundColor Green
    
    # Odoo (8069) - 僅內網
    New-NetFirewallRule -DisplayName "Wuchang-Odoo-LAN" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8069 -RemoteAddress 192.168.50.0/24 -ErrorAction SilentlyContinue | Out-Null
    Write-Host "   ✅ Odoo (8069, LAN only)" -ForegroundColor Green
    
    Write-Host ""
}

# ============================================
# 3. 檢查並安裝 Nginx
# ============================================

if (-not $SkipNginx) {
    Write-Host "3️⃣  檢查 Nginx..." -ForegroundColor Yellow
    
    $nginxPath = "C:\tools\nginx\nginx.exe"
    
    if (-not (Test-Path $nginxPath)) {
        Write-Host "   ⚠️  Nginx 未安裝" -ForegroundColor Yellow
        Write-Host "   是否安裝 Nginx？(y/n)" -ForegroundColor Yellow
        $confirm = Read-Host
        
        if ($confirm -eq "y") {
            # 檢查 Chocolatey
            $choco = Get-Command choco -ErrorAction SilentlyContinue
            if ($choco) {
                Write-Host "   📦 使用 Chocolatey 安裝..." -ForegroundColor Gray
                choco install nginx -y
                Write-Host "   ✅ Nginx 安裝完成" -ForegroundColor Green
            } else {
                Write-Host "   ❌ 請先安裝 Chocolatey 或手動安裝 Nginx" -ForegroundColor Red
                Write-Host "   Chocolatey: https://chocolatey.org/install" -ForegroundColor Gray
                Write-Host "   Nginx: https://nginx.org/en/download.html" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "   ✅ Nginx 已安裝" -ForegroundColor Green
    }
    
    Write-Host ""
}

# ============================================
# 4. 生成 Nginx 配置
# ============================================

if (-not $SkipNginx -and (Test-Path "C:\tools\nginx")) {
    Write-Host "4️⃣  生成 Nginx 配置..." -ForegroundColor Yellow
    
    $nginxConfig = @"
# 五常 AI - Nginx 配置
# 生成時間: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# 上游服務
upstream odoo {
    server 127.0.0.1:8069;
}

upstream sync_service {
    server 127.0.0.1:8766;
}

# HTTP 重導向
server {
    listen 80;
    server_name $Domain sync.$Domain api.$Domain;
    
    location /.well-known/acme-challenge/ {
        root C:/Certbot/webroot;
    }
    
    location / {
        return 301 https://`$host`$request_uri;
    }
}

# HTTPS 主站（Odoo）
server {
    listen 443 ssl http2;
    server_name $Domain www.$Domain;
    
    # SSL 憑證（請更新路徑）
    ssl_certificate C:/Certbot/live/$Domain/fullchain.pem;
    ssl_certificate_key C:/Certbot/live/$Domain/privkey.pem;
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 安全標頭
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # 客戶端限制
    client_max_body_size 100M;
    
    # Odoo 代理
    location / {
        proxy_pass http://odoo;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        
        # WebSocket 支援
        proxy_http_version 1.1;
        proxy_set_header Upgrade `$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}

# 同步服務
server {
    listen 443 ssl http2;
    server_name sync.$Domain;
    
    ssl_certificate C:/Certbot/live/$Domain/fullchain.pem;
    ssl_certificate_key C:/Certbot/live/$Domain/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://sync_service;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        
        client_max_body_size 500M;
        proxy_request_buffering off;
        
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
"@
    
    $configPath = "C:\tools\nginx\conf\wuchang.conf"
    $nginxConfig | Out-File -FilePath $configPath -Encoding UTF8 -Force
    Write-Host "   ✅ 配置已生成: $configPath" -ForegroundColor Green
    
    Write-Host "   ⚠️  請記得:" -ForegroundColor Yellow
    Write-Host "      1. 更新 SSL 憑證路徑" -ForegroundColor Gray
    Write-Host "      2. 在 nginx.conf 引入此配置" -ForegroundColor Gray
    Write-Host "      3. 測試並重啟 Nginx" -ForegroundColor Gray
    
    Write-Host ""
}

# ============================================
# 5. DNS 配置提示
# ============================================

if (-not $SkipDNS) {
    Write-Host "5️⃣  DNS 配置指引" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   請在域名管理面板設定以下記錄:" -ForegroundColor White
    Write-Host ""
    Write-Host "   A 記錄:" -ForegroundColor Cyan
    Write-Host "   類型: A" -ForegroundColor Gray
    Write-Host "   名稱: @" -ForegroundColor Gray
    Write-Host "   內容: $PublicIP" -ForegroundColor Gray
    Write-Host "   TTL: Auto" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   CNAME 記錄:" -ForegroundColor Cyan
    Write-Host "   sync.$Domain → $Domain" -ForegroundColor Gray
    Write-Host "   api.$Domain → $Domain" -ForegroundColor Gray
    Write-Host "   www.$Domain → $Domain" -ForegroundColor Gray
    Write-Host ""
}

# ============================================
# 6. 路由器設定提示
# ============================================

Write-Host "6️⃣  路由器 Port Forwarding" -ForegroundColor Yellow
Write-Host ""
Write-Host "   請在路由器管理面板 (通常是 192.168.50.1) 設定:" -ForegroundColor White
Write-Host ""
Write-Host "   規則 1: HTTPS" -ForegroundColor Cyan
Write-Host "   外部端口: 443  →  內部: 192.168.50.249:443" -ForegroundColor Gray
Write-Host ""
Write-Host "   規則 2: 同步服務" -ForegroundColor Cyan
Write-Host "   外部端口: 8766  →  內部: 192.168.50.249:8766" -ForegroundColor Gray
Write-Host ""

# ============================================
# 7. SSL 憑證指引
# ============================================

Write-Host "7️⃣  SSL 憑證設定" -ForegroundColor Yellow
Write-Host ""
Write-Host "   方案 1: Cloudflare 自動 SSL (推薦)" -ForegroundColor Cyan
Write-Host "   - 前往 Cloudflare Dashboard" -ForegroundColor Gray
Write-Host "   - SSL/TLS → 設定為「完整(嚴格)」" -ForegroundColor Gray
Write-Host ""
Write-Host "   方案 2: Let's Encrypt" -ForegroundColor Cyan
Write-Host "   - choco install certbot -y" -ForegroundColor Gray
Write-Host "   - certbot certonly --standalone -d $Domain" -ForegroundColor Gray
Write-Host ""

# ============================================
# 8. 生成測試腳本
# ============================================

Write-Host "8️⃣  生成測試腳本..." -ForegroundColor Yellow

$testScript = @"
# 五常 AI - 外網連線測試腳本

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🧪 外網連線測試" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

`$domain = "$Domain"
`$tests = @()

# 測試 1: DNS 解析
Write-Host "1️⃣  DNS 解析測試..." -ForegroundColor Yellow
try {
    `$dnsResult = Resolve-DnsName -Name `$domain -ErrorAction Stop
    `$resolvedIP = `$dnsResult[0].IPAddress
    Write-Host "   ✅ `$domain → `$resolvedIP" -ForegroundColor Green
    `$tests += @{Test="DNS"; Status="✅"; Result=`$resolvedIP}
} catch {
    Write-Host "   ❌ DNS 解析失敗" -ForegroundColor Red
    `$tests += @{Test="DNS"; Status="❌"; Result="Failed"}
}

Write-Host ""

# 測試 2: HTTPS 連線
Write-Host "2️⃣  HTTPS 連線測試..." -ForegroundColor Yellow
try {
    `$httpResult = Invoke-WebRequest -Uri "https://`$domain" -UseBasicParsing -TimeoutSec 10
    Write-Host "   ✅ HTTP Status: `$(`$httpResult.StatusCode)" -ForegroundColor Green
    `$tests += @{Test="HTTPS"; Status="✅"; Result=`$httpResult.StatusCode}
} catch {
    Write-Host "   ❌ HTTPS 連線失敗: `$_" -ForegroundColor Red
    `$tests += @{Test="HTTPS"; Status="❌"; Result="Failed"}
}

Write-Host ""

# 測試 3: SSL 憑證
Write-Host "3️⃣  SSL 憑證檢查..." -ForegroundColor Yellow
try {
    `$tcpClient = New-Object System.Net.Sockets.TcpClient(`$domain, 443)
    `$sslStream = New-Object System.Net.Security.SslStream(`$tcpClient.GetStream(), `$false)
    `$sslStream.AuthenticateAsClient(`$domain)
    `$cert = `$sslStream.RemoteCertificate
    `$expiryDate = [DateTime]::Parse(`$cert.GetExpirationDateString())
    `$daysLeft = (`$expiryDate - (Get-Date)).Days
    Write-Host "   ✅ 憑證有效，剩餘 `$daysLeft 天" -ForegroundColor Green
    `$sslStream.Close()
    `$tcpClient.Close()
    `$tests += @{Test="SSL"; Status="✅"; Result="`$daysLeft days"}
} catch {
    Write-Host "   ❌ SSL 憑證檢查失敗" -ForegroundColor Red
    `$tests += @{Test="SSL"; Status="❌"; Result="Failed"}
}

Write-Host ""

# 測試 4: 同步服務
Write-Host "4️⃣  同步服務測試..." -ForegroundColor Yellow
try {
    `$syncUrl = "https://sync.`$domain/ping"
    `$headers = @{"X-Sync-Token" = "`$env:SYNC_SECRET"}
    `$syncResult = Invoke-WebRequest -Uri `$syncUrl -Headers `$headers -UseBasicParsing -TimeoutSec 10
    Write-Host "   ✅ 同步服務正常" -ForegroundColor Green
    `$tests += @{Test="Sync"; Status="✅"; Result="OK"}
} catch {
    Write-Host "   ⚠️  同步服務測試失敗（可能未設定 SYNC_SECRET）" -ForegroundColor Yellow
    `$tests += @{Test="Sync"; Status="⚠️"; Result="Check Token"}
}

Write-Host ""

# 總結
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  📊 測試總結" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

`$tests | ForEach-Object {
    Write-Host "  `$(`$_.Status) `$(`$_.Test): `$(`$_.Result)" -ForegroundColor White
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
"@

$testScriptPath = "c:\wuchang V5.1.0\network_config\test_external_access.ps1"
$testScript | Out-File -FilePath $testScriptPath -Encoding UTF8 -Force
Write-Host "   ✅ 測試腳本已生成: $testScriptPath" -ForegroundColor Green

Write-Host ""

# ============================================
# 完成
# ============================================

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  ✅ 設定完成" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "後續步驟:" -ForegroundColor Yellow
Write-Host "  1. 設定 DNS 記錄（參考上方指引）" -ForegroundColor White
Write-Host "  2. 設定路由器 Port Forwarding" -ForegroundColor White
Write-Host "  3. 取得並安裝 SSL 憑證" -ForegroundColor White
Write-Host "  4. 配置並重啟 Nginx" -ForegroundColor White
Write-Host "  5. 執行測試腳本驗證" -ForegroundColor White
Write-Host ""
Write-Host "文檔參考:" -ForegroundColor Yellow
Write-Host "  c:\wuchang V5.1.0\network_config\external_access_guide.md" -ForegroundColor Gray
Write-Host ""
Write-Host "測試腳本:" -ForegroundColor Yellow
Write-Host "  .\test_external_access.ps1" -ForegroundColor Gray
Write-Host ""
