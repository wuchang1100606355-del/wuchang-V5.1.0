# 完整 DNS 設定指南 - 為商家和居民提供穩定服務

**設定目標：** 確保商家和居民可以穩定訪問服務  
**重要性：** ⭐⭐⭐⭐⭐ 生產環境關鍵設定

---

## 🎯 設定目標

為以下服務提供穩定的域名訪問：
- **Odoo ERP 系統：** https://app.wuchang.org.tw
- **AI 介面：** https://ai.wuchang.org.tw  
- **容器管理：** https://admin.wuchang.org.tw
- **系統監控：** https://monitor.wuchang.org.tw

---

## 📋 完整設定步驟

### 步驟 1: 安裝 cloudflared

**Windows 安裝：**
1. 下載：https://github.com/cloudflare/cloudflared/releases/latest
2. 下載 `cloudflared-windows-amd64.exe`
3. 重新命名為 `cloudflared.exe`
4. 放到系統 PATH 中（例如：`C:\Windows\System32\`）

**驗證安裝：**
```powershell
cloudflared --version
```

應該看到類似：`cloudflared version 2024.x.x`

---

### 步驟 2: 登入 Cloudflare

```powershell
cloudflared tunnel login
```

**說明：**
- 這會開啟瀏覽器讓您登入 Cloudflare 帳號
- 選擇您要管理的網域：**wuchang.org.tw**
- 完成後會在 `%USERPROFILE%\.cloudflared` 產生憑證檔案

**檢查憑證：**
```powershell
dir %USERPROFILE%\.cloudflared
```

應該看到 `cert.pem` 檔案。

---

### 步驟 3: 建立命名隧道

```powershell
cloudflared tunnel create wuchang-tunnel
```

**重要：** 記下產生的 **Tunnel ID**！

例如：
```
Created tunnel wuchang-tunnel with id abc123-4567-8901-2345-6789abcdef12
```

**記下這個 ID：** `abc123-4567-8901-2345-6789abcdef12`

**列出所有隧道：**
```powershell
cloudflared tunnel list
```

---

### 步驟 4: 配置 DNS 路由

為所有服務配置 DNS 路由：

```powershell
# Odoo ERP 系統
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw

# Open WebUI (AI 介面)
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw

# Portainer (容器管理)
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw

# Uptime Kuma (監控)
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

**驗證 DNS 路由：**
```powershell
cloudflared tunnel route dns list
```

應該看到所有 4 個域名的路由配置。

---

### 步驟 5: 複製憑證檔案

**找到憑證檔案：**
憑證檔案位置：`%USERPROFILE%\.cloudflared\<tunnel-id>.json`

**使用 PowerShell 複製：**
```powershell
# 替換 <tunnel-id> 為步驟 3 記下的實際 ID
Copy-Item "$env:USERPROFILE\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"
```

**或手動複製：**
- 來源：`C:\Users\<您的用戶名>\.cloudflared\<tunnel-id>.json`
- 目標：`C:\wuchang V5.1.0\wuchang-V5.1.0\cloudflared\credentials.json`

**驗證憑證檔案：**
```powershell
Test-Path "cloudflared\credentials.json"
```

應該顯示 `True`。

---

### 步驟 6: 更新配置檔案

編輯 `cloudflared/config.yml`，將 `<tunnel-id>` 替換為步驟 3 記下的實際 Tunnel ID：

```yaml
# Cloudflare Tunnel 配置
# 自動生成/更新時間: 2026-01-20

tunnel: abc123-4567-8901-2345-6789abcdef12  # ← 替換這裡！
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # Odoo ERP 系統
  - hostname: app.wuchang.org.tw
    service: http://wuchangv510-wuchang-web-1:8069
  
  # Open WebUI (AI 介面)
  - hostname: ai.wuchang.org.tw
    service: http://wuchangv510-open-webui-1:8080
  
  # Portainer (容器管理)
  - hostname: admin.wuchang.org.tw
    service: http://wuchangv510-portainer-1:9000
  
  # Uptime Kuma (監控)
  - hostname: monitor.wuchang.org.tw
    service: http://wuchangv510-uptime-kuma-1:3001
  
  # 預設規則（必須放在最後）
  - service: http_status:404
```

**重要提醒：**
- 確保 Tunnel ID 正確（不含 `<` 和 `>`）
- 確保所有服務名稱與實際容器名稱一致

---

### 步驟 7: 重啟 Cloudflare Tunnel 容器

```powershell
docker restart wuchangv510-cloudflared-1
```

**查看容器狀態：**
```powershell
docker ps | Select-String cloudflared
```

**查看容器日誌：**
```powershell
docker logs wuchangv510-cloudflared-1 --tail 30
```

應該看到：
- ✅ `Registered tunnel connection` 
- ✅ 沒有 `Cannot determine default configuration path` 錯誤
- ✅ 沒有 `Cannot determine default origin certificate path` 錯誤

---

### 步驟 8: 驗證設定

**檢查 DNS 解析：**
```powershell
nslookup app.wuchang.org.tw
```

應該解析到 Cloudflare IP（通常是 `104.x.x.x` 或 `172.x.x.x` 範圍）

**檢查所有域名：**
```powershell
nslookup app.wuchang.org.tw
nslookup ai.wuchang.org.tw
nslookup admin.wuchang.org.tw
nslookup monitor.wuchang.org.tw
```

**執行檢查腳本：**
```powershell
python check_dns_status.py
```

應該看到：
- ✅ DNS 解析成功（4/4）
- ✅ 服務連接成功（4/4）

**瀏覽器測試：**
- 訪問：`https://app.wuchang.org.tw`
- 應該可以看到 Odoo ERP 登入頁面

---

## ✅ 驗證清單

完成設定後，請確認以下項目：

- [ ] cloudflared 已安裝並可用
- [ ] Cloudflare 帳號已登入
- [ ] 隧道已建立（wuchang-tunnel）
- [ ] DNS 路由已設定（4 個域名）
- [ ] 憑證檔案已複製到 `cloudflared/credentials.json`
- [ ] 配置檔案中的 Tunnel ID 已更新
- [ ] 容器已重啟並正常運行
- [ ] DNS 解析成功（所有域名）
- [ ] HTTPS 服務可以訪問（所有服務）

---

## 📊 服務訪問地址

設定完成後，商家和居民可以通過以下地址訪問：

| 服務 | 網址 | 說明 |
|-----|------|------|
| Odoo ERP 系統 | https://app.wuchang.org.tw | 主要業務系統 |
| AI 介面 | https://ai.wuchang.org.tw | AI 智能助手 |
| 容器管理 | https://admin.wuchang.org.tw | 系統管理（需登入） |
| 系統監控 | https://monitor.wuchang.org.tw | 服務狀態監控 |

---

## 🔧 疑難排解

### 問題 1: 找不到 cloudflared 命令

**解決方案：**
- 確保 cloudflared 已安裝並在 PATH 中
- 或使用完整路徑執行

### 問題 2: 憑證檔案找不到

**檢查：**
```powershell
dir %USERPROFILE%\.cloudflared
```

**如果沒有檔案：**
- 重新執行 `cloudflared tunnel login`

### 問題 3: DNS 無法解析

**可能原因：**
- DNS 路由未設定
- 等待 DNS 傳播（可能需要幾分鐘到幾小時）

**檢查：**
```powershell
cloudflared tunnel route dns list
```

**如果沒有路由：**
- 重新執行步驟 4 的 DNS 路由設定

### 問題 4: 服務無法連接

**檢查步驟：**
1. 容器是否運行：`docker ps | Select-String cloudflared`
2. 容器日誌：`docker logs wuchangv510-cloudflared-1`
3. 配置檔案中的服務名稱是否正確

**常見錯誤：**
- `service: http://wuchang-web:8069` ❌（錯誤的容器名稱）
- `service: http://wuchangv510-wuchang-web-1:8069` ✅（正確的容器名稱）

---

## 🎯 後續維護

### 定期檢查

**每日檢查：**
```powershell
python check_dns_status.py
```

**每週檢查：**
```powershell
docker logs wuchangv510-cloudflared-1 --tail 50
```

**每月檢查：**
- 驗證所有服務可以訪問
- 檢查 DNS 解析是否正常
- 檢查容器運行狀態

### 監控建議

**建議設定：**
1. Uptime Kuma 監控所有服務
2. 郵件或簡訊告警（服務中斷時通知）
3. 定期備份配置檔案

**監控項目：**
- DNS 解析狀態
- HTTPS 連接狀態
- 容器運行狀態
- 服務響應時間

---

## 📝 重要提醒

1. **生產環境設定**
   - 這是生產環境關鍵設定
   - 設定完成後請妥善保管配置檔案
   - 建議定期備份 `cloudflared/` 目錄

2. **服務可用性**
   - 商家和居民依賴這些服務
   - 請確保服務穩定運行
   - 設定監控告警及時發現問題

3. **安全設定**
   - 建議為管理界面（admin.wuchang.org.tw）設定訪問密碼
   - 定期更新密碼和憑證
   - 監控異常訪問

---

## 🔗 相關資源

- [Cloudflare Tunnel 文件](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [DNS 路由設定](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/routes/)
- 檢查腳本：`check_dns_status.py`
- 修復腳本：`fix_dns_configuration.py`
- 設定腳本：`setup_dns_complete.py`

---

**設定指南產生時間：** 2026-01-20  
**目的：** 為商家和居民提供穩定可靠的服務可見度  
**重要性：** ⭐⭐⭐⭐⭐ 生產環境關鍵設定
