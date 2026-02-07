# 網域部署執行指南

## 📋 當前狀態

**檢查時間：** 2026-01-20

### ✅ 已完成項目

- ✅ 所有容器運行正常（6/6）
  - Caddy 反向代理
  - Cloudflare Tunnel
  - Odoo ERP
  - PostgreSQL 資料庫
  - Portainer
  - Uptime Kuma

### ⚠️ 待完成項目

- ⚠️ Cloudflare Tunnel 配置需要完善
  - 需要替換 `<tunnel-id>` 為實際的隧道 ID
  - 需要下載 `credentials.json` 檔案
- ⚠️ Caddy 配置需要創建
  - 需要創建 Caddyfile 配置文件
- ⚠️ DNS 配置尚未完成
  - 需要在 Cloudflare DNS 添加記錄

---

## 🚀 執行步驟

### 步驟 1: 建立 Cloudflare Tunnel

#### 1.1 安裝 cloudflared（如果尚未安裝）

**Windows:**
```powershell
# 方法 1: 使用 Chocolatey
choco install cloudflared

# 方法 2: 手動下載
# 前往 https://github.com/cloudflare/cloudflared/releases
# 下載最新版本的 cloudflared-windows-amd64.exe
# 重命名為 cloudflared.exe 並放到 PATH
```

**或使用 Docker:**
```bash
docker pull cloudflare/cloudflared:latest
```

#### 1.2 登入 Cloudflare

```bash
cloudflared tunnel login
```

這會：
- 開啟瀏覽器進行認證
- 選擇您的網域（例如：wuchang.org.tw）
- 自動下載憑證

#### 1.3 建立隧道

```bash
cloudflared tunnel create wuchang-tunnel
```

**記錄隧道 ID**（顯示為 `Created tunnel wuchang-tunnel with id <tunnel-id>`）

#### 1.4 複製憑證檔案

憑證檔案位置：
```
%USERPROFILE%\.cloudflared\<tunnel-id>.json
```

複製到專案目錄：
```powershell
# 找到憑證檔案
$creds = Get-ChildItem "$env:USERPROFILE\.cloudflared\*.json" | Select-Object -First 1

# 複製到專案目錄
Copy-Item $creds.FullName -Destination ".\cloudflared\credentials.json"
```

#### 1.5 更新 config.yml

編輯 `cloudflared/config.yml`：

```yaml
tunnel: <tunnel-id>  # 替換為步驟 1.3 中獲得的 tunnel-id
credentials-file: /etc/cloudflared/credentials.json

ingress:
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
  
  # Caddy UI (管理介面)
  - hostname: caddy.wuchang.org.tw
    service: http://wuchangv510-caddy-ui-1:80
  
  # 預設規則（必須放在最後）
  - service: http_status:404
```

**注意：** 服務名稱必須是容器的實際名稱，例如 `wuchangv510-wuchang-web-1`。

---

### 步驟 2: 配置 DNS 記錄

#### 2.1 登入 Cloudflare 控制台

1. 前往 https://dash.cloudflare.com/
2. 選擇您的網域（例如：wuchang.org.tw）
3. 點擊左側「DNS」

#### 2.2 添加 DNS 記錄

為每個子域名添加 CNAME 記錄：

| 類型 | 名稱 | 目標 | 代理狀態 |
|------|------|------|----------|
| CNAME | app | `<tunnel-id>.cfargotunnel.com` | 已代理（橙色雲朵） |
| CNAME | ai | `<tunnel-id>.cfargotunnel.com` | 已代理 |
| CNAME | admin | `<tunnel-id>.cfargotunnel.com` | 已代理 |
| CNAME | monitor | `<tunnel-id>.cfargotunnel.com` | 已代理 |
| CNAME | caddy | `<tunnel-id>.cfargotunnel.com` | 已代理 |

**或使用通配符（更簡單）：**

| 類型 | 名稱 | 目標 | 代理狀態 |
|------|------|------|----------|
| CNAME | * | `<tunnel-id>.cfargotunnel.com` | 已代理 |

#### 2.3 驗證 DNS 傳播

等待 1-5 分鐘後，檢查 DNS 解析：

```powershell
# Windows
nslookup app.wuchang.org.tw

# 或使用
Resolve-DnsName app.wuchang.org.tw
```

---

### 步驟 3: 創建 Caddy 配置（可選）

如果您想使用 Caddy 作為反向代理（在 Cloudflare Tunnel 之前），可以創建 Caddyfile：

#### 3.1 生成 Caddyfile 範本

```powershell
python domain_deployment_helper.py
# 選擇 4: 生成 Caddyfile 範本
```

#### 3.2 編輯 Caddyfile

創建 `caddy/Caddyfile`：

```caddy
{
    email your-email@example.com
    log {
        output file /var/log/caddy/access.log
        format json
    }
}

# Odoo ERP 系統
app.wuchang.org.tw {
    reverse_proxy wuchangv510-wuchang-web-1:8069 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
    
    header {
        X-Frame-Options "SAMEORIGIN"
    }
}

# Open WebUI (AI 介面)
ai.wuchang.org.tw {
    reverse_proxy wuchangv510-open-webui-1:8080 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
    
    @websocket {
        header Connection *Upgrade*
        header Upgrade websocket
    }
    reverse_proxy @websocket wuchangv510-open-webui-1:8080
}

# Portainer (容器管理)
admin.wuchang.org.tw {
    reverse_proxy wuchangv510-portainer-1:9000 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
}

# Uptime Kuma (監控)
monitor.wuchang.org.tw {
    reverse_proxy wuchangv510-uptime-kuma-1:3001 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
}

# 預設處理
:80, :443 {
    respond "404 Not Found" 404
}
```

#### 3.3 更新 Docker Compose

如果使用 Caddy，確保 docker-compose.yml 中掛載了 Caddyfile：

```yaml
services:
  caddy:
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      - ./caddy/data:/data
      - ./caddy/config:/config
```

---

### 步驟 4: 重啟服務

#### 4.1 重啟 Cloudflare Tunnel

```powershell
docker-compose restart cloudflared
```

#### 4.2 檢查服務狀態

```powershell
# 檢查容器日誌
docker logs wuchangv510-cloudflared-1

# 檢查容器狀態
docker ps | findstr cloudflared
```

---

### 步驟 5: 驗證部署

#### 5.1 測試 DNS 解析

```powershell
Resolve-DnsName app.wuchang.org.tw
```

應該解析到 Cloudflare 的 IP（例如：104.x.x.x）。

#### 5.2 測試 HTTPS 連接

```powershell
# 使用 curl 測試
curl -I https://app.wuchang.org.tw

# 或使用瀏覽器訪問
# https://app.wuchang.org.tw
```

#### 5.3 測試服務訪問

訪問以下 URL 驗證服務：

- ✅ Odoo ERP: https://app.wuchang.org.tw
- ✅ Open WebUI: https://ai.wuchang.org.tw
- ✅ Portainer: https://admin.wuchang.org.tw
- ✅ Uptime Kuma: https://monitor.wuchang.org.tw

#### 5.4 檢查 SSL 證書

```powershell
# 檢查證書資訊
$cert = [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
$request = [System.Net.HttpWebRequest]::Create("https://app.wuchang.org.tw")
$request.GetResponse()
```

---

## 📝 配置檢查清單

### Cloudflare Tunnel
- [ ] 已安裝 cloudflared
- [ ] 已登入 Cloudflare
- [ ] 已建立隧道
- [ ] 已複製 credentials.json
- [ ] 已更新 config.yml（包含 tunnel-id）
- [ ] 已配置 ingress 規則

### DNS 配置
- [ ] 已在 Cloudflare DNS 添加 CNAME 記錄
- [ ] DNS 記錄指向正確的 Tunnel
- [ ] 代理狀態設為「已代理」（橙色雲朵）
- [ ] DNS 已成功解析

### 容器配置
- [ ] Cloudflare Tunnel 容器運行正常
- [ ] 服務容器運行正常
- [ ] 容器網路連接正常

### 驗證
- [ ] DNS 解析正常
- [ ] HTTPS 連接正常
- [ ] SSL 證書有效
- [ ] 所有服務可以訪問

---

## 🔧 故障排除

### 問題 1: Cloudflare Tunnel 無法連接

**檢查：**
```powershell
# 查看容器日誌
docker logs wuchangv510-cloudflared-1

# 檢查配置檔案
Get-Content .\cloudflared\config.yml

# 檢查憑證檔案
Test-Path .\cloudflared\credentials.json
```

**解決方法：**
1. 確認 credentials.json 存在且格式正確
2. 確認 config.yml 中的 tunnel-id 正確
3. 確認 ingress 規則中的服務名稱正確

### 問題 2: DNS 無法解析

**檢查：**
```powershell
# 檢查 DNS 記錄
Resolve-DnsName app.wuchang.org.tw

# 清除 DNS 快取
ipconfig /flushdns
```

**解決方法：**
1. 確認 Cloudflare DNS 記錄已添加
2. 等待 DNS 傳播（通常 1-5 分鐘）
3. 確認 CNAME 目標正確

### 問題 3: 502 Bad Gateway

**檢查：**
```powershell
# 檢查服務容器狀態
docker ps | findstr wuchang-web

# 檢查容器日誌
docker logs wuchangv510-wuchang-web-1
```

**解決方法：**
1. 確認後端服務運行正常
2. 確認 config.yml 中的服務名稱正確
3. 確認容器網路連接正常

### 問題 4: SSL 證書錯誤

Cloudflare Tunnel 自動提供 SSL 證書，如果出現錯誤：

1. 確認 DNS 記錄已設為「已代理」（橙色雲朵）
2. 在 Cloudflare 控制台確認 SSL/TLS 設定為「完整（嚴格）」
3. 清除瀏覽器快取

---

## 📚 相關文件

- `DOMAIN_DEPLOYMENT_PLAN.md` - 完整域名部署規劃
- `EXTERNAL_ACCESS_SETUP.md` - 外網訪問配置指南
- `CLOUD_DEPLOYMENT_GUIDE.md` - 雲端部署指南
- `domain_deployment_helper.py` - 部署輔助工具

---

## ✅ 總結

完成以上步驟後，您的服務就可以通過以下域名訪問：

- **Odoo ERP:** https://app.wuchang.org.tw
- **Open WebUI:** https://ai.wuchang.org.tw
- **Portainer:** https://admin.wuchang.org.tw
- **Uptime Kuma:** https://monitor.wuchang.org.tw

所有服務都會：
- ✅ 自動使用 HTTPS
- ✅ 自動獲得 SSL 證書
- ✅ 通過 Cloudflare CDN 加速
- ✅ 受到 DDoS 防護

---

**最後更新：** 2026-01-20
