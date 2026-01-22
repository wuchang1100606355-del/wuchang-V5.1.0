# Tunnel ID 是什麼？

---

## 📖 什麼是 Tunnel ID？

**Tunnel ID** 是 Cloudflare 為每個 Tunnel 分配的唯一識別碼。

### 簡單比喻

就像：
- **身份證字號**：每個人都有一個唯一的身分證字號
- **Tunnel ID**：每個 Tunnel 都有一個唯一的 ID

### 實際用途

Tunnel ID 用來：
1. **識別您的 Tunnel**：告訴 Cloudflare 要使用哪個 Tunnel
2. **DNS 設定**：DNS 記錄需要指向 `<Tunnel ID>.cfargotunnel.com`
3. **配置檔案**：`config.yml` 中需要填入 Tunnel ID

---

## 🔍 Tunnel ID 長什麼樣子？

Tunnel ID 是一個**長字串**，例如：
```
abc123def4567890123456789012345678
```

或
```
PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs
```

**特徵**：
- 通常 32-64 個字元
- 包含英文字母和數字
- 每個 Tunnel 的 ID 都不同

---

## 🚀 如何取得 Tunnel ID？

### 方法一：建立新 Tunnel（推薦）

**步驟**：

1. **進入容器**：
   ```powershell
   docker exec -it wuchangv510-cloudflared-1 sh
   ```

2. **登入 Cloudflare**（會開啟瀏覽器，點擊授權）：
   ```bash
   cloudflared tunnel login
   ```
   - 這會自動開啟瀏覽器
   - 點擊「Authorize」或「授權」按鈕
   - 授權後可以關閉瀏覽器

3. **建立 Tunnel**：
   ```bash
   cloudflared tunnel create wuchang-life
   ```
   - 這會顯示類似以下的訊息：
     ```
     Created tunnel wuchang-life with id abc123def4567890123456789012345678
     ```
   - **`abc123def4567890123456789012345678` 就是 Tunnel ID**

4. **退出容器**：
   ```bash
   exit
   ```

---

### 方法二：查看現有 Tunnel

**如果您已經建立過 Tunnel**：

```powershell
docker exec -it wuchangv510-cloudflared-1 sh
cloudflared tunnel list
exit
```

這會顯示所有現有的 Tunnel 及其 ID，例如：
```
ID                                   NAME           CREATED
abc123def4567890123456789012345678   wuchang-life   2026-01-22T10:00:00Z
```

---

## 📝 如何使用 Tunnel ID？

### 1. 填入 config.yml

編輯 `cloudflared/config.yml`：

```yaml
tunnel: abc123def4567890123456789012345678  # 您的 Tunnel ID
```

### 2. 設定 DNS 記錄

在 Cloudflare Dashboard 設定 DNS 記錄：

- **類型**：`CNAME`
- **名稱**：`wuchang.life` 或 `www`
- **目標**：`abc123def4567890123456789012345678.cfargotunnel.com`

**完整格式**：`<Tunnel ID>.cfargotunnel.com`

---

## ⚠️ 重要注意事項

### 1. Tunnel ID 是唯一的

- 每個 Tunnel 都有不同的 ID
- 不能使用別人的 Tunnel ID
- 建立新 Tunnel 會產生新的 ID

### 2. Tunnel ID 不會改變

- 一旦建立，Tunnel ID 就不會改變
- 即使重新命名 Tunnel，ID 也不會變

### 3. 必須先建立 Tunnel

- 在設定 DNS 之前，必須先建立 Tunnel 並取得 ID
- 沒有 Tunnel ID 就無法設定 DNS

---

## 🔄 完整流程範例

### 步驟 1：建立 Tunnel 並取得 ID

```powershell
docker exec -it wuchangv510-cloudflared-1 sh
cloudflared tunnel login
cloudflared tunnel create wuchang-life
# 顯示：Created tunnel wuchang-life with id abc123def4567890123456789012345678
exit
```

**記下 ID**：`abc123def4567890123456789012345678`

### 步驟 2：更新 config.yml

```yaml
tunnel: abc123def4567890123456789012345678
```

### 步驟 3：設定 DNS

在 Cloudflare Dashboard：
- `wuchang.life` → `abc123def4567890123456789012345678.cfargotunnel.com`
- `www.wuchang.life` → `abc123def4567890123456789012345678.cfargotunnel.com`

---

## ❓ 常見問題

### Q: Tunnel ID 和 API 令牌一樣嗎？

**A: 不一樣**！
- **API 令牌**：用來授權 API 操作（例如：`PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs`）
- **Tunnel ID**：用來識別特定的 Tunnel（例如：`abc123def4567890123456789012345678`）

### Q: 可以自己設定 Tunnel ID 嗎？

**A: 不行**。Tunnel ID 是由 Cloudflare 自動產生的，無法自行設定。

### Q: 忘記 Tunnel ID 怎麼辦？

**A: 使用 `cloudflared tunnel list` 查看所有 Tunnel 及其 ID**。

---

## 📋 總結

- **Tunnel ID** = Cloudflare 為每個 Tunnel 分配的唯一識別碼
- **取得方式** = 使用 `cloudflared tunnel create` 建立 Tunnel
- **用途** = 填入 `config.yml` 和設定 DNS 記錄
- **格式** = DNS 記錄格式：`<Tunnel ID>.cfargotunnel.com`

---

**建立時間**：2026-01-22
