# Squarespace DNS 修改清單

**⚠️ 重要更新**：根據 Cloudflare Dashboard 截圖，DNS 記錄實際上是在 **Cloudflare 管理**，不是在 Squarespace！

**請參考**：`cloudflared/在Cloudflare直接設定DNS.md` - 在 Cloudflare Dashboard（繁體中文介面）直接修改

---

**以下內容僅供參考**（如果 DNS 仍在 Squarespace 管理）：

**網域**：wuchang.life  
**設定位置**：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings

---

## ⚠️ 重要：修改前必須完成

**必須先完成 Cloudflare Tunnel 配置，取得 Tunnel ID**

1. 執行 `cloudflared tunnel login`
2. 執行 `cloudflared tunnel create wuchang-life`
3. 取得 Tunnel ID（例如：`abc123def456789...`）

**取得 Tunnel ID 後，將 `<tunnel-id>` 替換為實際的 Tunnel ID**

---

## 📋 需要修改的記錄

### 1. 根域名（@）- 第一個 A 記錄

**現況**：
```
Host: @
Type: A
Priority: N/A
TTL: 5 mins
Data: 35.185.167.23
```

**修改為**：
```
Host: @
Type: CNAME
Priority: N/A
TTL: 5 mins
Data: <tunnel-id>.cfargotunnel.com
```

**操作**：**編輯** 這個記錄，將 Type 改為 CNAME，Data 改為 `<tunnel-id>.cfargotunnel.com`

---

### 2. 根域名（@）- 第二個 A 記錄

**現況**：
```
Host: @
Type: A
Priority: N/A
TTL: 5 mins
Data: 220.135.21.74
```

**修改為**：**刪除** 這個記錄

**操作**：**刪除** 這個記錄（因為根域名只需要一個 CNAME 記錄）

---

### 3. WWW 子域名（www）

**現況**：
```
Host: www
Type: A
Priority: N/A
TTL: 5 mins
Data: 220.135.21.74
```

**修改為**：
```
Host: www
Type: CNAME
Priority: N/A
TTL: 5 mins
Data: <tunnel-id>.cfargotunnel.com
```

**操作**：**編輯** 這個記錄，將 Type 改為 CNAME，Data 改為 `<tunnel-id>.cfargotunnel.com`

---

## ✅ 不需要修改的記錄（保留）

以下記錄**不需要修改**，請保留：

- `housing` A 記錄 → `104.199.144.93`
- `_acme-challenge` TXT 記錄
- `admin` A 記錄 → `35.201.170.114`
- `@` TXT 記錄 → `OpenAI`
- `butler` A 記錄 → `35.201.170.114`
- `odoo` A 記錄 → `35.185.167.23`
- `_acme-challenge.www` TXT 記錄
- `pm` A 記錄 → `104.199.144.93`
- `shop` A 記錄 → `220.135.21.74`
- `core` A 記錄 → `35.201.170.114`
- `vs` A 記錄 → `35.201.170.114`
- `verify` A 記錄 → `35.201.170.114`
- `hj` A 記錄 → `104.199.144.93`
- `pos` A 記錄 → `104.199.144.93`
- `ft` A 記錄 → `35.201.170.114`
- Google records（MX 和 CNAME）

---

## 📝 修改步驟

### 步驟 1：取得 Tunnel ID

```bash
# 完成 Cloudflare Tunnel 配置後
cloudflared tunnel list

# 記下 Tunnel ID，例如：abc123def456789...
```

### 步驟 2：修改根域名（@）第一個 A 記錄

1. 找到 `@` A 記錄（Data: `35.185.167.23`）
2. 點擊 **編輯**
3. 修改：
   - **Type**：改為 `CNAME`
   - **Data**：改為 `<tunnel-id>.cfargotunnel.com`（替換 `<tunnel-id>` 為實際值）
   - **TTL**：保持 `5 mins` 或改為 `自動`
4. 儲存

### 步驟 3：刪除根域名（@）第二個 A 記錄

1. 找到 `@` A 記錄（Data: `220.135.21.74`）
2. 點擊 **刪除**
3. 確認刪除

### 步驟 4：修改 WWW 子域名

1. 找到 `www` A 記錄（Data: `220.135.21.74`）
2. 點擊 **編輯**
3. 修改：
   - **Type**：改為 `CNAME`
   - **Data**：改為 `<tunnel-id>.cfargotunnel.com`（替換 `<tunnel-id>` 為實際值）
   - **TTL**：保持 `5 mins` 或改為 `自動`
4. 儲存

---

## ⚠️ 注意事項

### 1. Squarespace 可能不支援根域名 CNAME

**如果 Squarespace 不允許根域名（@）使用 CNAME**：

**解決方案**：
- **方案 A（推薦）**：將 DNS 管理轉移到 Cloudflare
  1. 在 Cloudflare 添加網域 `wuchang.life`
  2. Cloudflare 會提供 DNS 伺服器名稱
  3. 在 Squarespace 更新 DNS 伺服器為 Cloudflare 的伺服器
  4. 在 Cloudflare Dashboard 配置 DNS 記錄

- **方案 B**：暫時保留根域名 A 記錄，只修改 www
  - 這樣 `www.wuchang.life` 可以正常使用
  - 但 `wuchang.life` 無法使用 Cloudflare Tunnel

### 2. DNS 傳播時間

- 修改後需要等待 5-10 分鐘讓 DNS 傳播
- 使用 https://www.whatsmydns.net/ 檢查全球傳播狀態

### 3. 驗證設定

修改完成後，驗證：
```bash
# 檢查根域名
nslookup wuchang.life

# 檢查 WWW 子域名
nslookup www.wuchang.life
```

---

## 📋 修改摘要

| 記錄 | 操作 | Type | Data |
|------|------|------|------|
| `@` (第一個) | **編輯** | A → **CNAME** | `35.185.167.23` → **`<tunnel-id>.cfargotunnel.com`** |
| `@` (第二個) | **刪除** | A | `220.135.21.74` |
| `www` | **編輯** | A → **CNAME** | `220.135.21.74` → **`<tunnel-id>.cfargotunnel.com`** |

---

**建立時間**：2026-01-22  
**相關文檔**：
- `cloudflared/MANUAL_SETUP_GUIDE.md` - Cloudflare Tunnel 配置指南
- `SQUARESPACE_DNS_SETUP.md` - Squarespace 完整設定指南
