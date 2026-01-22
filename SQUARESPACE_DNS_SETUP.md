# Squarespace DNS 設定指南

**網域商**：Squarespace  
**網域**：wuchang.life  
**設定位置**：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings

---

## ⚠️ 重要：設定前必須完成

在設定 DNS 之前，您必須先完成 Cloudflare Tunnel 配置，以取得 **Tunnel ID**。

### 步驟 1：完成 Cloudflare Tunnel 配置

請按照 `cloudflared/MANUAL_SETUP_GUIDE.md` 的步驟：

1. **登入 Cloudflare**
   ```bash
   cloudflared tunnel login
   ```

2. **建立或選擇 Tunnel**
   ```bash
   cloudflared tunnel create wuchang-life
   ```
   或使用現有 Tunnel：
   ```bash
   cloudflared tunnel list
   ```

3. **取得 Tunnel ID**
   - 從命令輸出中取得，例如：`abc123def456789...`
   - 或從 Cloudflare Dashboard → Zero Trust → Networks → Tunnels 查看

4. **配置 credentials.json**
   - 參考 `cloudflared/credentials.json.template`
   - 填入 AccountTag, TunnelSecret, TunnelID

5. **更新 config.yml**
   - 參考 `cloudflared/config.yml.template`
   - 將 `<tunnel-id>` 替換為實際的 Tunnel ID

---

## 📋 Squarespace DNS 設定步驟

### 步驟 2：在 Squarespace 設定 DNS

1. **訪問 DNS 設定頁面**
   - 直接連結：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings
   - 或登入 Squarespace → 網域 → wuchang.life → DNS 設定

2. **配置根域名（wuchang.life）**

   **如果 Squarespace 支援根域名 CNAME**：
   ```
   類型：CNAME
   主機名稱：@
   指向/目標：<tunnel-id>.cfargotunnel.com
   TTL：自動（或 300）
   ```

   **如果 Squarespace 不支援根域名 CNAME**：
   - 需要將 DNS 管理轉移到 Cloudflare（推薦）
   - 或使用 A 記錄（不推薦，無法使用 Tunnel）

3. **配置 WWW 子域名（www.wuchang.life）**
   ```
   類型：CNAME
   主機名稱：www
   指向/目標：<tunnel-id>.cfargotunnel.com
   TTL：自動（或 300）
   ```

4. **儲存設定**
   - 點擊「儲存」或「更新」
   - 等待 DNS 傳播（通常 5-10 分鐘）

---

## 🔍 如何取得 Tunnel ID

### 方法 1：從命令列取得

```bash
# 列出所有 Tunnel
cloudflared tunnel list

# 輸出範例：
# ID                                   NAME            CREATED
# abc123def456789...                   wuchang-life    2026-01-22T...
```

### 方法 2：從 Cloudflare Dashboard 取得

1. 訪問：https://one.dash.cloudflare.com/
2. 進入 **Zero Trust** → **Networks** → **Tunnels**
3. 找到您的 Tunnel（例如：`wuchang-life`）
4. 點擊 Tunnel 名稱
5. 在詳細資訊中查看 **Tunnel ID**

---

## 📝 DNS 設定範本（待填入）

**請將 `<tunnel-id>` 替換為實際的 Tunnel ID**

### 根域名設定
```
類型：CNAME
主機名稱：@
指向/目標：[待填入] <tunnel-id>.cfargotunnel.com
TTL：自動
```

### WWW 子域名設定
```
類型：CNAME
主機名稱：www
指向/目標：[待填入] <tunnel-id>.cfargotunnel.com
TTL：自動
```

**範例**（假設 Tunnel ID 是 `abc123def456789`）：
```
類型：CNAME
主機名稱：@
指向/目標：abc123def456789.cfargotunnel.com
TTL：自動
```

---

## ⚠️ Squarespace 特殊注意事項

### 1. 根域名 CNAME 限制

**問題**：Squarespace 可能不支援根域名（@）使用 CNAME

**解決方案**：
- **方案 A（推薦）**：將 DNS 管理轉移到 Cloudflare
  1. 在 Cloudflare 添加網域 `wuchang.life`
  2. Cloudflare 會提供 DNS 伺服器名稱
  3. 在 Squarespace 更新 DNS 伺服器為 Cloudflare 的伺服器
  4. 在 Cloudflare Dashboard 配置 DNS 記錄

- **方案 B**：使用 A 記錄（不推薦）
  - 無法使用 Cloudflare Tunnel
  - 需要直接指向 IP 地址
  - 無法獲得自動 SSL 證書

### 2. DNS 傳播時間

- **Squarespace**：通常 5-10 分鐘
- **全球傳播**：最多 24-48 小時
- **驗證方法**：使用 https://www.whatsmydns.net/ 檢查

### 3. 現有記錄處理

**在修改前**：
- [ ] 備份現有 DNS 記錄（截圖或記錄）
- [ ] 確認哪些記錄需要保留（如 MX 記錄、其他子網域）
- [ ] 確認哪些記錄需要修改（根域名和 www）

**修改時**：
- [ ] 先添加新記錄
- [ ] 驗證新記錄正常
- [ ] 再刪除或修改舊記錄

---

## ✅ 設定檢查清單

### 設定前
- [ ] 完成 Cloudflare Tunnel 登入
- [ ] 建立或選擇 Tunnel
- [ ] 取得 Tunnel ID
- [ ] 配置 credentials.json
- [ ] 更新 config.yml
- [ ] 備份現有 DNS 記錄

### 設定中
- [ ] 訪問 Squarespace DNS 設定頁面
- [ ] 配置根域名 CNAME（如果支援）
- [ ] 配置 WWW 子域名 CNAME
- [ ] 確認記錄值正確（包含 `.cfargotunnel.com`）
- [ ] 儲存設定

### 設定後
- [ ] 等待 DNS 傳播（5-10 分鐘）
- [ ] 使用 `nslookup wuchang.life` 驗證
- [ ] 使用 `nslookup www.wuchang.life` 驗證
- [ ] 使用 https://www.whatsmydns.net/ 檢查全球傳播
- [ ] 測試 `https://wuchang.life` 可訪問
- [ ] 測試 `https://www.wuchang.life` 可訪問
- [ ] 確認 SSL 證書有效

---

## 🔗 相關資源

- **Squarespace DNS 設定**：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings
- **Cloudflare Tunnel 手動配置指南**：`cloudflared/MANUAL_SETUP_GUIDE.md`
- **DNS 傳播檢查**：https://www.whatsmydns.net/
- **Cloudflare Dashboard**：https://dash.cloudflare.com/

---

## 📌 重要提醒

1. **必須先完成 Cloudflare Tunnel 配置**，才能取得 Tunnel ID
2. **Squarespace 可能不支援根域名 CNAME**，建議將 DNS 管理轉移到 Cloudflare
3. **DNS 傳播需要時間**，設定後請耐心等待
4. **備份現有記錄**，避免遺失重要設定

---

**建立時間**：2026-01-22  
**網域商**：Squarespace  
**網域**：wuchang.life
