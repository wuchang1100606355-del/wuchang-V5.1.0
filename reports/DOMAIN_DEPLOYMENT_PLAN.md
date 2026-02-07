# 網域部署規劃

## 📋 目錄

1. [概述](#概述)
2. [當前架構分析](#當前架構分析)
3. [域名規劃](#域名規劃)
4. [DNS 配置](#dns-配置)
5. [反向代理配置（Caddy）](#反向代理配置caddy)
6. [Cloudflare Tunnel 配置](#cloudflare-tunnel-配置)
7. [SSL/TLS 證書管理](#ssltls-證書管理)
8. [服務路由規劃](#服務路由規劃)
9. [部署步驟](#部署步驟)
10. [監控與維護](#監控與維護)
11. [安全考量](#安全考量)
12. [故障排除](#故障排除)

---

## 概述

本文檔提供完整的網域部署規劃，包括：
- 域名分配策略
- DNS 配置方案
- 反向代理設定
- SSL/TLS 證書管理
- 服務路由規劃
- 部署與維護流程

### 當前服務清單

| 服務名稱 | 容器名稱 | 內部端口 | 外部端口 | 用途 |
|---------|---------|---------|---------|------|
| Caddy | wuchangv510-caddy-1 | 80, 443 | 80, 443 | 反向代理/Web 伺服器 |
| Caddy UI | wuchangv510-caddy-ui-1 | 80, 443 | 8081, 8444 | Caddy 管理介面 |
| Cloudflare Tunnel | wuchangv510-cloudflared-1 | - | - | 外部訪問隧道 |
| Cloudflare Tunnel (Named) | wuchangv510-cloudflared-named-1 | - | - | 命名隧道 |
| PostgreSQL | wuchangv510-db-1 | 5432 | - | 資料庫 |
| Ollama | wuchangv510-ollama-1 | 11434 | 11434 | AI 模型服務 |
| Open WebUI | wuchangv510-open-webui-1 | 8080 | 8080 | AI 介面 |
| Portainer | wuchangv510-portainer-1 | 9000 | 9000 | 容器管理 |
| Uptime Kuma | wuchangv510-uptime-kuma-1 | 3001 | 3001 | 監控工具 |
| Odoo | wuchangv510-wuchang-web-1 | 8069 | 8069 | ERP 系統 |

---

## 當前架構分析

### 網路架構

```
Internet
    ↓
Cloudflare Tunnel (cloudflared)
    ↓
Caddy (反向代理) - 端口 80, 443
    ↓
┌─────────────────────────────────────┐
│  內部服務容器                         │
│  - Odoo (8069)                      │
│  - Open WebUI (8080)                │
│  - Ollama (11434)                   │
│  - Portainer (9000)                 │
│  - Uptime Kuma (3001)               │
│  - PostgreSQL (5432)                │
└─────────────────────────────────────┘
```

### 當前配置狀態

- ✅ Caddy 已配置為反向代理
- ✅ Cloudflare Tunnel 已設置
- ⚠️ 需要配置域名路由
- ⚠️ 需要配置 SSL 證書自動更新
- ⚠️ 需要規劃服務域名分配

---

## 域名規劃

### 主域名建議

根據服務性質，建議使用以下域名結構：

#### 方案一：子域名結構（推薦）

```
主域名: wuchang.org.tw (或您現有的域名)

服務域名分配：
├── www.wuchang.org.tw          → 主網站/首頁
├── app.wuchang.org.tw           → Odoo ERP 系統
├── ai.wuchang.org.tw            → Open WebUI (AI 介面)
├── api.wuchang.org.tw           → API 服務（未來擴展）
├── admin.wuchang.org.tw         → Portainer (容器管理)
├── monitor.wuchang.org.tw       → Uptime Kuma (監控)
├── caddy.wuchang.org.tw         → Caddy UI (管理介面)
└── tunnel.wuchang.org.tw        → Cloudflare Tunnel 狀態
```

#### 方案二：路徑結構

```
主域名: wuchang.org.tw

服務路徑分配：
├── wuchang.org.tw/              → 主網站
├── wuchang.org.tw/app           → Odoo ERP
├── wuchang.org.tw/ai            → Open WebUI
├── wuchang.org.tw/admin         → Portainer
├── wuchang.org.tw/monitor       → Uptime Kuma
└── wuchang.org.tw/caddy         → Caddy UI
```

**建議使用方案一（子域名結構）**，因為：
- 更清晰的服務分離
- 更好的安全隔離
- 更容易的 SSL 證書管理
- 更靈活的擴展性

### 域名註冊與 DNS 提供商

1. **域名註冊商選擇**
   - 台灣：PChome、Gandi、Namecheap
   - 國際：Cloudflare Registrar、Namecheap、Google Domains

2. **DNS 提供商建議**
   - **Cloudflare**（推薦）：免費、快速、安全
   - **Google Cloud DNS**：穩定、可靠
   - **AWS Route 53**：功能強大、付費

---

## DNS 配置

### Cloudflare DNS 配置

#### 1. 基本 DNS 記錄

```
類型    名稱              內容                    TTL    代理狀態
A       @                 <您的伺服器 IP>          Auto   [僅 DNS]
A       www               <您的伺服器 IP>          Auto   [僅 DNS]
CNAME   app               <Cloudflare Tunnel>      Auto   [已代理]
CNAME   ai                <Cloudflare Tunnel>      Auto   [已代理]
CNAME   api               <Cloudflare Tunnel>      Auto   [已代理]
CNAME   admin             <Cloudflare Tunnel>      Auto   [已代理]
CNAME   monitor           <Cloudflare Tunnel>      Auto   [已代理]
CNAME   caddy             <Cloudflare Tunnel>      Auto   [已代理]
```

#### 2. Cloudflare Tunnel 配置

如果使用 Cloudflare Tunnel，所有子域名應指向 Tunnel：

```
類型    名稱              內容                    TTL    代理狀態
CNAME   *                 <Tunnel UUID>.cfargotunnel.com  Auto   [已代理]
```

#### 3. 本地網路 DNS（可選）

如果需要在本地網路直接訪問：

```
類型    名稱              內容                    TTL
A       app.local          <本地 IP (10.8.0.x)>    300
A       ai.local           <本地 IP>               300
A       admin.local        <本地 IP>               300
```

### DNS 配置步驟

1. **登入 Cloudflare 控制台**
2. **選擇您的域名**
3. **進入 DNS 設定**
4. **添加記錄**：
   - 類型：CNAME
   - 名稱：app（或其他子域名）
   - 目標：`<tunnel-id>.cfargotunnel.com`
   - 代理狀態：已代理（橙色雲朵）
5. **等待 DNS 傳播**（通常 1-5 分鐘）

---

## 反向代理配置（Caddy）

### Caddyfile 配置

創建或更新 `Caddyfile`：

```caddy
# 全域設定
{
    # 自動 HTTPS
    email your-email@example.com
    # 日誌設定
    log {
        output file /var/log/caddy/access.log
        format json
    }
}

# 主網站
www.wuchang.org.tw, wuchang.org.tw {
    reverse_proxy localhost:8080 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
    
    # 安全標頭
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        Referrer-Policy "strict-origin-when-cross-origin"
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
    
    # Odoo 特定設定
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
    
    # WebSocket 支援
    @websocket {
        header Connection *Upgrade*
        header Upgrade websocket
    }
    reverse_proxy @websocket wuchangv510-open-webui-1:8080
}

# Portainer (容器管理)
admin.wuchang.org.tw {
    # 基本認證（建議）
    basicauth {
        admin $2a$14$加密的密碼雜湊
    }
    
    reverse_proxy wuchangv510-portainer-1:9000 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
}

# Uptime Kuma (監控)
monitor.wuchang.org.tw {
    # 基本認證（強烈建議）
    basicauth {
        monitor $2a$14$加密的密碼雜湊
    }
    
    reverse_proxy wuchangv510-uptime-kuma-1:3001 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
}

# Caddy UI (管理介面)
caddy.wuchang.org.tw {
    # 基本認證（必須）
    basicauth {
        caddy $2a$14$加密的密碼雜湊
    }
    
    reverse_proxy wuchangv510-caddy-ui-1:80 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
}

# API 服務（未來擴展）
api.wuchang.org.tw {
    reverse_proxy localhost:8080 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
    
    # API 特定設定
    header {
        Access-Control-Allow-Origin "*"
        Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
    }
}

# 預設處理（未匹配的域名）
:80, :443 {
    respond "404 Not Found" 404
}
```

### 生成基本認證密碼

使用 Caddy 工具生成密碼雜湊：

```bash
docker exec wuchangv510-caddy-1 caddy hash-password --plaintext your-password
```

或使用線上工具：
- https://caddyserver.com/docs/command-line#caddy-hash-password

### Caddy 配置檔案位置

建議將 Caddyfile 放在：
- `/etc/caddy/Caddyfile`（Linux）
- `C:\caddy\Caddyfile`（Windows）
- 或掛載到容器：`./caddy/Caddyfile:/etc/caddy/Caddyfile`

---

## Cloudflare Tunnel 配置

### 1. 創建 Tunnel

```bash
# 在 Cloudflare Zero Trust 控制台創建 Tunnel
# 或使用命令行
cloudflared tunnel create wuchang-tunnel
```

### 2. 配置檔案 (config.yml)

```yaml
tunnel: <tunnel-id>
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # Odoo
  - hostname: app.wuchang.org.tw
    service: http://localhost:8069
  
  # Open WebUI
  - hostname: ai.wuchang.org.tw
    service: http://localhost:8080
  
  # Portainer
  - hostname: admin.wuchang.org.tw
    service: http://localhost:9000
  
  # Uptime Kuma
  - hostname: monitor.wuchang.org.tw
    service: http://localhost:3001
  
  # Caddy UI
  - hostname: caddy.wuchang.org.tw
    service: http://localhost:8081
  
  # 預設規則
  - service: http_status:404
```

### 3. 運行 Tunnel

```bash
cloudflared tunnel run wuchang-tunnel
```

### 4. Docker Compose 配置

更新 `docker-compose.yml`：

```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: wuchangv510-cloudflared-1
    command: tunnel run
    volumes:
      - ./cloudflared/config.yml:/etc/cloudflared/config.yml:ro
      - ./cloudflared/credentials.json:/etc/cloudflared/credentials.json:ro
    restart: unless-stopped
```

---

## SSL/TLS 證書管理

### Caddy 自動 HTTPS

Caddy 會自動：
1. 從 Let's Encrypt 獲取證書
2. 自動續期
3. 支援 HTTP/2 和 HTTP/3

### Cloudflare SSL/TLS 設定

在 Cloudflare 控制台：
1. **SSL/TLS 模式**：設為「完整（嚴格）」
2. **自動 HTTPS 重寫**：啟用
3. **始終使用 HTTPS**：啟用
4. **最小 TLS 版本**：TLS 1.2

### 證書驗證

```bash
# 檢查證書
openssl s_client -connect app.wuchang.org.tw:443 -servername app.wuchang.org.tw

# 檢查證書到期時間
echo | openssl s_client -connect app.wuchang.org.tw:443 2>/dev/null | openssl x509 -noout -dates
```

---

## 服務路由規劃

### 路由表

| 域名 | 服務 | 容器 | 端口 | 認證 | 備註 |
|------|------|------|------|------|------|
| www.wuchang.org.tw | 主網站 | - | 8080 | 否 | 未來擴展 |
| app.wuchang.org.tw | Odoo ERP | wuchangv510-wuchang-web-1 | 8069 | Odoo 內建 | 主要業務系統 |
| ai.wuchang.org.tw | Open WebUI | wuchangv510-open-webui-1 | 8080 | WebUI 內建 | AI 服務介面 |
| admin.wuchang.org.tw | Portainer | wuchangv510-portainer-1 | 9000 | Caddy + Portainer | 容器管理 |
| monitor.wuchang.org.tw | Uptime Kuma | wuchangv510-uptime-kuma-1 | 3001 | Caddy + Kuma | 監控服務 |
| caddy.wuchang.org.tw | Caddy UI | wuchangv510-caddy-ui-1 | 8081 | Caddy | 反向代理管理 |
| api.wuchang.org.tw | API 服務 | - | 8080 | API Key | 未來擴展 |

### 內部服務（不公開）

| 服務 | 容器 | 端口 | 訪問方式 |
|------|------|------|----------|
| PostgreSQL | wuchangv510-db-1 | 5432 | 僅內部網路 |
| Ollama | wuchangv510-ollama-1 | 11434 | 僅內部網路或 VPN |

---

## 部署步驟

### 階段一：準備工作

1. **註冊域名**
   ```bash
   # 選擇域名註冊商並註冊 wuchang.org.tw
   ```

2. **設置 Cloudflare**
   - 將域名添加到 Cloudflare
   - 更新名稱伺服器（Nameservers）
   - 等待 DNS 傳播（通常 24-48 小時）

3. **準備配置檔案**
   ```bash
   # 創建配置目錄
   mkdir -p ./caddy
   mkdir -p ./cloudflared
   ```

### 階段二：DNS 配置

1. **在 Cloudflare 添加 DNS 記錄**
   - 登入 Cloudflare 控制台
   - 選擇域名
   - 進入 DNS 設定
   - 添加 CNAME 記錄指向 Tunnel

2. **驗證 DNS 傳播**
   ```bash
   # 檢查 DNS 記錄
   nslookup app.wuchang.org.tw
   dig app.wuchang.org.tw
   ```

### 階段三：配置 Caddy

1. **創建 Caddyfile**
   ```bash
   # 複製上述 Caddyfile 配置
   nano ./caddy/Caddyfile
   ```

2. **生成基本認證密碼**
   ```bash
   docker exec wuchangv510-caddy-1 caddy hash-password --plaintext your-password
   ```

3. **更新 docker-compose.yml**
   ```yaml
   services:
     caddy:
       volumes:
         - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
         - ./caddy/data:/data
         - ./caddy/config:/config
   ```

4. **重啟 Caddy**
   ```bash
   docker-compose restart caddy
   ```

### 階段四：配置 Cloudflare Tunnel

1. **創建 Tunnel**
   - 在 Cloudflare Zero Trust 控制台創建
   - 下載 credentials.json

2. **創建 config.yml**
   ```bash
   # 複製上述 config.yml 配置
   nano ./cloudflared/config.yml
   ```

3. **更新 docker-compose.yml**
   ```yaml
   services:
     cloudflared:
       volumes:
         - ./cloudflared/config.yml:/etc/cloudflared/config.yml:ro
         - ./cloudflared/credentials.json:/etc/cloudflared/credentials.json:ro
   ```

4. **重啟 Cloudflare Tunnel**
   ```bash
   docker-compose restart cloudflared
   ```

### 階段五：驗證與測試

1. **測試 DNS 解析**
   ```bash
   nslookup app.wuchang.org.tw
   ```

2. **測試 HTTPS 連接**
   ```bash
   curl -I https://app.wuchang.org.tw
   ```

3. **測試服務訪問**
   - 訪問 https://app.wuchang.org.tw（Odoo）
   - 訪問 https://ai.wuchang.org.tw（Open WebUI）
   - 訪問 https://admin.wuchang.org.tw（Portainer）

4. **檢查 SSL 證書**
   ```bash
   openssl s_client -connect app.wuchang.org.tw:443 -servername app.wuchang.org.tw
   ```

### 階段六：監控設置

1. **在 Uptime Kuma 添加監控**
   - 登入 monitor.wuchang.org.tw
   - 添加監控項目：
     - app.wuchang.org.tw
     - ai.wuchang.org.tw
     - admin.wuchang.org.tw

2. **設置告警**
   - 配置郵件通知
   - 配置 Telegram/Discord 通知

---

## 監控與維護

### 日常監控

1. **服務狀態監控**
   - Uptime Kuma：https://monitor.wuchang.org.tw
   - Portainer：https://admin.wuchang.org.tw

2. **日誌監控**
   ```bash
   # Caddy 日誌
   docker logs -f wuchangv510-caddy-1
   
   # Cloudflare Tunnel 日誌
   docker logs -f wuchangv510-cloudflared-1
   ```

3. **資源監控**
   ```bash
   # 容器資源使用
   docker stats
   ```

### 定期維護

1. **每週**
   - 檢查服務狀態
   - 檢查日誌錯誤
   - 備份配置檔案

2. **每月**
   - 更新容器映像
   - 檢查 SSL 證書到期時間
   - 檢查 DNS 記錄
   - 審查安全設定

3. **每季**
   - 安全審計
   - 效能優化
   - 備份驗證

### 備份策略

```bash
# 備份配置檔案
tar -czf backup-$(date +%Y%m%d).tar.gz \
  ./caddy \
  ./cloudflared \
  docker-compose.yml

# 備份資料庫
docker exec wuchangv510-db-1 pg_dump -U postgres > backup-db-$(date +%Y%m%d).sql
```

---

## 安全考量

### 1. 基本認證

所有管理介面應啟用基本認證：
- Portainer
- Uptime Kuma
- Caddy UI

### 2. 防火牆規則

```bash
# 僅允許必要端口
# 80, 443 (HTTP/HTTPS)
# 其他端口僅允許內部網路訪問
```

### 3. 安全標頭

在 Caddyfile 中設置安全標頭：
- HSTS
- X-Frame-Options
- X-Content-Type-Options
- CSP (Content Security Policy)

### 4. 訪問控制

- 使用 Cloudflare Access 控制訪問
- 設置 IP 白名單（如需要）
- 啟用 2FA（雙因素認證）

### 5. 定期更新

```bash
# 更新容器映像
docker-compose pull
docker-compose up -d

# 更新系統
apt update && apt upgrade
```

---

## 故障排除

### 常見問題

#### 1. DNS 無法解析

**症狀**：無法訪問域名

**解決方法**：
```bash
# 檢查 DNS 記錄
nslookup app.wuchang.org.tw

# 檢查 Cloudflare DNS 設定
# 確認 CNAME 記錄正確

# 清除 DNS 快取
ipconfig /flushdns  # Windows
sudo systemd-resolve --flush-caches  # Linux
```

#### 2. SSL 證書問題

**症狀**：瀏覽器顯示證書錯誤

**解決方法**：
```bash
# 檢查 Caddy 日誌
docker logs wuchangv510-caddy-1

# 手動重新獲取證書
docker exec wuchangv510-caddy-1 caddy reload --config /etc/caddy/Caddyfile

# 檢查證書到期時間
echo | openssl s_client -connect app.wuchang.org.tw:443 2>/dev/null | openssl x509 -noout -dates
```

#### 3. Cloudflare Tunnel 無法連接

**症狀**：外部無法訪問服務

**解決方法**：
```bash
# 檢查 Tunnel 狀態
docker logs wuchangv510-cloudflared-1

# 驗證 credentials.json
cat ./cloudflared/credentials.json

# 驗證 config.yml
cat ./cloudflared/config.yml

# 重啟 Tunnel
docker-compose restart cloudflared
```

#### 4. 服務無法訪問

**症狀**：域名可解析但服務無響應

**解決方法**：
```bash
# 檢查容器狀態
docker ps

# 檢查服務日誌
docker logs wuchangv510-wuchang-web-1

# 檢查 Caddy 配置
docker exec wuchangv510-caddy-1 caddy validate --config /etc/caddy/Caddyfile

# 測試內部連接
curl http://localhost:8069
```

#### 5. 502 Bad Gateway

**症狀**：Caddy 返回 502 錯誤

**解決方法**：
```bash
# 檢查後端服務是否運行
docker ps | grep wuchang-web

# 檢查容器網路
docker network inspect wuchangv510_default

# 檢查 Caddy 日誌
docker logs wuchangv510-caddy-1 | tail -50
```

### 日誌位置

```bash
# Caddy 日誌
docker logs wuchangv510-caddy-1
/var/log/caddy/access.log

# Cloudflare Tunnel 日誌
docker logs wuchangv510-cloudflared-1

# 服務日誌
docker logs <container-name>
```

### 緊急恢復

如果服務完全無法訪問：

1. **檢查容器狀態**
   ```bash
   docker ps -a
   ```

2. **重啟所有服務**
   ```bash
   docker-compose restart
   ```

3. **檢查網路連接**
   ```bash
   ping 8.8.8.8
   ```

4. **檢查防火牆**
   ```bash
   # Windows
   netsh advfirewall show allprofiles
   
   # Linux
   sudo ufw status
   ```

---

## 附錄

### A. 快速參考命令

```bash
# 查看所有容器
docker ps -a

# 查看 Caddy 配置
docker exec wuchangv510-caddy-1 caddy list-modules

# 重新載入 Caddy 配置
docker exec wuchangv510-caddy-1 caddy reload

# 檢查 DNS
nslookup app.wuchang.org.tw

# 測試 HTTPS
curl -I https://app.wuchang.org.tw

# 查看日誌
docker logs -f wuchangv510-caddy-1
```

### B. 配置檔案範本

所有配置檔案範本請參考上述各章節。

### C. 相關資源

- [Caddy 官方文件](https://caddyserver.com/docs/)
- [Cloudflare Tunnel 文件](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Docker Compose 文件](https://docs.docker.com/compose/)

---

## 更新記錄

| 日期 | 版本 | 更新內容 | 作者 |
|------|------|---------|------|
| 2026-01-19 | 1.0 | 初始版本 | System |

---

**注意**：本文檔應根據實際部署情況進行調整。建議在生產環境部署前，先在測試環境驗證所有配置。

