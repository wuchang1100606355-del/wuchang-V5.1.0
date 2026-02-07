# 外網訪問配置指南

## ✅ 是的，可以從外網訪問！

系統支援多種外網訪問方式，讓您可以在任何地方使用服務。

---

## 🌐 外網訪問方式

### 方式 1：Cloudflare Tunnel（推薦）⭐

**最安全、最簡單的方式，無需開放路由器端口**

#### 優點
- ✅ **完全免費**
- ✅ **自動 HTTPS**（SSL 證書自動管理）
- ✅ **無需開放路由器端口**（不需要固定 IP）
- ✅ **隱藏真實 IP**（通過 Cloudflare CDN）
- ✅ **DDoS 防護**（Cloudflare 自動防護）

#### 配置步驟

1. **建立 Cloudflare 帳號**（如果還沒有）
   - 前往 https://dash.cloudflare.com/
   - 註冊免費帳號

2. **新增您的網域到 Cloudflare**
   - 在 Cloudflare Dashboard 新增網域
   - 按照指示更新 DNS 設定

3. **建立 Cloudflare Tunnel**
   ```bash
   # 安裝 cloudflared（如果還沒有）
   # Windows: 下載 https://github.com/cloudflare/cloudflared/releases
   
   # 登入 Cloudflare
   cloudflared tunnel login
   
   # 建立隧道
   cloudflared tunnel create wuchang-tunnel
   
   # 建立配置檔案
   ```

4. **配置 Docker Compose**

   建立 `docker-compose.external.yml`：
   ```yaml
   version: '3.8'
   
   services:
     cloudflared:
       image: cloudflare/cloudflared:latest
       container_name: wuchang-cloudflared
       restart: unless-stopped
       command: tunnel run
       volumes:
         - ./cloudflared/config.yml:/etc/cloudflared/config.yml:ro
         - ./cloudflared/credentials.json:/etc/cloudflared/credentials.json:ro
   
     wuchang-web:
       image: odoo:17.0
       depends_on:
         - db
       ports:
         - "8069:8069"  # 內部端口，cloudflared 會轉發
       volumes:
         - ./local_storage/data/odoo:/var/lib/odoo
         - ./local_storage/uploads:/var/lib/odoo/filestore
       restart: unless-stopped
   
     db:
       image: postgres:15
       environment:
         - POSTGRES_DB=postgres
         - POSTGRES_PASSWORD=odoo
         - POSTGRES_USER=odoo
       volumes:
         - ./local_storage/database/data:/var/lib/postgresql/data
       restart: unless-stopped
   ```

5. **配置 Cloudflare Tunnel 路由**

   編輯 `cloudflared/config.yml`：
   ```yaml
   tunnel: <tunnel-id>
   credentials-file: /etc/cloudflared/credentials.json
   
   ingress:
     # Odoo ERP 系統
     - hostname: app.wuchang.org.tw
       service: http://wuchang-web:8069
     
     # 預設規則（必須放在最後）
     - service: http_status:404
   ```

6. **啟動服務**
   ```bash
   docker-compose -f docker-compose.external.yml up -d
   ```

7. **訪問服務**
   - 打開瀏覽器訪問：`https://app.wuchang.org.tw`
   - 自動使用 HTTPS，無需額外配置

---

### 方式 2：DDNS + 路由器端口轉發

**使用您的路由器 DDNS（coffeeLofe.asuscomm.com）**

#### 優點
- ✅ 使用現有路由器 DDNS
- ✅ 直接連接，延遲較低

#### 缺點
- ⚠️ 需要開放路由器端口
- ⚠️ 需要手動管理 SSL 證書
- ⚠️ 暴露真實 IP

#### 配置步驟

1. **在路由器設定端口轉發**
   ```
   外部端口：8069 → 內部 IP：10.8.0.1:8069
   ```

2. **配置 Caddy 反向代理**（自動 HTTPS）

   建立 `Caddyfile`：
   ```
   app.wuchang.org.tw {
       reverse_proxy localhost:8069
   }
   ```

3. **訪問服務**
   - `https://coffeeLofe.asuscomm.com:8069`
   - 或使用域名：`https://app.wuchang.org.tw`

---

### 方式 3：VPN 訪問（內部網路）

**透過 VPN 連接後，使用內網 IP 訪問**

#### 優點
- ✅ 最安全（加密連接）
- ✅ 不需要公開服務

#### 缺點
- ⚠️ 需要先連接 VPN
- ⚠️ 需要 VPN 客戶端

#### 配置步驟

1. **連接 VPN**
   ```bash
   # 使用 OpenVPN 或系統 VPN
   # VPN 網段：10.8.0.0/24
   ```

2. **訪問服務**
   - 本機：`http://localhost:8069`
   - 伺服器：`http://10.8.0.1:8069`
   - 本機（從伺服器）：`http://10.8.0.6:8069`

---

## 📋 推薦配置方案

### 方案 A：完全外網訪問（推薦）

```
Internet
    ↓
Cloudflare Tunnel (cloudflared)
    ↓
Docker 容器 (localhost:8069)
    ↓
服務正常運行
```

**優點：**
- ✅ 任何地方都可以訪問
- ✅ 自動 HTTPS
- ✅ 不需要開放路由器端口
- ✅ 免費

---

### 方案 B：混合方案

```
外網訪問：
  Cloudflare Tunnel → app.wuchang.org.tw

內部訪問：
  VPN → 10.8.0.1:8069
  DDNS → coffeeLofe.asuscomm.com:8069
```

**優點：**
- ✅ 多種訪問方式
- ✅ 外網和內網都可以使用
- ✅ 靈活配置

---

## 🔧 快速設定腳本

建立 `setup_external_access.py` 自動配置外網訪問：

```python
# 自動設定 Cloudflare Tunnel
# 自動配置域名路由
# 自動啟動服務
```

---

## ⚠️ 安全注意事項

### 1. **使用 HTTPS**
- ✅ Cloudflare Tunnel 自動提供 HTTPS
- ✅ Caddy 可以自動申請 Let's Encrypt 證書

### 2. **防火牆設定**
- ✅ 只開放必要的端口
- ✅ 使用 Cloudflare Tunnel 時不需要開放端口

### 3. **認證保護**
- ✅ 為管理介面設定密碼
- ✅ 使用 OAuth 或 API Key 保護 API

### 4. **資料庫安全**
- ✅ **絕對不要**將資料庫端口暴露到外網
- ✅ 只允許應用容器訪問資料庫

---

## 📝 當前狀態檢查

### 檢查 Cloudflare Tunnel
```bash
docker ps | grep cloudflared
docker logs wuchang-cloudflared
```

### 檢查端口開放
```bash
# Windows
netstat -an | findstr :8069

# 檢查外部訪問
curl https://app.wuchang.org.tw
```

### 檢查 VPN 連接
```bash
ipconfig | findstr "10.8.0"
ping 10.8.0.1
```

---

## 🎯 總結

**是的，可以從外網訪問！** 推薦使用 **Cloudflare Tunnel**：

1. ✅ **完全免費**
2. ✅ **自動 HTTPS**
3. ✅ **不需要開放路由器端口**
4. ✅ **安全可靠**
5. ✅ **任何地方都可以訪問**

**下一步：**
1. 設定 Cloudflare 帳號和網域
2. 建立 Cloudflare Tunnel
3. 配置域名路由
4. 啟動服務
5. 從任何地方訪問您的服務！

---

## 📚 相關文件

- `DOMAIN_DEPLOYMENT_PLAN.md` - 完整域名部署規劃
- `NETWORK_INTERCONNECTION_DDNS_VPN.md` - 網路互通設定
- `docker-compose.safe.yml` - 本地儲存配置
- `domain_deployment_helper.py` - 部署輔助工具
