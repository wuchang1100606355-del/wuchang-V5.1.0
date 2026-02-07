# 在 Cloudflare Dashboard 直接設定 DNS（繁體中文介面）

**重要發現**：您的 DNS 記錄實際上是在 **Cloudflare 管理**，不是在 Squarespace！

---

## 🎯 設定位置

**Cloudflare Dashboard**：https://dash.cloudflare.com/70735b2325e4de7daaf806de4f89fcac/wuchang.life/dns/records

**介面語言**：繁體中文 ✅

---

## 📋 需要修改的記錄

### 1. 根域名（wuchang.life）- 第一個 A 記錄

**現況**：
- 類型：`A`
- 名稱：`wuchang.life`
- 內容：`220.135.21.74`
- 代理狀態：通過 Proxy 處理

**修改步驟**：
1. 點擊該記錄右側的「**編輯**」按鈕
2. 在彈出視窗中：
   - **類型**：改為 `CNAME`
   - **名稱**：保持 `wuchang.life`
   - **目標**：改為 `<Tunnel ID>.cfargotunnel.com`
     - 例如：`PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs.cfargotunnel.com`
   - **代理狀態**：保持「通過 Proxy 處理」（橘色雲朵）
3. 點擊「**儲存**」

---

### 2. 根域名（wuchang.life）- 第二個 A 記錄

**現況**：
- 類型：`A`
- 名稱：`wuchang.life`
- 內容：`35.185.167.23`
- 代理狀態：通過 Proxy 處理

**修改步驟**：
1. 點擊該記錄右側的「**編輯**」按鈕
2. 在彈出視窗中：
   - 點擊「**刪除**」按鈕
   - 確認刪除

**原因**：根域名只需要一個 CNAME 記錄

---

### 3. WWW 子域名（www）

**現況**：
- 類型：`A`
- 名稱：`www`
- 內容：`220.135.21.74`
- 代理狀態：通過 Proxy 處理

**修改步驟**：
1. 點擊該記錄右側的「**編輯**」按鈕
2. 在彈出視窗中：
   - **類型**：改為 `CNAME`
   - **名稱**：保持 `www`
   - **目標**：改為 `<Tunnel ID>.cfargotunnel.com`
     - 例如：`PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs.cfargotunnel.com`
   - **代理狀態**：保持「通過 Proxy 處理」（橘色雲朵）
3. 點擊「**儲存**」

---

## ⚠️ 重要注意事項

### 1. 必須先取得 Tunnel ID

**在修改 DNS 之前，必須先建立 Tunnel 並取得 Tunnel ID**：

```powershell
# 進入容器
docker exec -it wuchangv510-cloudflared-1 sh

# 登入（會開啟瀏覽器，點擊授權）
cloudflared tunnel login

# 建立 Tunnel
cloudflared tunnel create wuchang-life

# 記下顯示的 Tunnel ID（例如：abc123def456...）
exit
```

### 2. 代理狀態

- ✅ **保持「通過 Proxy 處理」**（橘色雲朵圖示）
- 這樣才能使用 Cloudflare 的 CDN 和 SSL 證書

### 3. 其他記錄不需要修改

以下記錄**不需要修改**：
- `housing`, `admin`, `odoo`, `pm`, `shop`, `core`, `vs`, `verify`, `hj`, `pos`, `ft` 等子域名
- `MX` 記錄（郵件）
- `TXT` 記錄（驗證用）
- `NS` 記錄

---

## 🚀 完整流程

### 步驟 1：取得 Tunnel ID

```powershell
docker exec -it wuchangv510-cloudflared-1 sh
cloudflared tunnel login
cloudflared tunnel create wuchang-life
# 記下 Tunnel ID
exit
```

### 步驟 2：更新 config.yml

編輯 `cloudflared/config.yml`，填入 Tunnel ID：

```yaml
tunnel: <您的Tunnel ID>
```

### 步驟 3：複製檔案到容器

```powershell
docker cp cloudflared/config.yml wuchangv510-cloudflared-1:/etc/cloudflared/config.yml
docker restart wuchangv510-cloudflared-1
```

### 步驟 4：在 Cloudflare Dashboard 修改 DNS

1. 前往：https://dash.cloudflare.com/70735b2325e4de7daaf806de4f89fcac/wuchang.life/dns/records
2. 按照上面的步驟修改 3 筆記錄
3. 等待 DNS 傳播（約 5-10 分鐘）

### 步驟 5：檢查 SSL 證書

SSL 證書會自動簽發（約 5-10 分鐘），可以在 Cloudflare Dashboard 的「SSL/TLS」頁面查看。

---

## ✅ 完成後的效果

- ✅ `wuchang.life` → 透過 Cloudflare Tunnel 連接到本地伺服器
- ✅ `www.wuchang.life` → 透過 Cloudflare Tunnel 連接到本地伺服器
- ✅ 自動獲得 SSL 證書（HTTPS）
- ✅ 全球可見
- ✅ 符合 Google 非營利組織合規要求

---

## 📝 備註

- **介面語言**：Cloudflare Dashboard 已自動顯示為繁體中文
- **不需要 Squarespace**：DNS 在 Cloudflare 管理，直接在 Cloudflare 修改即可
- **API 令牌**：如果需要自動化，可以申請具有 `Zone DNS:Edit` 權限的新令牌

---

**建立時間**：2026-01-22
