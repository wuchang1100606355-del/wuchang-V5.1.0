# Cloudflare Tunnel 手動配置指南

## 📋 前置需求

1. Cloudflare 帳戶（已登入）
2. 網域 `wuchang.life` 已在 Cloudflare 管理
3. 本機已安裝 `cloudflared` 或使用 Docker 容器

---

## 🔧 步驟 1：登入 Cloudflare 並獲取憑證

### 方法 A：使用本機 cloudflared（如果已安裝）

```bash
# 1. 登入 Cloudflare（會開啟瀏覽器）
cloudflared tunnel login

# 2. 在瀏覽器中完成授權
# 3. 憑證會自動儲存到：C:\Users\<使用者名稱>\.cloudflared\cert.pem
```

### 方法 B：使用 Docker 容器

```bash
# 1. 進入 cloudflared 容器
docker exec -it wuchangv510-cloudflared-1 sh

# 2. 在容器內執行登入
cloudflared tunnel login

# 3. 憑證會儲存在容器內，需要複製出來
```

### 方法 C：手動下載憑證（推薦）

1. 訪問：https://one.dash.cloudflare.com/
2. 選擇網域：`wuchang.life`
3. 進入 **Zero Trust** → **Networks** → **Tunnels**
4. 點擊 **Create a tunnel**
5. 選擇 **Cloudflared** 作為連接器
6. 命名隧道（例如：`wuchang-life-tunnel`）
7. 下載憑證檔案（`<tunnel-id>.json`）

---

## 🔧 步驟 2：建立或選擇 Tunnel

### 建立新 Tunnel

```bash
# 建立新隧道
cloudflared tunnel create wuchang-life

# 輸出會顯示 Tunnel ID，例如：
# Created tunnel wuchang-life with id abc123def456...
```

### 或使用現有 Tunnel

```bash
# 列出所有隧道
cloudflared tunnel list

# 記下要使用的 Tunnel ID
```

---

## 🔧 步驟 3：配置憑證檔案

### 建立 credentials.json

在 `cloudflared/` 目錄下建立 `credentials.json`：

```json
{
  "AccountTag": "your-account-tag",
  "TunnelSecret": "your-tunnel-secret-base64",
  "TunnelID": "your-tunnel-id",
  "TunnelName": "wuchang-life"
}
```

**取得這些值的方法：**

1. **AccountTag**：
   - 訪問 https://one.dash.cloudflare.com/
   - 在右側面板找到 **Account ID**

2. **TunnelID**：
   - 從步驟 2 的輸出取得
   - 或從 Cloudflare Dashboard → Zero Trust → Networks → Tunnels 查看

3. **TunnelSecret**：
   - 從下載的憑證檔案中取得
   - 或從 `C:\Users\<使用者名稱>\.cloudflared\cert.pem` 中提取

---

## 🔧 步驟 4：更新 config.yml

編輯 `cloudflared/config.yml`：

```yaml
tunnel: <your-tunnel-id>  # 替換為實際的 Tunnel ID
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # 首頁（主域名）
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  
  # 根域名
  - hostname: wuchang.life
    service: http://wuchangv510-caddy-1:80
  
  # Odoo ERP 系統
  - hostname: app.wuchang.org.tw
    service: http://wuchangv510-wuchang-web-1:8069
  
  # Open WebUI (AI 介面)
  - hostname: ai.wuchang.org.tw
    service: http://wuchangv510-open-webui-1:8080
  
  # Portainer (容器管理)
  - hostname: admin.wuchang.org.tw
    service: http://wuchangv510-portainer-1:9000
  
  # Uptime Kuma (監控)
  - hostname: monitor.wuchang.org.tw
    service: http://wuchangv510-uptime-kuma-1:3001
  
  # 預設規則（必須放在最後）
  - service: http_status:404
```

**重要：**
- 將 `<your-tunnel-id>` 替換為實際的 Tunnel ID
- 確保 `credentials-file` 路徑正確（Docker 容器內路徑為 `/etc/cloudflared/credentials.json`）

---

## 🔧 步驟 5：配置 DNS 路由

### 方法 A：使用命令列

```bash
# 為 www.wuchang.life 配置路由
cloudflared tunnel route dns wuchang-life www.wuchang.life

# 為 wuchang.life 配置路由
cloudflared tunnel route dns wuchang-life wuchang.life
```

### 方法 B：在 Cloudflare Dashboard 手動配置

1. 訪問：https://one.dash.cloudflare.com/
2. 選擇網域：`wuchang.life`
3. 進入 **DNS** → **Records**
4. 為每個 hostname 建立 CNAME 記錄：
   - **Name**: `www` → **Target**: `<tunnel-id>.cfargotunnel.com`
   - **Name**: `@` (根域名) → **Target**: `<tunnel-id>.cfargotunnel.com`
   - **Proxy status**: 開啟（橙色雲朵）

---

## 🔧 步驟 6：複製憑證到容器

如果使用 Docker 容器，需要將憑證檔案複製到容器內：

```bash
# 方法 1：使用 docker cp
docker cp cloudflared/credentials.json wuchangv510-cloudflared-1:/etc/cloudflared/credentials.json
docker cp cloudflared/config.yml wuchangv510-cloudflared-1:/etc/cloudflared/config.yml

# 方法 2：在 docker-compose.yml 中掛載卷
# volumes:
#   - ./cloudflared:/etc/cloudflared
```

---

## 🔧 步驟 7：重啟 Cloudflare Tunnel 容器

```bash
# 重啟容器
docker restart wuchangv510-cloudflared-1

# 檢查日誌
docker logs -f wuchangv510-cloudflared-1
```

**成功標誌：**
- 日誌顯示 `Connection established`
- 沒有錯誤訊息
- 狀態顯示為 `Connected`

---

## ✅ 驗證配置

### 1. 檢查容器狀態

```bash
docker ps | grep cloudflared
```

### 2. 檢查日誌

```bash
docker logs wuchangv510-cloudflared-1
```

### 3. 測試訪問

```bash
# 從外部測試
curl -I https://www.wuchang.life
curl -I https://wuchang.life
```

### 4. 檢查 DNS 解析

```bash
# 檢查 DNS 記錄
nslookup www.wuchang.life
nslookup wuchang.life
```

---

## 📝 配置檔案範例

### credentials.json 範例

```json
{
  "AccountTag": "abc123def456789",
  "TunnelSecret": "base64-encoded-secret-here",
  "TunnelID": "abc123def456789",
  "TunnelName": "wuchang-life"
}
```

### config.yml 完整範例

```yaml
tunnel: abc123def456789
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  - hostname: wuchang.life
    service: http://wuchangv510-caddy-1:80
  - hostname: app.wuchang.org.tw
    service: http://wuchangv510-wuchang-web-1:8069
  - hostname: ai.wuchang.org.tw
    service: http://wuchangv510-open-webui-1:8080
  - hostname: admin.wuchang.org.tw
    service: http://wuchangv510-portainer-1:9000
  - hostname: monitor.wuchang.org.tw
    service: http://wuchangv510-uptime-kuma-1:3001
  - service: http_status:404
```

---

## ⚠️ 常見問題

### 問題 1：憑證檔案找不到

**解決方案：**
- 確認 `credentials.json` 在正確位置
- 檢查檔案權限
- 確認 Docker 容器內的掛載路徑

### 問題 2：Tunnel ID 錯誤

**解決方案：**
- 使用 `cloudflared tunnel list` 確認正確的 Tunnel ID
- 檢查 `config.yml` 中的 `tunnel:` 欄位

### 問題 3：DNS 路由未生效

**解決方案：**
- 等待 DNS 傳播（通常 5-10 分鐘）
- 檢查 Cloudflare Dashboard 中的 DNS 記錄
- 確認 CNAME 記錄指向正確的 `<tunnel-id>.cfargotunnel.com`

### 問題 4：容器無法連接

**解決方案：**
- 檢查容器日誌：`docker logs wuchangv510-cloudflared-1`
- 確認網路連接正常
- 檢查防火牆設定

---

## 📚 參考資源

- Cloudflare Tunnel 文檔：https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- Cloudflare Dashboard：https://one.dash.cloudflare.com/
- 網域管理：https://dash.cloudflare.com/

---

**最後更新**：2026-01-22
