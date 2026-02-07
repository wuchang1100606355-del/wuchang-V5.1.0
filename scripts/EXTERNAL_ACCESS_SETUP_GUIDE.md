# 外網訪問設定完整指南

**建立時間：** 2026-01-20  
**目的：** 啟用系統外網訪問功能

---

## 🚀 快速設定（自動）

**執行自動設定腳本：**

```powershell
.\scripts\setup_external_access.ps1
```

腳本會自動：
- ✅ 檢查 Cloudflare Tunnel 容器狀態
- ✅ 檢查配置檔案
- ✅ 啟動 Cloudflare Tunnel 服務
- ✅ 顯示設定狀態

---

## 📋 完整設定步驟

### 步驟 1：準備 Cloudflare Tunnel 憑證

**方式 A：使用現有 Tunnel（推薦）**

1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 前往 **Zero Trust** → **Networks** → **Tunnels**
3. 找到或建立 Tunnel（名稱：`wuchang-tunnel`）
4. 下載 `credentials.json` 檔案
5. 將檔案放到 `cloudflared/` 目錄

**方式 B：建立新 Tunnel**

```bash
# 使用 cloudflared CLI 建立
cloudflared tunnel create wuchang-tunnel

# 下載憑證
cloudflared tunnel credentials-file wuchang-tunnel credentials.json
```

---

### 步驟 2：設定 DNS 路由

**在 Cloudflare Dashboard 設定：**

1. 前往 **Zero Trust** → **Networks** → **Tunnels**
2. 點擊 `wuchang-tunnel`
3. 設定 **Public Hostnames**：

| Hostname | Service | 說明 |
|----------|---------|------|
| `www.wuchang.life` | `http://caddy:80` | 首頁 |
| `app.wuchang.org.tw` | `http://wuchang-web:8069` | Odoo ERP |
| `ai.wuchang.org.tw` | `http://open-webui:8080` | AI 介面 |
| `admin.wuchang.org.tw` | `http://portainer:9000` | 容器管理 |
| `monitor.wuchang.org.tw` | `http://uptime-kuma:3001` | 系統監控 |

**或使用 CLI 設定：**

```bash
# 首頁
cloudflared tunnel route dns wuchang-tunnel www.wuchang.life

# Odoo ERP
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw

# AI 介面
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw

# 容器管理
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw

# 系統監控
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

---

### 步驟 3：更新 docker-compose.yml

確保 Cloudflare Tunnel 容器配置正確：

```yaml
cloudflared:
  image: cloudflare/cloudflared:latest
  depends_on:
    - caddy
    - wuchang-web
    - open-webui
    - portainer
    - uptime-kuma
  volumes:
    - ./cloudflared/config.yml:/etc/cloudflared/config.yml:ro
    - ./cloudflared/credentials.json:/etc/cloudflared/credentials.json:ro
  command: tunnel run
  restart: unless-stopped
```

---

### 步驟 4：啟動服務

```powershell
# 啟動 Cloudflare Tunnel
docker-compose -f docker-compose.yml --profile system up -d cloudflared

# 檢查狀態
docker ps --filter "name=cloudflared"

# 查看日誌
docker logs wuchang-cloudflared-1 --tail 20
```

---

## ✅ 驗證外網訪問

### 1. 檢查容器狀態

```powershell
docker ps --filter "name=cloudflared"
```

**預期：** 容器狀態為 "Up"

---

### 2. 檢查日誌

```powershell
docker logs wuchang-cloudflared-1 --tail 20
```

**預期看到：**
- `Connecting to tunnel...`
- `Connection established`
- `Registered tunnel connection`

---

### 3. 測試 DNS 解析

```powershell
nslookup www.wuchang.life
```

**預期：** 解析到 Cloudflare IP（104.x.x.x 或 172.x.x.x）

---

### 4. 測試外網訪問

**在瀏覽器訪問：**
- `http://www.wuchang.life` - 首頁
- `https://app.wuchang.org.tw` - Odoo ERP
- `https://ai.wuchang.org.tw` - AI 介面
- `https://admin.wuchang.org.tw` - 容器管理
- `https://monitor.wuchang.org.tw` - 系統監控

---

## 🔧 故障排除

### 問題 1：容器無法啟動

**檢查：**
- 憑證檔案是否存在
- 配置檔案格式是否正確
- 日誌中的錯誤訊息

**解決：**
```powershell
# 查看詳細日誌
docker logs wuchang-cloudflared-1

# 檢查配置檔案
Get-Content cloudflared\config.yml
```

---

### 問題 2：DNS 解析失敗

**檢查：**
- DNS 路由是否正確設定
- 域名是否已添加到 Cloudflare

**解決：**
- 確認 DNS 路由已設定
- 等待 DNS 傳播（可能需要幾分鐘）

---

### 問題 3：連接超時

**檢查：**
- Tunnel 是否正常連接
- 容器網路配置是否正確

**解決：**
```powershell
# 重啟 Tunnel
docker restart wuchang-cloudflared-1

# 檢查容器網路
docker network inspect wuchang_default
```

---

## 📊 外網訪問地址

設定完成後，可通過以下地址訪問：

| 服務 | 外網地址 | 本地地址 |
|------|---------|---------|
| **首頁** | http://www.wuchang.life | http://localhost:80 |
| **Odoo ERP** | https://app.wuchang.org.tw | http://localhost:8069 |
| **AI 介面** | https://ai.wuchang.org.tw | http://localhost:8080 |
| **容器管理** | https://admin.wuchang.org.tw | http://localhost:9000 |
| **系統監控** | https://monitor.wuchang.org.tw | http://localhost:3001 |

---

## 📝 相關檔案

- `cloudflared/config.yml` - Tunnel 配置檔案
- `cloudflared/credentials.json` - Tunnel 憑證（需從 Cloudflare 取得）
- `scripts/setup_external_access.ps1` - 自動設定腳本
- `reports/HOMEPAGE_WUCHANG_LIFE_SETUP.md` - 首頁設定指南

---

**指南時間：** 2026-01-20  
**狀態：** 準備就緒，等待執行 ✅
