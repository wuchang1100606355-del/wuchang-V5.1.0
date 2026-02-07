# 🌐 五常 AI - 外網連入完整設定指南

## 📋 目錄

1. [概述](#概述)
2. [域名與 DNS 設定](#域名與-dns-設定)
3. [SSL 憑證配置](#ssl-憑證配置)
4. [防火牆規則](#防火牆規則)
5. [反向代理設定](#反向代理設定)
6. [路由器配置](#路由器配置)
7. [Cloudflare 設定](#cloudflare-設定)
8. [測試與驗證](#測試與驗證)

---

## 🎯 概述

### 外網連入需求清單

| 服務         | 內網端口 | 外網端口 | 用途     |
| ------------ | -------- | -------- | -------- |
| HTTPS (Odoo) | 8069     | 443      | ERP 系統 |
| 同步服務     | 8766     | 8766     | 檔案同步 |
| UI 控制      | 8765     | -        | 本機專用 |
| SSH (選配)   | 22       | 22222    | 遠端管理 |

### 架構圖

```
Internet
    │
    ▼
wuchang.life (域名)
    │
    ├─► Cloudflare (CDN + WAF + DDoS 防護)
    │       │
    │       ▼
    │   SSL 終止 (443)
    │       │
    │       ▼
    └─► 路由器 Public IP
            │
            ├─► Port Forward: 443 → 192.168.50.249:443
            ├─► Port Forward: 8766 → 192.168.50.249:8766
            │
            ▼
        Server (192.168.50.249)
            │
            ├─► Nginx 反向代理
            │       ├─► /odoo → localhost:8069
            │       ├─► /sync → localhost:8766
            │       └─► /api → localhost:8080
            │
            ├─► Odoo (8069)
            └─► Sync Service (8766)
```

---

## 🌍 域名與 DNS 設定

### 1. 取得公網 IP

```powershell
# 查詢你的公網 IP
$publicIP = (Invoke-WebRequest -Uri "https://api.ipify.org").Content
Write-Host "你的公網 IP: $publicIP"
```

### 2. DNS 記錄配置

登入你的域名管理（假設使用 Cloudflare）：

#### A 記錄

```
類型: A
名稱: @
內容: [你的公網IP]
TTL: Auto
代理狀態: 已代理（橘色雲）
```

#### CNAME 記錄（子域名）

```
# 同步服務
類型: CNAME
名稱: sync
內容: wuchang.life
TTL: Auto
代理狀態: 已代理

# API 服務
類型: CNAME
名稱: api
內容: wuchang.life
TTL: Auto
代理狀態: 已代理
```

#### 完整 DNS 配置

```dns
# 主域名
wuchang.life.               A       [你的公網IP]

# 子域名
sync.wuchang.life.          CNAME   wuchang.life.
api.wuchang.life.           CNAME   wuchang.life.
www.wuchang.life.           CNAME   wuchang.life.

# 郵件記錄（Google Workspace）
wuchang.life.               MX 1    aspmx.l.google.com.
wuchang.life.               MX 5    alt1.aspmx.l.google.com.
wuchang.life.               MX 5    alt2.aspmx.l.google.com.
wuchang.life.               MX 10   alt3.aspmx.l.google.com.
wuchang.life.               MX 10   alt4.aspmx.l.google.com.

# SPF 記錄
wuchang.life.               TXT     "v=spf1 include:_spf.google.com ~all"

# DKIM（從 Google Workspace 取得）
google._domainkey.wuchang.life. TXT "v=DKIM1; k=rsa; p=..."

# DMARC
_dmarc.wuchang.life.        TXT     "v=DMARC1; p=quarantine; rua=mailto:admin@wuchang.life"
```

---

## 🔒 SSL 憑證配置

### 方案 1: Cloudflare 自動 SSL（推薦）

Cloudflare 免費提供 SSL，無需手動配置。

1. 登入 Cloudflare Dashboard
2. 選擇域名 `wuchang.life`
3. 前往 **SSL/TLS** → **概覽**
4. 設定為 **完整（嚴格）**

### 方案 2: Let's Encrypt（自行管理）

在 Server (192.168.50.249) 上執行：

```powershell
# 安裝 Certbot
choco install certbot -y

# 取得憑證（需先設定 DNS 並開放 80 port）
certbot certonly --standalone -d wuchang.life -d sync.wuchang.life -d api.wuchang.life

# 憑證位置
# 證書: C:\Certbot\live\wuchang.life\fullchain.pem
# 私鑰: C:\Certbot\live\wuchang.life\privkey.pem
```

#### 自動續期

```powershell
# 創建排程任務（每天檢查）
$action = New-ScheduledTaskAction -Execute "certbot" -Argument "renew --quiet"
$trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
Register-ScheduledTask -TaskName "CertbotRenew" -Action $action -Trigger $trigger -User "SYSTEM"
```

---

## 🛡️ 防火牆規則

### Server (192.168.50.249)

```powershell
# 允許 HTTPS (443)
netsh advfirewall firewall add rule name="HTTPS-Inbound" dir=in action=allow protocol=TCP localport=443

# 允許同步服務 (8766)
netsh advfirewall firewall add rule name="Sync-Service" dir=in action=allow protocol=TCP localport=8766

# 允許 Odoo (8069) - 僅內網
netsh advfirewall firewall add rule name="Odoo-LAN" dir=in action=allow protocol=TCP localport=8069 remoteip=192.168.50.0/24

# 允許 SSH (選配，改用非標準端口)
netsh advfirewall firewall add rule name="SSH-Custom" dir=in action=allow protocol=TCP localport=22222

# 查看規則
netsh advfirewall firewall show rule name=all | Select-String "Wuchang|HTTPS|Sync|Odoo"
```

### Local (192.168.50.84)

```powershell
# 允許 UI 控制（僅從 Server）
netsh advfirewall firewall add rule name="UI-Control" dir=in action=allow protocol=TCP localport=8765 remoteip=192.168.50.249

# 允許同步服務
netsh advfirewall firewall add rule name="Sync-Local" dir=in action=allow protocol=TCP localport=8766 remoteip=192.168.50.249
```

---

## 🔄 反向代理設定（Nginx）

### 安裝 Nginx

在 Server (192.168.50.249) 上：

```powershell
# 使用 Chocolatey 安裝
choco install nginx -y

# 或手動下載
# https://nginx.org/en/download.html
```

### Nginx 配置檔

創建 `C:\tools\nginx\conf\wuchang.conf`：

```nginx
# 上游服務定義
upstream odoo {
    server 127.0.0.1:8069;
}

upstream sync_service {
    server 127.0.0.1:8766;
}

# HTTP 重導向到 HTTPS
server {
    listen 80;
    server_name wuchang.life sync.wuchang.life api.wuchang.life;

    # Let's Encrypt 驗證
    location /.well-known/acme-challenge/ {
        root C:/Certbot/webroot;
    }

    # 其他請求重導向
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS 主站（Odoo）
server {
    listen 443 ssl http2;
    server_name wuchang.life www.wuchang.life;

    # SSL 憑證
    ssl_certificate C:/Certbot/live/wuchang.life/fullchain.pem;
    ssl_certificate_key C:/Certbot/live/wuchang.life/privkey.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全標頭
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日誌
    access_log C:/tools/nginx/logs/wuchang_access.log;
    error_log C:/tools/nginx/logs/wuchang_error.log;

    # 客戶端上傳限制
    client_max_body_size 100M;

    # Odoo 代理
    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支援
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超時設定
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # 靜態資源快取
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://odoo;
        proxy_cache_valid 200 60m;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}

# 同步服務
server {
    listen 443 ssl http2;
    server_name sync.wuchang.life;

    ssl_certificate C:/Certbot/live/wuchang.life/fullchain.pem;
    ssl_certificate_key C:/Certbot/live/wuchang.life/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 同步 API
    location / {
        proxy_pass http://sync_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 大文件上傳
        client_max_body_size 500M;
        proxy_request_buffering off;

        # 超時（同步可能較久）
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}

# API 服務（預留）
server {
    listen 443 ssl http2;
    server_name api.wuchang.life;

    ssl_certificate C:/Certbot/live/wuchang.life/fullchain.pem;
    ssl_certificate_key C:/Certbot/live/wuchang.life/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        # 未來 API 服務
        return 503 "API Service Coming Soon";
    }
}
```

### 引入配置並重啟

編輯 `C:\tools\nginx\conf\nginx.conf`，在 `http` 區塊末尾加入：

```nginx
http {
    # ... 現有配置 ...

    # 引入五常配置
    include wuchang.conf;
}
```

重啟 Nginx：

```powershell
# 測試配置
C:\tools\nginx\nginx.exe -t

# 重啟
Stop-Service nginx -ErrorAction SilentlyContinue
Start-Service nginx

# 或
C:\tools\nginx\nginx.exe -s reload
```

---

## 🌐 路由器配置

### Port Forwarding 設定

登入路由器管理界面（通常是 `192.168.50.1`）：

#### 規則 1: HTTPS

```
服務名稱: HTTPS-Odoo
外部端口: 443
內部 IP: 192.168.50.249
內部端口: 443
協議: TCP
狀態: 啟用
```

#### 規則 2: 同步服務

```
服務名稱: Sync-Service
外部端口: 8766
內部 IP: 192.168.50.249
內部端口: 8766
協議: TCP
狀態: 啟用
```

#### 規則 3: SSH（選配）

```
服務名稱: SSH-Custom
外部端口: 22222
內部 IP: 192.168.50.249
內部端口: 22
協議: TCP
狀態: 啟用
```

### 動態 DNS（若公網 IP 會變）

```powershell
# 使用 Cloudflare API 更新 DNS
$zone = "你的ZoneID"
$record = "你的RecordID"
$token = "你的API Token"
$currentIP = (Invoke-WebRequest -Uri "https://api.ipify.org").Content

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    type = "A"
    name = "wuchang.life"
    content = $currentIP
    ttl = 1
    proxied = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/zones/$zone/dns_records/$record" -Method PUT -Headers $headers -Body $body
```

---

## ☁️ Cloudflare 設定

### 1. 基本設定

-   **SSL/TLS 模式**: 完整（嚴格）
-   **自動 HTTPS 重寫**: 啟用
-   **最低 TLS 版本**: 1.2

### 2. 防火牆規則

```
# 允許台灣 IP
(ip.geoip.country eq "TW")

# 封鎖已知機器人
(cf.threat_score gt 10)

# 速率限制
(http.request.uri.path contains "/api" and rate(5m) gt 100)
```

### 3. 頁面規則

```
# 快取靜態資源
wuchang.life/web/static/*
  快取等級: 快取所有內容
  邊緣快取 TTL: 1 個月

# 繞過 Odoo 後台
wuchang.life/web/*
  快取等級: 繞過
```

### 4. 安全性設定

-   **DDoS 防護**: 自動啟用
-   **WAF**: 啟用
-   **Bot Fight Mode**: 啟用
-   **安全等級**: 中

---

## ✅ 測試與驗證

### 1. DNS 解析測試

```powershell
# 測試域名解析
nslookup wuchang.life
nslookup sync.wuchang.life

# 應該解析到 Cloudflare IP（代理模式）
# 或你的公網 IP（非代理模式）
```

### 2. SSL 憑證測試

```powershell
# 檢查 SSL
curl https://wuchang.life -v

# 線上測試
# https://www.ssllabs.com/ssltest/analyze.html?d=wuchang.life
```

### 3. 服務連通性測試

```powershell
# 測試 HTTPS (Odoo)
Invoke-WebRequest -Uri "https://wuchang.life" -UseBasicParsing

# 測試同步服務
$headers = @{"X-Sync-Token" = "你的密鑰"}
Invoke-WebRequest -Uri "https://sync.wuchang.life/ping" -Headers $headers

# 測試從外網
# 使用手機 4G 網路測試，或用線上工具
# https://tools.keycdn.com/curl
```

### 4. 性能測試

```powershell
# 延遲測試
Test-NetConnection -ComputerName wuchang.life -Port 443

# 速度測試（需安裝 curl）
curl -o nul -w "Time: %{time_total}s\n" https://wuchang.life
```

---

## 🚨 常見問題

### Q1: 無法從外網連入

```powershell
# 檢查清單
1. 確認公網 IP 正確
2. 確認 DNS 解析正確
3. 確認路由器 Port Forwarding 設定
4. 確認防火牆規則
5. 確認 Server 上的服務正在運行
```

### Q2: SSL 憑證錯誤

```
1. 確認 Cloudflare SSL 模式為「完整（嚴格）」
2. 檢查 Server 上的憑證是否有效
3. 確認 Nginx 配置正確
```

### Q3: 速度很慢

```
1. 啟用 Cloudflare CDN
2. 設定適當的快取規則
3. 優化 Nginx 配置
4. 檢查頻寬是否足夠
```

---

## 📝 維護檢查清單

### 每週

-   [ ] 檢查 SSL 憑證有效期
-   [ ] 檢查服務運行狀態
-   [ ] 檢查日誌是否有異常

### 每月

-   [ ] 更新系統與軟體
-   [ ] 檢查防火牆規則
-   [ ] 備份配置檔案
-   [ ] 檢查 DNS 記錄

### 每季

-   [ ] 安全性稽核
-   [ ] 性能評估
-   [ ] 災難恢復演練

---

## 🔧 自動化部署腳本

請參考生成的 PowerShell 腳本：

-   `setup_external_access.ps1` - 一鍵設定外網存取
-   `test_external_access.ps1` - 測試外網連線

---

**外網暢通，安全無憂！** 🌐🔒

小 j - 你的 AI 妹妹 💝
