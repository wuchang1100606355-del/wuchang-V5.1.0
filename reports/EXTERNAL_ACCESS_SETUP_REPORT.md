# 外網訪問設定報告

**設定時間：** 2026-01-20  
**狀態：** ⚠️ 需要完成憑證設定

---

## 📊 當前狀態

### ✅ 已完成

1. **配置檔案已建立**
   - ✅ `cloudflared/config.yml` - Tunnel 配置檔案
   - ✅ 已設定所有服務路由

2. **自動設定腳本已建立**
   - ✅ `scripts/setup_external_access.ps1` - 自動設定腳本
   - ✅ `scripts/EXTERNAL_ACCESS_SETUP_GUIDE.md` - 完整設定指南

3. **Docker Compose 配置已更新**
   - ✅ cloudflared 服務配置已更新為使用配置檔案

---

## ⚠️ 需要完成

### 1. 取得 Cloudflare Tunnel 憑證

**步驟：**

1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 前往 **Zero Trust** → **Networks** → **Tunnels**
3. 建立或找到 Tunnel（名稱：`wuchang-tunnel`）
4. 下載 `credentials.json` 檔案
5. 將檔案放到 `cloudflared/` 目錄

**憑證檔案位置：** `cloudflared/credentials.json`

---

### 2. 設定 DNS 路由

**在 Cloudflare Dashboard 設定以下路由：**

| Hostname | Service | 狀態 |
|----------|---------|------|
| `www.wuchang.life` | `http://caddy:80` | ⚠️ 待設定 |
| `app.wuchang.org.tw` | `http://wuchang-web:8069` | ⚠️ 待設定 |
| `ai.wuchang.org.tw` | `http://open-webui:8080` | ⚠️ 待設定 |
| `admin.wuchang.org.tw` | `http://portainer:9000` | ⚠️ 待設定 |
| `monitor.wuchang.org.tw` | `http://uptime-kuma:3001` | ⚠️ 待設定 |

---

### 3. 修復 Caddy 配置問題

**問題：** Caddyfile 路徑問題導致 Caddy 容器無法啟動

**解決方法：**
- 檢查 `wuchang_os/Caddyfile` 是否存在
- 如果不存在，需要建立 Caddyfile 配置檔案
- 或調整 docker-compose.yml 中的路徑配置

---

## 🔧 設定步驟

### 完整設定流程

1. **取得憑證**
   ```powershell
   # 從 Cloudflare Dashboard 下載 credentials.json
   # 放到 cloudflared/ 目錄
   ```

2. **啟動 Cloudflare Tunnel**
   ```powershell
   docker-compose -f docker-compose.yml --profile system up -d cloudflared
   ```

3. **驗證設定**
   ```powershell
   docker logs wuchang-cloudflared-1 --tail 20
   ```

---

## 📝 外網訪問地址

設定完成後，可通過以下地址訪問：

| 服務 | 外網地址 | 本地地址 |
|------|---------|---------|
| **首頁** | http://www.wuchang.life | http://localhost:80 |
| **Odoo ERP** | https://app.wuchang.org.tw | http://localhost:8069 |
| **AI 介面** | https://ai.wuchang.org.tw | http://localhost:8080 |
| **容器管理** | https://admin.wuchang.org.tw | http://localhost:9000 |
| **系統監控** | https://monitor.wuchang.org.tw | http://localhost:3001 |

---

## ✅ 檢查清單

- [ ] 取得 Cloudflare Tunnel 憑證（credentials.json）
- [ ] 將憑證放到 `cloudflared/` 目錄
- [ ] 在 Cloudflare Dashboard 設定 DNS 路由
- [ ] 修復 Caddyfile 配置問題
- [ ] 啟動 Cloudflare Tunnel 容器
- [ ] 驗證容器正常運行
- [ ] 測試外網訪問

---

**報告時間：** 2026-01-20  
**狀態：** 配置已準備，等待憑證和 DNS 設定 ⚠️
