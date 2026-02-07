# 外網訪問設定狀態報告

**檢查時間：** 2026-01-20  
**狀態：** ⚠️ 需要完成憑證設定

---

## 📊 當前狀態摘要

### ✅ 已準備完成

1. **配置檔案**
   - ✅ `cloudflared/config.yml` - Tunnel 路由配置
   - ✅ 已設定所有服務路由（首頁、Odoo、AI、管理、監控）

2. **自動化腳本**
   - ✅ `scripts/setup_external_access.ps1` - 自動設定腳本
   - ✅ `scripts/EXTERNAL_ACCESS_SETUP_GUIDE.md` - 完整指南

3. **Docker 配置**
   - ✅ `docker-compose.yml` 已更新
   - ✅ Cloudflare Tunnel 服務配置已就緒

---

## ⚠️ 需要完成（兩個關鍵步驟）

### 1. 取得 Cloudflare Tunnel 憑證 ⚠️ **必須**

**快速步驟：**
1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. **Zero Trust** → **Networks** → **Tunnels**
3. 建立或選擇 Tunnel（名稱：`wuchang-tunnel`）
4. 下載 `credentials.json`
5. 放到 `cloudflared/` 目錄

**檔案位置：** `cloudflared/credentials.json`

---

### 2. 設定 DNS 路由 ⚠️ **必須**

**在 Cloudflare Dashboard 設定以下路由：**

| Hostname | Service | 用途 |
|----------|---------|------|
| `www.wuchang.life` | `http://caddy:80` | 首頁 |
| `app.wuchang.org.tw` | `http://wuchang-web:8069` | Odoo ERP |
| `ai.wuchang.org.tw` | `http://open-webui:8080` | AI 介面 |
| `admin.wuchang.org.tw` | `http://portainer:9000` | 容器管理 |
| `monitor.wuchang.org.tw` | `http://uptime-kuma:3001` | 系統監控 |

**設定位置：**
- Cloudflare Dashboard → Zero Trust → Networks → Tunnels
- 點擊 `wuchang-tunnel` → **Public Hostnames** → **Add a public hostname**

---

## 🚀 完成設定後

**啟動 Cloudflare Tunnel：**

```powershell
.\scripts\setup_external_access.ps1
```

或：

```powershell
docker-compose -f docker-compose.yml --profile system up -d cloudflared
```

---

## 🌐 外網訪問地址

設定完成後，可通過以下地址訪問：

- **首頁：** http://www.wuchang.life
- **Odoo ERP：** https://app.wuchang.org.tw
- **AI 介面：** https://ai.wuchang.org.tw
- **容器管理：** https://admin.wuchang.org.tw
- **系統監控：** https://monitor.wuchang.org.tw

---

## 📋 快速檢查清單

- [ ] 取得 Cloudflare Tunnel 憑證（credentials.json）
- [ ] 將憑證放到 `cloudflared/` 目錄
- [ ] 在 Cloudflare Dashboard 設定 DNS 路由
- [ ] 啟動 Cloudflare Tunnel 容器
- [ ] 驗證容器正常運行
- [ ] 測試外網訪問

---

**詳細指南：** `scripts/EXTERNAL_ACCESS_SETUP_GUIDE.md`  
**快速開始：** `reports/EXTERNAL_ACCESS_QUICK_START.md`
