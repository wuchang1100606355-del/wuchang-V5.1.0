# 使用 Cloudflare API 令牌設定指南

**API 令牌**：`PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs`

**⚠️ 重要限制**：此 API 令牌權限為 `API Tokens:Edit`，**無法管理 DNS 或 Tunnel**。請參考 `API令牌限制說明.md`。

---

## 📋 API 令牌的用途

**當前令牌限制**：
- ❌ **無法管理 DNS 記錄**（權限不足）
- ❌ **無法管理 Tunnel**（權限不足）
- ✅ **只能管理其他 API 令牌**（不是我們需要的）

**需要的權限**：
1. **Zone DNS:Edit** - 管理 DNS 記錄
2. **Account Cloudflare Tunnel:Edit** - 管理 Tunnel
3. **Zone:Read** - 讀取網域資訊

**其他限制**：
- IP 限制：只允許從 `220.135.21.74` 使用
- 有效期：到 2026年2月1日（約 10 天）

---

## 🚀 方法一：使用 API 令牌自動設定 DNS（推薦）

**優點**：完全自動化，不需要手動操作 Squarespace

### 步驟 1：取得 Tunnel ID

**必須先建立 Tunnel**（使用 cloudflared CLI）：

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

### 步驟 2：使用 API 令牌自動設定 DNS

**執行以下 Python 腳本**：

```powershell
python cloudflared/setup_dns_with_api_token.py
```

這個腳本會：
- 自動查詢您的帳號資訊
- 自動設定 DNS 記錄（CNAME）
- 不需要手動操作 Squarespace

---

## 🚀 方法二：手動設定（如果 API 令牌權限不足）

### 步驟 1：取得 Tunnel ID

同方法一的步驟 1

### 步驟 2：在 Squarespace 手動設定 DNS

**設定位置**：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings

**需要修改的記錄**：

1. **根域名（@）第一個**：
   - 編輯 → Type 改為 `CNAME`
   - Data 改為 `<Tunnel ID>.cfargotunnel.com`

2. **根域名（@）第二個**：
   - 刪除

3. **WWW 子域名**：
   - 編輯 → Type 改為 `CNAME`
   - Data 改為 `<Tunnel ID>.cfargotunnel.com`

---

## 🔧 使用 API 令牌查詢資訊

**執行查詢腳本**：

```powershell
python cloudflared/query_with_api_token.py
```

這會顯示：
- 帳號資訊
- 現有 Tunnel 列表
- DNS 記錄狀態

---

## 📝 建立 DNS 自動設定腳本

讓我為您建立一個使用 API 令牌自動設定 DNS 的腳本。
