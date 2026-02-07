# 不修改 DNS 的替代方案（符合 Google 非營利規範）

**重要限制**：根據 Google 非營利組織規範，**不能修改網站和網域設定**。

---

## 🎯 目標

在不修改 DNS 記錄的前提下，實現：
1. ✅ HTTPS/SSL 證書（Google 非營利要求）
2. ✅ 全球可見性（Google 非營利要求）
3. ✅ 保持現有 DNS 記錄不變

---

## 💡 解決方案：使用 Cloudflare Tunnel（不需要修改 DNS）

### 關鍵發現

**Cloudflare Tunnel 可以在不修改 DNS 的情況下運作**！

### 工作原理

1. **Cloudflare Tunnel 連接到 Cloudflare**
   - Tunnel 在本地運行，主動連接到 Cloudflare
   - 不需要修改 DNS 記錄

2. **使用 Cloudflare 的代理功能**
   - 現有的 A 記錄保持不變
   - Cloudflare 的代理會自動處理 HTTPS
   - 流量通過 Cloudflare 的 CDN

3. **SSL 證書自動簽發**
   - Cloudflare 會自動為您的域名簽發 SSL 證書
   - 不需要修改 DNS 記錄

---

## 🚀 實施步驟

### 步驟 1：完成 Cloudflare Tunnel 配置（已完成 ✅）

- ✅ 已登入 Cloudflare
- ✅ 已建立 Tunnel：`wuchang-life`
- ✅ Tunnel ID：`837487dc-1536-43ec-a1c9-ee366a0aa4b7`
- ✅ 已更新 `config.yml`

### 步驟 2：複製檔案到容器

```powershell
# 複製憑證檔案
docker cp "C:\Users\o0930\.cloudflared\837487dc-1536-43ec-a1c9-ee366a0aa4b7.json" wuchangv510-cloudflared-1:/etc/cloudflared/credentials.json

# 複製 config.yml
docker cp cloudflared/config.yml wuchangv510-cloudflared-1:/etc/cloudflared/config.yml
```

### 步驟 3：重啟容器

```powershell
docker restart wuchangv510-cloudflared-1
```

### 步驟 4：檢查日誌

```powershell
docker logs wuchangv510-cloudflared-1
```

應該看到 `Connection established` 或類似的成功訊息。

---

## ⚠️ 重要：不需要修改 DNS

### 為什麼不需要修改 DNS？

1. **Cloudflare Tunnel 是主動連接**
   - Tunnel 從本地主動連接到 Cloudflare
   - 不需要 DNS 指向 Tunnel

2. **Cloudflare 代理會自動處理**
   - 現有的 A 記錄（`220.135.21.74`）保持不變
   - Cloudflare 的代理會自動將流量路由到 Tunnel
   - 不需要將 DNS 改為 CNAME

3. **SSL 證書會自動簽發**
   - Cloudflare 會自動為您的域名簽發 SSL 證書
   - 不需要修改 DNS 記錄

---

## 📋 驗證步驟

### 1. 檢查 Tunnel 連接

```powershell
docker logs wuchangv510-cloudflared-1
```

應該看到：
- `Connection established`
- 沒有錯誤訊息

### 2. 檢查 HTTPS 訪問

在瀏覽器訪問：
- https://wuchang.life
- https://www.wuchang.life

應該看到：
- ✅ 有效的 SSL 證書（鎖頭圖示）
- ✅ 網站正常載入

### 3. 檢查 DNS 記錄（確認未修改）

在 Cloudflare Dashboard 檢查：
- ✅ `wuchang.life` 的 A 記錄仍然是 `220.135.21.74`
- ✅ `www.wuchang.life` 的 A 記錄仍然是 `220.135.21.74`
- ✅ **DNS 記錄未修改**

---

## ✅ 符合 Google 非營利規範

### 技術要求

- ✅ **HTTPS/SSL 證書**：通過 Cloudflare 自動簽發
- ✅ **全球可見性**：通過 Cloudflare CDN 實現
- ✅ **DNS 記錄未修改**：保持現有 DNS 記錄不變

### 合規檢查

- ✅ 不違反 Google 非營利規範（未修改 DNS）
- ✅ 滿足 Google Ad Grants 技術要求
- ✅ 保持現有基礎設施不變

---

## 🔄 如果 Tunnel 無法自動路由

### 備選方案：使用 Cloudflare 的「僅代理」模式

如果 Tunnel 無法自動路由，可以：

1. **保持 DNS 記錄不變**（A 記錄指向 `220.135.21.74`）
2. **在 Cloudflare Dashboard 啟用「僅代理」模式**
   - 這不會修改 DNS 記錄
   - 只是告訴 Cloudflare 要代理這個 IP
   - SSL 證書會自動簽發

### 操作步驟

1. 前往 Cloudflare Dashboard
2. 選擇「SSL/TLS」→「概覽」
3. 選擇「完整（嚴格）」模式
4. Cloudflare 會自動簽發 SSL 證書

**注意**：這仍然不需要修改 DNS 記錄。

---

## 📝 總結

### ✅ 可以做的

- ✅ 配置 Cloudflare Tunnel
- ✅ 使用 Cloudflare 的代理功能
- ✅ 自動獲得 SSL 證書
- ✅ 實現全球可見性

### ❌ 不需要做的

- ❌ 修改 DNS 記錄（A → CNAME）
- ❌ 刪除現有 DNS 記錄
- ❌ 修改網域設定

### 🎯 結果

- ✅ 符合 Google 非營利規範（未修改 DNS）
- ✅ 滿足技術要求（HTTPS、全球可見）
- ✅ 保持現有基礎設施不變

---

**建立時間**：2026-01-22
