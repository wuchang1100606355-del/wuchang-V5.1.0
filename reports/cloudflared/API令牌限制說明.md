# API 令牌限制說明

**API 令牌**：`PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs`

---

## ⚠️ 重要限制

### 1. IP 地址限制

**只允許從以下 IP 使用**：
- `220.135.21.74`（您的固定 IP）

**影響**：
- ✅ 從您的伺服器（220.135.21.74）可以使用
- ❌ 從其他 IP 無法使用
- ❌ 從本地電腦可能無法使用（除非透過 VPN 或代理）

### 2. 權限限制

**目前權限**：
- `All users - API Tokens:Edit`

**問題**：
- ⚠️ 這個權限只能**管理其他 API 令牌**，不能管理 DNS 或 Tunnel
- ❌ 無法使用此令牌來設定 DNS 記錄
- ❌ 無法使用此令牌來建立或管理 Tunnel

### 3. 時間限制

**有效期**：
- 開始日期：2026年1月22日
- 結束日期：2026年2月1日
- **剩餘時間**：約 10 天

**影響**：
- ⚠️ 2月1日後此令牌將失效
- 需要在此之前完成設定，或申請新的令牌

---

## 🔧 解決方案

### 方案一：申請新的 API 令牌（推薦）

**需要的權限**：
1. **Zone DNS:Edit** - 管理 DNS 記錄
2. **Account Cloudflare Tunnel:Edit** - 管理 Tunnel
3. **Zone:Read** - 讀取網域資訊

**申請步驟**：
1. 登入 Cloudflare Dashboard
2. 前往「My Profile」→「API Tokens」
3. 建立新令牌，選擇以下權限：
   - Zone DNS:Edit
   - Account Cloudflare Tunnel:Edit
   - Zone:Read
4. IP 過濾：設定為 `220.135.21.74`（或留空允許所有 IP）
5. 有效期：設定較長時間（例如 1 年）

### 方案二：使用 cloudflared CLI（不需要 API 令牌）

**優點**：
- ✅ 不需要 API 令牌
- ✅ 可以直接建立和管理 Tunnel
- ✅ 更簡單直接

**步驟**：
```powershell
# 進入容器
docker exec -it wuchangv510-cloudflared-1 sh

# 登入（會開啟瀏覽器）
cloudflared tunnel login

# 建立 Tunnel
cloudflared tunnel create wuchang-life

# 取得 Tunnel ID
cloudflared tunnel list

exit
```

### 方案三：手動設定 DNS（如果 DNS 在 Squarespace）

**如果 DNS 仍在 Squarespace 管理**：
- 不需要 API 令牌
- 直接在 Squarespace 手動設定 DNS 記錄
- 參考：`SQUARESPACE_DNS_CHANGES.md`

---

## 📋 當前 API 令牌可用功能

**可以使用的功能**：
- ✅ 查詢帳號資訊（如果權限足夠）
- ❌ 管理 DNS 記錄（權限不足）
- ❌ 管理 Tunnel（權限不足）
- ❌ 建立新的 API 令牌（可以，但這不是我們需要的）

---

## 🎯 建議

**立即行動**：
1. **使用 cloudflared CLI 建立 Tunnel**（不需要 API 令牌）
2. **在 Squarespace 手動設定 DNS**（如果 DNS 在 Squarespace）
3. **或申請新的 API 令牌**（如果 DNS 在 Cloudflare 且需要自動化）

**長期方案**：
- 申請具有正確權限的 API 令牌
- 設定較長的有效期
- 考慮是否需要 IP 限制

---

## 📝 更新記錄

- 2026-01-22：記錄 API 令牌限制資訊
