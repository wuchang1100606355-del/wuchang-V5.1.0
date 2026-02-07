#!/bin/bash
# 外網聯入快速配置助手
# 支援 CloudFlare Tunnel / 公網 IP / Tailscale VPN

echo "==================================="
echo "  Wuchang 外網聯入配置助手"
echo "==================================="
echo ""
echo "選擇聯入方案："
echo "1) CloudFlare Tunnel（推薦 ⭐ 最簡單）"
echo "2) 公網 IP + 反向代理"
echo "3) Tailscale VPN（內網穿透）"
echo "4) AWS/GCP 雲端部署"
echo ""
read -p "請選擇 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📝 CloudFlare Tunnel 配置"
        echo "================================"
        echo ""
        echo "1️⃣ 前往 https://dash.cloudflare.com"
        echo "2️⃣ 選擇 Zero Trust > Networks > Tunnels"
        echo "3️⃣ 點擊 'Create a tunnel'"
        echo "4️⃣ 選擇 Cloudflared connector"
        echo "5️⃣ 複製 token"
        echo ""
        read -p "請貼上你的 Cloudflare Tunnel Token: " TUNNEL_TOKEN
        
        # 更新 .env
        if grep -q "CLOUDFLARE_TUNNEL_TOKEN" .env; then
            sed -i "s/CLOUDFLARE_TUNNEL_TOKEN=.*/CLOUDFLARE_TUNNEL_TOKEN=$TUNNEL_TOKEN/" .env
        else
            echo "CLOUDFLARE_TUNNEL_TOKEN=$TUNNEL_TOKEN" >> .env
        fi
        
        echo ""
        echo "✅ Token 已保存"
        echo ""
        echo "啟動隧道容器..."
        docker-compose --profile system up -d cloudflared-named
        
        echo ""
        echo "📌 接下來在 CloudFlare Dashboard 設置："
        echo "   - 建立 CNAME 記錄"
        echo "   - 名稱: wuchang"
        echo "   - 內容: <tunnel-id>.cfargotunnel.com"
        echo ""
        echo "測試連接: curl -I https://wuchang.life"
        ;;
        
    2)
        echo ""
        echo "🌐 公網 IP 配置"
        echo "================================"
        echo ""
        echo "檢查你的公網 IP..."
        PUBLIC_IP=$(curl -s https://api.ipify.org)
        echo "🔍 公網 IP: $PUBLIC_IP"
        echo ""
        echo "⚙️ 路由器設定步驟："
        echo "   1. 進入 192.168.1.1（或路由器管理頁面）"
        echo "   2. 設定 > 端口轉發"
        echo "   3. 設置："
        echo "      - 外部端口: 80, 443"
        echo "      - 內部 IP: 192.168.50.84"
        echo "      - 內部端口: 80, 443"
        echo ""
        read -p "請輸入你的域名 (例: wuchang.life): " DOMAIN
        
        echo ""
        echo "更新 DNS 記錄："
        echo "   - Type: A"
        echo "   - Name: @"
        echo "   - Value: $PUBLIC_IP"
        echo ""
        echo "驗證 DNS："
        nslookup $DOMAIN
        
        echo ""
        echo "✅ Caddy 將自動取得 Let's Encrypt SSL 證書"
        echo "啟動服務: docker-compose --profile system up -d caddy"
        ;;
        
    3)
        echo ""
        echo "🔐 Tailscale VPN 配置"
        echo "================================"
        echo ""
        echo "安裝 Tailscale..."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL https://tailscale.com/install.sh | sh
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install tailscale
        else
            echo "❌ 不支援的系統，請手動安裝: https://tailscale.com/download"
            exit 1
        fi
        
        echo ""
        echo "啟動 Tailscale..."
        sudo tailscale up --advertise-routes=192.168.50.0/24 --accept-dns=true
        
        echo ""
        echo "📌 在 Tailscale Admin 啟用子網路路由："
        echo "   https://login.tailscale.com/admin/machines"
        echo ""
        echo "在遠端裝置上："
        echo "   1. 安裝 Tailscale"
        echo "   2. 登入"
        echo "   3. 存取: https://<tailscale-ip>"
        ;;
        
    4)
        echo ""
        echo "☁️ 雲端部署（GCP Cloud Run）"
        echo "================================"
        echo ""
        echo "前置要求："
        echo "   - Google Cloud Account"
        echo "   - gcloud CLI 已安裝"
        echo ""
        read -p "按 Enter 前往 Google Cloud Console: " 
        echo "https://console.cloud.google.com/run"
        
        echo ""
        echo "或執行以下指令部署："
        echo "gcloud run deploy wuchang-system \\"
        echo "  --source . \\"
        echo "  --platform managed \\"
        echo "  --region asia-east1 \\"
        echo "  --allow-unauthenticated"
        ;;
        
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

echo ""
echo "✨ 配置完成！"
echo "📖 詳細文檔: EXTERNAL_NETWORK_SOLUTIONS.md"
