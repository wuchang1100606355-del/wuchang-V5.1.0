# DNS 配置修復指南

**更新時間：** 2026-01-20

## ✅ 已完成的修復

### 1. 更新配置檔案

- ✅ 已更新 `cloudflared/config.yml`
- ✅ 修正容器名稱為實際運行中的容器名稱
- ✅ 新增所有四個域名的配置

---

## 🔧 需要手動執行的步驟

### 步驟 1: 安裝 cloudflared（如果還沒有）

**選項 A: Windows 安裝**
1. 下載：https://github.com/cloudflare/cloudflared/releases
2. 解壓縮並將 `cloudflared.exe` 放到 PATH 中

**選項 B: 使用 Docker（推薦）**
```bash
docker pull cloudflare/cloudflared:latest
```

### 步驟 2: 登入 Cloudflare

```bash
cloudflared tunnel login
```

這會：
- 開啟瀏覽器讓您登入 Cloudflare
- 在 `%USERPROFILE%\.cloudflared` 目錄產生憑證檔案

### 步驟 3: 建立命名隧道

```bash
cloudflared tunnel create wuchang-tunnel
```

**記下產生的 Tunnel ID**（例如：`abc123-4567-8901-2345-6789abcdef12`）

### 步驟 4: 配置 DNS 路由

```bash
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

### 步驟 5: 複製憑證檔案

將憑證檔案複製到專案目錄：

```powershell
# 替換 <tunnel-id> 為步驟 3 記下的實際 ID
Copy-Item "$env:USERPROFILE\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"
```

或手動複製：
- 來源：`C:\Users\<您的用戶名>\.cloudflared\<tunnel-id>.json`
- 目標：`C:\wuchang V5.1.0\wuchang-V5.1.0\cloudflared\credentials.json`

### 步驟 6: 更新配置檔案中的 Tunnel ID

編輯 `cloudflared/config.yml`，將 `<tunnel-id>` 替換為步驟 3 記下的實際 Tunnel ID：

```yaml
tunnel: abc123-4567-8901-2345-6789abcdef12  # 替換這裡
credentials-file: /etc/cloudflared/credentials.json
```

### 步驟 7: 重啟 Cloudflare Tunnel 容器

```bash
docker restart wuchangv510-cloudflared-1
```

或使用 Docker Compose：

```bash
docker-compose -f docker-compose.cloud.yml restart cloudflared
```

### 步驟 8: 驗證修復

執行檢查腳本：

```bash
python check_dns_status.py
```

應該看到：
- ✅ DNS 解析成功
- ✅ 服務連接成功

---

## 📋 快速修復命令（一行執行）

如果您已經有 Cloudflare 帳號，可以依次執行：

```powershell
# 1. 登入（會開啟瀏覽器）
cloudflared tunnel login

# 2. 建立隧道（記下 ID）
cloudflared tunnel create wuchang-tunnel

# 3. 配置 DNS（替換 wuchang-tunnel 為實際隧道名稱）
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw

# 4. 複製憑證（替換 <tunnel-id> 為實際 ID）
Copy-Item "$env:USERPROFILE\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"

# 5. 編輯 config.yml 更新 Tunnel ID（手動編輯）

# 6. 重啟容器
docker restart wuchangv510-cloudflared-1

# 7. 驗證
python check_dns_status.py
```

---

## 🔍 驗證清單

修復完成後，確認：

- [ ] `cloudflared/credentials.json` 檔案存在
- [ ] `cloudflared/config.yml` 中的 Tunnel ID 已更新（不再是 `<tunnel-id>`）
- [ ] DNS 路由已設定（使用 `cloudflared tunnel route dns list` 檢查）
- [ ] 容器日誌顯示正常連接（`docker logs wuchangv510-cloudflared-1`）
- [ ] 域名可以解析（使用 `nslookup app.wuchang.org.tw`）
- [ ] HTTPS 服務可以訪問（在瀏覽器訪問 `https://app.wuchang.org.tw`）

---

## ⚠️ 常見問題

### 問題 1: 找不到 cloudflared 命令

**解決方案：**
- 確保 cloudflared 已安裝並在 PATH 中
- 或使用 Docker：`docker run --rm cloudflare/cloudflared tunnel login`

### 問題 2: 憑證檔案找不到

**檢查位置：**
- Windows: `C:\Users\<用戶名>\.cloudflared\`
- 使用 `dir %USERPROFILE%\.cloudflared` 查看

### 問題 3: DNS 無法解析

**可能原因：**
- DNS 路由未設定
- 等待 DNS 傳播（可能需要幾分鐘到幾小時）

**檢查：**
```bash
cloudflared tunnel route dns list
```

### 問題 4: 服務無法連接

**檢查：**
1. 容器是否運行：`docker ps | grep cloudflared`
2. 容器日誌：`docker logs wuchangv510-cloudflared-1`
3. 配置檔案中的服務名稱是否正確

---

## 📝 配置檔案說明

### 容器名稱對應

配置檔案中的服務名稱對應實際容器名稱：

| 配置中的服務 | 實際容器名稱 |
|------------|------------|
| `wuchangv510-wuchang-web-1:8069` | Odoo ERP |
| `wuchangv510-open-webui-1:8080` | Open WebUI |
| `wuchangv510-portainer-1:9000` | Portainer |
| `wuchangv510-uptime-kuma-1:3001` | Uptime Kuma |

### 域名對應

| 域名 | 服務 |
|-----|-----|
| `app.wuchang.org.tw` | Odoo ERP 系統 |
| `ai.wuchang.org.tw` | Open WebUI (AI 介面) |
| `admin.wuchang.org.tw` | Portainer (容器管理) |
| `monitor.wuchang.org.tw` | Uptime Kuma (監控) |

---

## 🔗 相關資源

- [Cloudflare Tunnel 文件](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [DNS 路由設定](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/routes/)
- 檢查腳本：`check_dns_status.py`
- 修復腳本：`fix_dns_configuration.py`

---

**修復指南產生時間：** 2026-01-20
