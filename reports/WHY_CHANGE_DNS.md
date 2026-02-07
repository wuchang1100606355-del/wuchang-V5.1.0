# 為什麼要在 Squarespace 修改 DNS 設定？

---

## 🤔 為什麼要改 DNS？

### 現況問題

**目前的 DNS 設定**：
- `wuchang.life` → 指向 `220.135.21.74`（直接指向 IP）
- `www.wuchang.life` → 指向 `220.135.21.74`（直接指向 IP）

**問題**：
1. ❌ 直接指向 IP，無法使用 Cloudflare Tunnel
2. ❌ 無法自動獲得 SSL 證書
3. ❌ 無法全球加速
4. ❌ 不符合 Google 非營利組織合規要求（必須使用 HTTPS）

---

## ✅ 修改後的好處

### 修改為 CNAME 指向 Cloudflare Tunnel

**新的 DNS 設定**：
- `wuchang.life` → 指向 `<tunnel-id>.cfargotunnel.com`（CNAME）
- `www.wuchang.life` → 指向 `<tunnel-id>.cfargotunnel.com`（CNAME）

**好處**：
1. ✅ 可以使用 Cloudflare Tunnel（全球可見）
2. ✅ 自動獲得免費 SSL 證書（HTTPS）
3. ✅ 全球 CDN 加速
4. ✅ 符合 Google 非營利組織合規要求
5. ✅ 不需要開放防火牆端口

---

## 📍 為什麼要在 Squarespace 改？

### DNS 設定的位置

**DNS 設定必須在網域商那邊改**，因為：

1. **DNS 記錄由網域商管理**
   - 您的網域 `wuchang.life` 是在 Squarespace 註冊的
   - DNS 記錄的修改權限在 Squarespace
   - 只有網域商可以修改 DNS 記錄

2. **DNS 的工作原理**
   ```
   用戶訪問 wuchang.life
        ↓
   查詢 DNS 伺服器（由網域商管理）
        ↓
   返回 IP 地址或 CNAME 目標
        ↓
   用戶連接到對應的伺服器
   ```

3. **必須在源頭修改**
   - 就像您要改地址，必須去戶政事務所改
   - DNS 記錄要改，必須去網域商（Squarespace）改

---

## 🔄 修改流程說明

### 現在的流程

```
用戶 → 查詢 DNS → Squarespace DNS 伺服器
                ↓
           返回 220.135.21.74（A 記錄）
                ↓
           用戶連接到 220.135.21.74
                ↓
           但端口 443 無法連接（沒有 SSL 證書）
```

### 修改後的流程

```
用戶 → 查詢 DNS → Squarespace DNS 伺服器
                ↓
           返回 <tunnel-id>.cfargotunnel.com（CNAME）
                ↓
           用戶連接到 Cloudflare
                ↓
           Cloudflare Tunnel → 您的本地伺服器
                ↓
           自動 SSL 證書，全球可見
```

---

## 💡 為什麼不能在其他地方改？

### 選項 1：在 Cloudflare 改 ❌ 不行

**為什麼不行**：
- 您的網域 DNS 管理權限在 Squarespace
- Cloudflare 沒有權限修改 Squarespace 的 DNS 記錄
- 必須在網域商（Squarespace）那邊改

### 選項 2：在本地改 ❌ 不行

**為什麼不行**：
- 本地改的 DNS 只影響您的電腦
- 其他用戶還是會查詢 Squarespace 的 DNS
- 必須在源頭（Squarespace）改

### 選項 3：在 Squarespace 改 ✅ 必須

**為什麼必須**：
- DNS 記錄由 Squarespace 管理
- 只有 Squarespace 可以修改 DNS 記錄
- 這是唯一正確的地方

---

## 🎯 簡單來說

**就像改地址**：
- 您的地址登記在戶政事務所
- 要改地址，必須去戶政事務所改
- 不能在其他地方改

**DNS 也是一樣**：
- 您的 DNS 記錄登記在 Squarespace
- 要改 DNS，必須在 Squarespace 改
- 不能在其他地方改

---

## 📋 必須修改的記錄

### 為什麼要改這 3 筆記錄？

1. **`@` 第一個 A 記錄**（35.185.167.23）
   - 改為 CNAME → 指向 Cloudflare Tunnel
   - 這樣 `wuchang.life` 才能使用 Tunnel

2. **`@` 第二個 A 記錄**（220.135.21.74）
   - 刪除 → 因為根域名只需要一個記錄
   - 避免 DNS 解析不確定

3. **`www` A 記錄**（220.135.21.74）
   - 改為 CNAME → 指向 Cloudflare Tunnel
   - 這樣 `www.wuchang.life` 才能使用 Tunnel

---

## ✅ 總結

**為什麼要在 Squarespace 改**：
1. DNS 記錄由 Squarespace 管理
2. 只有網域商可以修改 DNS 記錄
3. 這是唯一正確的地方

**為什麼要改**：
1. 使用 Cloudflare Tunnel（全球可見）
2. 自動獲得 SSL 證書（HTTPS）
3. 符合 Google 非營利組織合規要求

**如果不想在 Squarespace 改**：
- 可以將 DNS 管理轉移到 Cloudflare
- 但還是需要在 Squarespace 更新 DNS 伺服器名稱
- 詳細步驟請參考：`CLOUDFLARE_DNS_TRANSFER_GUIDE.md`

---

**建立時間**：2026-01-22
