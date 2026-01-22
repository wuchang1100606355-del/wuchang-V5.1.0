# DNS 設定位置指南

**更新時間**：2026-01-22  
**目的**：確認網域 DNS 設定位置並提供設定指引

---

## 📍 DNS 設定位置確認

**您的網域商**：**Squarespace**  
**DNS 設定位置**：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings

---

### 情況 1：網域在 Cloudflare 管理

**判斷依據**：
- 使用 Cloudflare Tunnel
- 需要配置 CNAME 指向 `<tunnel-id>.cfargotunnel.com`
- Cloudflare Tunnel 通常與 Cloudflare DNS 一起使用

**設定位置**：**Cloudflare Dashboard**

**設定步驟**：
1. 訪問：https://dash.cloudflare.com/
2. 選擇網域：`wuchang.life`
3. 進入 **DNS** → **Records**
4. 配置以下記錄：

```
類型    名稱          目標                              Proxy     TTL
CNAME   @             <tunnel-id>.cfargotunnel.com     ✅ 開啟    Auto
CNAME   www           <tunnel-id>.cfargotunnel.com     ✅ 開啟    Auto
```

**注意**：
- `@` 代表根域名 `wuchang.life`
- Proxy 必須開啟（橙色雲朵圖示）
- 設定後等待 5-10 分鐘讓 DNS 傳播

---

### 情況 2：網域在 Squarespace 管理 ✅ **您的網域商**

**確認**：您的網域 `wuchang.life` 在 **Squarespace** 管理

**設定位置**：**Squarespace 控制台**
- 直接訪問：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings

**設定步驟**：
1. 訪問：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings
2. 登入 Squarespace 帳戶
3. 進入 DNS 設定頁面
4. 配置以下記錄：

**⚠️ 重要：需要先完成 Cloudflare Tunnel 配置才能取得 Tunnel ID**

**設定前準備**：
- [ ] 完成 Cloudflare Tunnel 登入（`cloudflared tunnel login`）
- [ ] 建立或選擇 Tunnel（`cloudflared tunnel create wuchang-life`）
- [ ] 取得 Tunnel ID（例如：`abc123def456...`）

**DNS 記錄設定**：

```
類型    主機名稱      指向/目標                         TTL
CNAME   @             <tunnel-id>.cfargotunnel.com     自動
CNAME   www           <tunnel-id>.cfargotunnel.com     自動
```

**Squarespace 設定說明**：
- **主機名稱**：`@` 代表根域名 `wuchang.life`，`www` 代表 `www.wuchang.life`
- **指向/目標**：填入 `<tunnel-id>.cfargotunnel.com`（將 `<tunnel-id>` 替換為實際的 Tunnel ID）
- **TTL**：選擇自動或 300 秒

**注意**：
- Squarespace 可能不支援根域名（@）使用 CNAME
- 如果不支援，需要：
  1. 將 DNS 管理轉移到 Cloudflare（推薦），或
  2. 使用 A 記錄指向 Cloudflare 的 IP（不推薦，無法使用 Tunnel）

---

### 情況 3：DNS 管理已轉移到 Cloudflare

**判斷依據**：
- 網域註冊商顯示 DNS 伺服器為 Cloudflare
- 例如：`ns1.cloudflare.com`, `ns2.cloudflare.com`

**設定位置**：**Cloudflare Dashboard**

**設定步驟**：同「情況 1」

---

## 🔍 如何確認網域管理位置

### 方法 1：檢查 DNS 伺服器

```bash
# Windows
nslookup -type=NS wuchang.life

# 查看返回的 DNS 伺服器名稱
# 如果是 cloudflare.com → 在 Cloudflare 管理
# 如果是其他（如 namecheap.com, godaddy.com）→ 在註冊商管理
```

### 方法 2：檢查網域註冊商

1. 訪問：https://whois.net/ 或 https://whois.com/
2. 查詢：`wuchang.life`
3. 查看 **Registrar** 欄位
4. 查看 **Name Servers** 欄位

### 方法 3：嘗試登入 Cloudflare

1. 訪問：https://dash.cloudflare.com/
2. 嘗試登入
3. 查看是否有 `wuchang.life` 網域
4. 如果有 → 在 Cloudflare 管理
5. 如果沒有 → 可能在註冊商管理

---

## 📋 設定前準備

### 必須取得的資訊

1. **Tunnel ID**
   - 從 Cloudflare Dashboard → Zero Trust → Networks → Tunnels
   - 或從 `cloudflared tunnel list` 命令取得

2. **Cloudflare 帳戶**
   - 如果網域在 Cloudflare 管理，需要登入 Cloudflare Dashboard

3. **網域註冊商帳戶**
   - 如果網域在註冊商管理，需要登入註冊商控制台

---

## 🎯 推薦設定方式

### 最佳方案：將 DNS 管理轉移到 Cloudflare

**優點**：
- ✅ 可以使用 Cloudflare Tunnel 的所有功能
- ✅ 自動 SSL 證書（免費）
- ✅ 全球 CDN 加速
- ✅ 更好的安全性
- ✅ 免費使用

**步驟**：
1. 在 Cloudflare 添加網域
2. Cloudflare 會提供 DNS 伺服器名稱
3. 在網域註冊商更新 DNS 伺服器
4. 等待 DNS 傳播（通常 24-48 小時）
5. 在 Cloudflare Dashboard 配置 DNS 記錄

---

## ⚠️ 重要注意事項

### 1. 根域名 CNAME 限制

**問題**：某些 DNS 服務不支援根域名（@）使用 CNAME

**解決方案**：
- **方案 A**：將 DNS 管理轉移到 Cloudflare（推薦）
- **方案 B**：使用 Cloudflare 的 CNAME Flattening 功能
- **方案 C**：使用 A 記錄指向 Cloudflare IP（不推薦，無法使用 Tunnel）

### 2. DNS 傳播時間

- **TTL 設定**：建議使用 Auto 或較短的 TTL（300 秒）
- **傳播時間**：通常 5-10 分鐘，最多 24-48 小時
- **驗證方法**：使用 https://www.whatsmydns.net/ 檢查全球 DNS 傳播

### 3. 現有記錄處理

**在修改前**：
- [ ] 備份現有 DNS 記錄
- [ ] 確認哪些記錄需要保留
- [ ] 確認哪些記錄需要修改

**修改時**：
- [ ] 先添加新記錄
- [ ] 驗證新記錄正常
- [ ] 再刪除舊記錄

---

## 📝 設定檢查清單

### 設定前
- [ ] 確認網域管理位置（Cloudflare 或註冊商）
- [ ] 取得 Tunnel ID
- [ ] 備份現有 DNS 記錄
- [ ] 確認 Cloudflare Tunnel 已配置並運行

### 設定中
- [ ] 在正確位置（Cloudflare 或註冊商）配置 DNS 記錄
- [ ] 配置根域名 CNAME：`@` → `<tunnel-id>.cfargotunnel.com`
- [ ] 配置 WWW CNAME：`www` → `<tunnel-id>.cfargotunnel.com`
- [ ] 確認 Proxy 狀態（Cloudflare）或記錄類型正確（註冊商）

### 設定後
- [ ] 等待 DNS 傳播（5-10 分鐘）
- [ ] 使用 `nslookup` 驗證 DNS 解析
- [ ] 使用 https://www.whatsmydns.net/ 檢查全球傳播
- [ ] 測試 `https://wuchang.life` 可訪問
- [ ] 測試 `https://www.wuchang.life` 可訪問
- [ ] 確認 SSL 證書有效

---

## 🔗 相關資源

- **Cloudflare Dashboard**：https://dash.cloudflare.com/
- **Cloudflare Tunnel 文檔**：https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **DNS 傳播檢查**：https://www.whatsmydns.net/
- **WHOIS 查詢**：https://whois.net/

---

## 💡 快速判斷

**如果您不確定網域在哪裡管理，請執行：**

```bash
# Windows PowerShell
nslookup -type=NS wuchang.life

# 查看返回的 DNS 伺服器名稱
# 如果包含 "cloudflare" → 在 Cloudflare 管理
# 如果包含其他名稱（如 "namecheap", "godaddy"）→ 在註冊商管理
```

**或者直接嘗試：**
1. 訪問 https://dash.cloudflare.com/ 並登入
2. 查看是否有 `wuchang.life` 網域
3. 如果有 → 在 Cloudflare 設定
4. 如果沒有 → 在網域註冊商設定

---

**報告生成時間**：2026-01-22
