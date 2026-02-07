# 🌐 外網聯入方案

**更新日期**：2026 年 1 月 11 日  
**系統**：Wuchang V5.1.0 (Odoo 17 Docker)

---

## 📊 當前系統狀態

### 網路配置

-   **LAN IP**：192.168.50.84（本機私網）
-   **IPv6**：2001:b011:300a:91cf:77e4:8656:8e87:6f5b（公網 IPv6）
-   **防火牆**：Public 啟用，Domain/Private 關閉

### 開放服務

| 埠   | 服務          | 狀態         |
| ---- | ------------- | ------------ |
| 80   | HTTP (Caddy)  | ✅ LISTENING |
| 443  | HTTPS (Caddy) | ✅ LISTENING |
| 8069 | Odoo Web      | ✅ LISTENING |
| 8080 | AI 服務       | ✅ LISTENING |
| 3001 | Uptime Kuma   | ✅ LISTENING |

### 已配置的域名

```
wuchang.life              (主域)
odoo.wuchang.life         (Odoo)
ai.wuchang.life           (AI 服務)
llm.wuchang.life          (Ollama)
status.wuchang.life       (監控)
housing.wuchang.life      (社區)
pos.wuchang.life          (POS 系統)
```

---

## 🚀 外網聯入方案（4 種選擇）

### ✅ 方案 1：CloudFlare Tunnel（推薦 ⭐⭐⭐⭐⭐）

**優勢：**

-   ✅ 無需公網 IP
-   ✅ 無需設定防火牆/端口轉發
-   ✅ 免費 SSL/TLS（自動管理）
-   ✅ DDoS 保護內建
-   ✅ 支持無限子域

**現有配置：**

-   `cloudflared` 容器已在 docker-compose.yml 中定義
-   `cloudflared-named` 支持命名隧道

**實施步驟：**

```bash
# 1. 取得 CloudFlare Tunnel Token
# 前往 https://dash.cloudflare.com > Zero Trust > Networks > Tunnels
# 建立新隧道 → 複製 TOKEN

# 2. 設定環境變數
echo "CLOUDFLARE_TUNNEL_TOKEN=eyJh..." >> .env

# 3. 啟動隧道
docker-compose --profile system up -d cloudflared-named

# 4. 在 CloudFlare Dashboard 設置 DNS
# 類型：CNAME
# 名稱：wuchang
# 內容：<tunnel-id>.cfargotunnel.com

# 5. 驗證連接
curl https://wuchang.life
```

**成本：** 免費 / 月 $20+（企業功能）

---

### ✅ 方案 2：反向代理 + 公網 IP（傳統方案）

**優勢：**

-   ✅ 完全控制
-   ✅ 低延遲
-   ✅ 適合專業部署

**前置要求：**

-   ISP 公網 IP（靜態或動態）
-   域名 DNS A 記錄指向公網 IP
-   路由器端口轉發設定

**實施步驟：**

```bash
# 1. 檢查公網 IP
curl https://api.ipify.org

# 2. 路由器設定（以常見機型為例）
# 進入 192.168.1.1
# 設定 > 端口轉發
# - 外部端口：80, 443
# - 內部 IP：192.168.50.84
# - 內部端口：80, 443

# 3. 更新 Caddyfile（使用固定域名）
# 編輯 wuchang_os/Caddyfile，確保域名已配置

# 4. 更新 DNS A 記錄
# Type: A
# Name: @
# Value: <your-public-ip>

# 5. 測試 HTTPS（Caddy 自動管理 Let's Encrypt）
curl -I https://wuchang.life
```

**成本：** 免費（需 ISP 支持）

---

### ✅ 方案 3：AWS / Azure / GCP 負載均衡器

**優勢：**

-   ✅ 高可用性
-   ✅ 自動擴展
-   ✅ CDN 整合
-   ✅ 企業級支持

**實施步驟：**

```bash
# 1. 部署至 GCP Cloud Run
gcloud run deploy wuchang-system \
  --image gcr.io/wuchang/odoo:latest \
  --platform managed \
  --region asia-east1 \
  --port 8069 \
  --allow-unauthenticated

# 2. 綁定自訂域名
# GCP Console > Cloud Run > 服務 > 設定自訂網域

# 3. 設定 Cloud CDN
gcloud compute backend-services create wuchang-backend \
  --global \
  --enable-cdn
```

**成本：** $5-50/月（依流量）

---

### ✅ 方案 4：VPN + 內網穿透（對等聯網）

**優勢：**

-   ✅ 最安全（端對端加密）
-   ✅ 無需公網暴露
-   ✅ P2P 連接可靠

**工具選項：**

-   **Tailscale**（推薦）
-   WireGuard
-   ZeroTier

**實施步驟（Tailscale）：**

```bash
# 1. 安裝 Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# 2. 啟動並登入
sudo tailscale up --advertise-routes=192.168.50.0/24

# 3. 在 Tailscale Admin 啟用子網路路由
# https://login.tailscale.com/admin/machines

# 4. 遠端客戶端連接
# 在其他設備上安裝 Tailscale
# 自動獲得 VPN IP（如 100.123.45.67）

# 5. 存取系統
# https://100.123.45.67 （來自 VPN 內網）
```

**成本：** 免費（個人 3 台裝置）/ $8-120/月

---

## 📋 推薦配置方案

### 小規模社區（<100 用戶）

```
優先順序：
1️⃣ CloudFlare Tunnel（簡單、免費、安全）
2️⃣ Tailscale VPN（員工內網存取）
```

### 中型部署（100-1000 用戶）

```
優先順序：
1️⃣ 公網 IP + Caddy 反向代理
2️⃣ CloudFlare + 進階安全規則
```

### 企業級部署（>1000 用戶）

```
優先順序：
1️⃣ GCP / AWS 負載均衡
2️⃣ CloudFlare 企業版
3️⃣ 區域 CDN
```

---

## 🔧 快速實施清單

### 使用 CloudFlare Tunnel（推薦）

-   [ ] 登入 https://dash.cloudflare.com
-   [ ] Zero Trust > Tunnels > 建立隧道
-   [ ] 複製 `cloudflared` 命令的 TOKEN
-   [ ] 在 `.env` 中設定 `CLOUDFLARE_TUNNEL_TOKEN`
-   [ ] 執行 `docker-compose --profile system up -d cloudflared-named`
-   [ ] 在 CloudFlare DNS 設定 CNAME 記錄
-   [ ] 測試：`curl -I https://wuchang.life`

### 使用公網 IP

-   [ ] 確認 ISP 提供公網 IP：`curl https://api.ipify.org`
-   [ ] 路由器設定端口轉發（80, 443 → 192.168.50.84）
-   [ ] DNS A 記錄指向公網 IP
-   [ ] 驗證 DNS：`nslookup wuchang.life`
-   [ ] Caddy 會自動取得 Let's Encrypt SSL
-   [ ] 測試：`curl -I https://wuchang.life`

### 使用 VPN（Tailscale）

-   [ ] 安裝 Tailscale：`curl -fsSL https://tailscale.com/install.sh | sh`
-   [ ] 啟動：`sudo tailscale up`
-   [ ] 在 Tailscale Admin 啟用子網路
-   [ ] 遠端客戶端安裝 Tailscale
-   [ ] 連接：VPN IP 直接存取

---

## 🔐 安全考量

### 防火牆規則

```powershell
# 允許 HTTP/HTTPS
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow

# 限制 Odoo 直接存取（僅允許 Caddy 反向代理）
New-NetFirewallRule -DisplayName "Block Direct Odoo" -Direction Inbound -LocalPort 8069 -RemoteAddress 0.0.0.0/0 -Action Block
```

### SSL/TLS 驗證

```bash
# 檢查證書
openssl s_client -connect wuchang.life:443

# Caddy 自動管理（不需手動）
# 路徑：caddy-data:/data/caddy/certificates
```

### DDoS 防護

-   ✅ CloudFlare Tunnel 內建 DDoS 保護
-   ✅ Caddy Rate Limiting（可配置）

---

## 📞 故障排除

| 問題         | 原因                           | 解決                                           |
| ------------ | ------------------------------ | ---------------------------------------------- |
| DNS 無法解析 | DNS 記錄未生效                 | 檢查 DNS 傳播：`nslookup -type=A wuchang.life` |
| 連線超時     | 防火牆阻擋或路由器端口轉發失敗 | 驗證防火牆規則、路由器設定                     |
| SSL 證書錯誤 | Caddy 無法自動更新             | 檢查 `caddy-data` 卷權限                       |
| 無外網訪問   | 公網 IP 被 ISP 阻擋            | 聯繫 ISP 或使用 CloudFlare Tunnel              |

---

## ✨ 下一步建議

1. **立即實施**：選擇 CloudFlare Tunnel（最簡單）
2. **監控**：使用 `status.wuchang.life` (Uptime Kuma) 監控可用性
3. **優化**：配置 Caddy 快取和壓縮
4. **擴展**：添加 CDN 加速（CloudFlare 進階功能）

---

**系統狀態**：✅ 準備就緒  
**建議優先級**：🟢 高優先度 - 立即配置外網存取
