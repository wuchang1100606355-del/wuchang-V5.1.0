# 外網訪問快速開始指南

**建立時間：** 2026-01-20  
**狀態：** ⚠️ 需要 Cloudflare 憑證

---

## 🚀 三步驟開啟外網訪問

### 步驟 1：取得 Cloudflare 憑證 ⚠️（必須）

**快速方式：**

1. 前往 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 進入 **Zero Trust** → **Networks** → **Tunnels**
3. 點擊 **Create a tunnel**
4. 選擇 **Cloudflared**
5. 命名為 `wuchang-tunnel`
6. 下載 `credentials.json`
7. 放到 `cloudflared/` 目錄

**憑證檔案路徑：** `cloudflared/credentials.json`

---

### 步驟 2：啟動 Cloudflare Tunnel ✅（已準備）

**執行設定腳本：**

```powershell
.\scripts\setup_external_access.ps1
```

或手動啟動：

```powershell
docker-compose -f docker-compose.yml --profile system up -d cloudflared
```

---

### 步驟 3：設定 DNS 路由 ⚠️（必須）

**在 Cloudflare Dashboard 設定：**

| Hostname | Service | 說明 |
|----------|---------|------|
| `www.wuchang.life` | `http://caddy:80` | 首頁 |
| `app.wuchang.org.tw` | `http://wuchang-web:8069` | Odoo ERP |

**設定位置：**
- Cloudflare Dashboard → Zero Trust → Networks → Tunnels
- 點擊 `wuchang-tunnel` → Public Hostnames
- 添加上述路由

---

## ✅ 完成後驗證

```powershell
# 檢查容器
docker ps --filter "name=cloudflared"

# 查看日誌
docker logs wuchang-cloudflared-1 --tail 20

# 測試訪問
curl http://www.wuchang.life
```

---

## 🌐 外網訪問地址

設定完成後可通過以下地址訪問：

- **首頁：** http://www.wuchang.life
- **Odoo ERP：** https://app.wuchang.org.tw
- **AI 介面：** https://ai.wuchang.org.tw
- **容器管理：** https://admin.wuchang.org.tw
- **系統監控：** https://monitor.wuchang.org.tw

---

## ⚠️ 當前狀態

✅ **已完成：**
- 配置檔案已建立
- Docker Compose 配置已更新
- 自動設定腳本已準備

⚠️ **待完成：**
- 取得 Cloudflare Tunnel 憑證
- 設定 DNS 路由
- 啟動 Cloudflare Tunnel 容器

---

**詳細指南：** `scripts/EXTERNAL_ACCESS_SETUP_GUIDE.md`
