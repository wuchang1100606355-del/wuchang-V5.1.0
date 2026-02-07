# DNS 設定狀態說明

**檢查時間：** 2026-01-20

## 📊 目前狀態

### ❌ 需要進行 DNS 設定

根據檢查結果，**仍需要進行 DNS 設定**才能正常使用域名訪問服務。

---

## 🔍 為什麼需要設定？

### 當前問題

1. **域名無法解析**
   - `app.wuchang.org.tw` 等域名無法解析到 Cloudflare
   - 本地 DNS 查詢失敗

2. **Cloudflare Tunnel 未完整設定**
   - 容器運行中，但使用臨時隧道（trycloudflare.com）
   - 配置檔案中的 Tunnel ID 仍是佔位符 `<tunnel-id>`
   - 憑證檔案不存在

3. **服務無法通過域名訪問**
   - HTTPS 連接失敗
   - 無法使用正式域名訪問服務

### 如果設定 DNS 的好處

✅ **使用正式域名訪問**
- `https://app.wuchang.org.tw` → Odoo ERP
- `https://ai.wuchang.org.tw` → Open WebUI
- `https://admin.wuchang.org.tw` → Portainer
- `https://monitor.wuchang.org.tw` → Uptime Kuma

✅ **自動 HTTPS 加密**
- Cloudflare 自動管理 SSL 證書
- 無需手動配置證書

✅ **DDoS 防護**
- Cloudflare 自動防護
- 隱藏真實 IP

✅ **高可用性**
- Cloudflare 全球 CDN
- 自動負載均衡

---

## 🤔 可以跳過 DNS 設定嗎？

### 選項 1: 使用本地訪問（不需要 DNS）

如果您只在本機使用，**可以不設定 DNS**，直接使用本地端口：

- `http://localhost:8069` → Odoo ERP
- `http://localhost:8080` → Open WebUI
- `http://localhost:9000` → Portainer
- `http://localhost:3001` → Uptime Kuma

**優點：**
- 不需要任何設定
- 立即可用

**缺點：**
- 無法從外網訪問
- 需要使用 IP 地址或 localhost
- 沒有 HTTPS（除非本地配置）

### 選項 2: 使用 Cloudflare Tunnel 臨時域名（不需要 DNS）

容器目前已經在使用臨時隧道，會產生臨時域名（例如：`xxxxx.trycloudflare.com`）。

**查看臨時域名：**
```bash
docker logs wuchangv510-cloudflared-1 | grep "trycloudflare.com"
```

**優點：**
- 立即可以使用
- 自動 HTTPS
- 可以外網訪問

**缺點：**
- 域名不固定（每次重啟可能不同）
- 沒有正常運行保證
- 不適合生產環境

### 選項 3: 完整設定 DNS（推薦）

設定正式的 DNS 和 Cloudflare Tunnel。

**優點：**
- 使用正式域名
- 穩定可靠
- 適合生產環境

**缺點：**
- 需要一些設定步驟（約 5-10 分鐘）
- 需要 Cloudflare 帳號

---

## 📋 DNS 設定步驟總結

如果需要設定 DNS，需要執行以下步驟：

### 1. 安裝 cloudflared（如果還沒有）
```bash
# 下載: https://github.com/cloudflare/cloudflared/releases
```

### 2. 登入 Cloudflare
```bash
cloudflared tunnel login
```

### 3. 建立隧道
```bash
cloudflared tunnel create wuchang-tunnel
```

### 4. 設定 DNS 路由
```bash
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

### 5. 複製憑證並更新配置
- 複製憑證到 `cloudflared/credentials.json`
- 更新 `cloudflared/config.yml` 中的 Tunnel ID

### 6. 重啟容器
```bash
docker restart wuchangv510-cloudflared-1
```

---

## 💡 建議

### 如果您只需要本機使用

**可以不設定 DNS**，直接使用：
- `http://localhost:8069`
- `http://localhost:8080`
- 等等

### 如果需要外網訪問

**建議設定 DNS**，這樣可以：
- 使用正式的域名
- 穩定可靠
- 自動 HTTPS

### 如果暫時不想設定

可以使用臨時隧道域名（查看容器日誌中的 `trycloudflare.com` 網址）。

---

## ✅ 決定

**您的使用情況？**

1. **只在本機使用** → 不需要設定 DNS
2. **需要外網訪問但暫時用臨時域名** → 不需要設定 DNS（使用現有臨時隧道）
3. **需要正式的穩定域名** → **需要設定 DNS**（約 5-10 分鐘）

---

**詳細設定指南：** `DNS_FIX_GUIDE.md`
