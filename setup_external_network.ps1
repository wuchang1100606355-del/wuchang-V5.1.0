# 外網聯入快速配置助手（PowerShell）
# 支援 CloudFlare Tunnel / 公網 IP / Tailscale VPN

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "  Wuchang 外網聯入配置助手" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "選擇聯入方案：" -ForegroundColor Green
Write-Host "1) CloudFlare Tunnel（推薦 ⭐ 最簡單）" -ForegroundColor Yellow
Write-Host "2) 公網 IP + 反向代理" -ForegroundColor Yellow
Write-Host "3) Tailscale VPN（內網穿透）" -ForegroundColor Yellow
Write-Host "4) 檢查當前網路狀態" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "請選擇 (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "📝 CloudFlare Tunnel 配置" -ForegroundColor Cyan
        Write-Host "================================"
        Write-Host ""
        Write-Host "1️⃣ 前往 https://dash.cloudflare.com" -ForegroundColor White
        Write-Host "2️⃣ 選擇 Zero Trust > Networks > Tunnels" -ForegroundColor White
        Write-Host "3️⃣ 點擊 'Create a tunnel'" -ForegroundColor White
        Write-Host "4️⃣ 選擇 Cloudflared connector" -ForegroundColor White
        Write-Host "5️⃣ 複製 token" -ForegroundColor White
        Write-Host ""
        
        $TUNNEL_TOKEN = Read-Host "請貼上你的 Cloudflare Tunnel Token"
        
        # 更新 .env
        $envFile = ".env"
        if (Test-Path $envFile) {
            $content = Get-Content $envFile
            if ($content -match "CLOUDFLARE_TUNNEL_TOKEN") {
                $content = $content -replace "CLOUDFLARE_TUNNEL_TOKEN=.*", "CLOUDFLARE_TUNNEL_TOKEN=$TUNNEL_TOKEN"
            } else {
                $content += "`nCLOUDFLARE_TUNNEL_TOKEN=$TUNNEL_TOKEN"
            }
            $content | Set-Content $envFile
        } else {
            "CLOUDFLARE_TUNNEL_TOKEN=$TUNNEL_TOKEN" | Out-File $envFile
        }
        
        Write-Host ""
        Write-Host "✅ Token 已保存" -ForegroundColor Green
        Write-Host ""
        Write-Host "啟動隧道容器..." -ForegroundColor Yellow
        docker-compose --profile system up -d cloudflared-named
        
        Write-Host ""
        Write-Host "📌 接下來在 CloudFlare Dashboard 設置：" -ForegroundColor Cyan
        Write-Host "   - 建立 CNAME 記錄" -ForegroundColor White
        Write-Host "   - 名稱: wuchang" -ForegroundColor White
        Write-Host "   - 內容: <tunnel-id>.cfargotunnel.com" -ForegroundColor White
        Write-Host ""
        Write-Host "測試連接: curl -I https://wuchang.life" -ForegroundColor Yellow
    }
    
    "2" {
        Write-Host ""
        Write-Host "🌐 公網 IP 配置" -ForegroundColor Cyan
        Write-Host "================================"
        Write-Host ""
        Write-Host "檢查你的公網 IP..." -ForegroundColor Yellow
        
        try {
            $PUBLIC_IP = Invoke-RestMethod -Uri "https://api.ipify.org" -Method Get
            Write-Host "🔍 公網 IP: $PUBLIC_IP" -ForegroundColor Green
        } catch {
            Write-Host "❌ 無法取得公網 IP，請檢查網路連線" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "⚙️ 路由器設定步驟：" -ForegroundColor Cyan
        Write-Host "   1. 進入 192.168.1.1（或路由器管理頁面）" -ForegroundColor White
        Write-Host "   2. 設定 > 端口轉發" -ForegroundColor White
        Write-Host "   3. 設置：" -ForegroundColor White
        Write-Host "      - 外部端口: 80, 443" -ForegroundColor White
        Write-Host "      - 內部 IP: 192.168.50.84" -ForegroundColor White
        Write-Host "      - 內部端口: 80, 443" -ForegroundColor White
        Write-Host ""
        
        $DOMAIN = Read-Host "請輸入你的域名 (例: wuchang.life)"
        
        Write-Host ""
        Write-Host "更新 DNS 記錄：" -ForegroundColor Cyan
        Write-Host "   - Type: A" -ForegroundColor White
        Write-Host "   - Name: @" -ForegroundColor White
        Write-Host "   - Value: $PUBLIC_IP" -ForegroundColor White
        Write-Host ""
        
        Write-Host "驗證 DNS：" -ForegroundColor Yellow
        nslookup $DOMAIN
        
        Write-Host ""
        Write-Host "✅ Caddy 將自動取得 Let's Encrypt SSL 證書" -ForegroundColor Green
        Write-Host "啟動服務: docker-compose --profile system up -d caddy" -ForegroundColor Yellow
    }
    
    "3" {
        Write-Host ""
        Write-Host "🔐 Tailscale VPN 配置" -ForegroundColor Cyan
        Write-Host "================================"
        Write-Host ""
        Write-Host "安裝 Tailscale..." -ForegroundColor Yellow
        
        # Windows 安裝（使用 Chocolatey 或直接下載）
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install tailscale -y
        } else {
            Write-Host "使用 Chocolatey 安裝："
            Write-Host "choco install tailscale -y" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "啟動 Tailscale..." -ForegroundColor Yellow
        tailscale up --advertise-routes=192.168.50.0/24 --accept-dns
        
        Write-Host ""
        Write-Host "📌 在 Tailscale Admin 啟用子網路路由：" -ForegroundColor Cyan
        Write-Host "   https://login.tailscale.com/admin/machines" -ForegroundColor White
        Write-Host ""
        Write-Host "在遠端裝置上：" -ForegroundColor Cyan
        Write-Host "   1. 安裝 Tailscale" -ForegroundColor White
        Write-Host "   2. 登入" -ForegroundColor White
        Write-Host "   3. 存取: https://<tailscale-ip>" -ForegroundColor White
    }
    
    "4" {
        Write-Host ""
        Write-Host "🔍 當前網路狀態" -ForegroundColor Cyan
        Write-Host "================================"
        Write-Host ""
        
        # 公網 IP
        Write-Host "📍 公網 IP：" -ForegroundColor Yellow
        try {
            $pubIP = Invoke-RestMethod -Uri "https://api.ipify.org" -Method Get
            Write-Host "   $pubIP" -ForegroundColor Green
        } catch {
            Write-Host "   無法取得（可能無外網或 ISP 限制）" -ForegroundColor Red
        }
        
        # 本機 IP
        Write-Host ""
        Write-Host "📍 本機 IP：" -ForegroundColor Yellow
        $localIPs = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "172.*" }
        foreach ($ip in $localIPs) {
            Write-Host "   $($ip.IPAddress) ($($ip.InterfaceAlias))" -ForegroundColor White
        }
        
        # 防火牆狀態
        Write-Host ""
        Write-Host "🔥 防火牆狀態：" -ForegroundColor Yellow
        Get-NetFirewallProfile | Select-Object Name, Enabled | Format-Table -AutoSize
        
        # 開放的埠
        Write-Host ""
        Write-Host "🔓 開放的服務埠：" -ForegroundColor Yellow
        $ports = @(80, 443, 8069, 8080, 3001)
        foreach ($port in $ports) {
            $listening = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
            if ($listening) {
                Write-Host "   埠 $port: ✅ LISTENING" -ForegroundColor Green
            } else {
                Write-Host "   埠 $port: ❌ 未監聽" -ForegroundColor Red
            }
        }
        
        # DNS 名稱解析
        Write-Host ""
        Write-Host "🌐 DNS 測試：" -ForegroundColor Yellow
        $domains = @("wuchang.life", "odoo.wuchang.life", "ai.wuchang.life")
        foreach ($domain in $domains) {
            try {
                $ip = [System.Net.Dns]::GetHostAddresses($domain) | Select-Object -First 1
                Write-Host "   $domain -> $ip" -ForegroundColor Green
            } catch {
                Write-Host "   $domain -> ❌ 無法解析" -ForegroundColor Red
            }
        }
        
        # 容器狀態
        Write-Host ""
        Write-Host "🐳 Docker 容器狀態：" -ForegroundColor Yellow
        docker-compose ps --all
        
        Write-Host ""
        Write-Host "💡 建議：" -ForegroundColor Cyan
        Write-Host "   - 如果沒有公網 IP，使用 CloudFlare Tunnel" -ForegroundColor White
        Write-Host "   - 如果有公網 IP 但防火牆開啟，檢查端口轉發" -ForegroundColor White
        Write-Host "   - 如果 DNS 無法解析，檢查域名 DNS 記錄" -ForegroundColor White
    }
    
    default {
        Write-Host "❌ 無效選擇" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✨ 配置助手完成！" -ForegroundColor Green
Write-Host "📖 詳細文檔: EXTERNAL_NETWORK_SOLUTIONS.md" -ForegroundColor Cyan
