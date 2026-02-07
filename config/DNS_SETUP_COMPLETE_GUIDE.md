# 完整 DNS 設定指南 - 為商家和居民提供穩定服務

**設定目標：** 確保商家和居民可以穩定訪問服務

---

## 📋 設定步驟

### 步驟 1: 安裝 cloudflared

**Windows 安裝：**
1. 下載：https://github.com/cloudflare/cloudflared/releases/latest
2. 解壓縮 `cloudflared-windows-amd64.exe`
3. 重新命名為 `cloudflared.exe`
4. 放到 PATH 中（例如：`C:\Windows\System32\`）

**驗證安裝：**
```powershell
cloudflared --version
```

---

### 步驟 2: 登入 Cloudflare

```powershell
cloudflared tunnel login
```

**說明：**
- 這會開啟瀏覽器讓您登入 Cloudflare
- 選擇您要管理的網域（wuchang.org.tw）
- 完成後會在 `%USERPROFILE%\.cloudflared` 產生憑證

**檢查憑證：**
```powershell
dir %USERPROFILE%\.cloudflared
```

---

### 步驟 3: 建立命名隧道

```powershell
cloudflared tunnel create wuchang-tunnel
```

**重要：** 記下產生的 **Tunnel ID**（例如：`abc123-4567-8901-2345-6789abcdef12`）

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

---

### 步驟 5: 複製憑證檔案

**找到憑證檔案：**
憑證檔案位置：`%USERPROFILE%\.cloudflared\<tunnel-id>.json`

**複製到專案目錄：**
```powershell
# 替換 <tunnel-id> 為步驟 3 記下的實際 ID
Copy-Item "$env:USERPROFILE\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"
```

或手動複製：
- 來源：`C:\Users\<您的用戶名>\.cloudflared\<tunnel-id>.json`
- 目標：`C:\wuchang V5.1.0\wuchang-V5.1.0\cloudflared\credentials.json`

**驗證憑證檔案：**
```powershell
Test-Path "cloudflared\credentials.json"
```

---

### 步驟 6: 更新配置檔案

編輯 `cloudflared/config.yml`，將 `<tunnel-id>` 替換為步驟 3 記下的實際 Tunnel ID：

```yaml
tunnel: abc123-4567-8901-2345-6789abcdef12  # 替換這裡
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
docker logs wuchangv510-cloudflared-1 --tail 20
```

應該看到：
- `Registered tunnel connection` ✅
- 沒有 `Cannot determine default configuration path` 錯誤

---

### 步驟 8: 驗證設定

**檢查 DNS 解析：**
```powershell
nslookup app.wuchang.org.tw
```

應該解析到 Cloudflare IP（通常是 `104.x.x.x` 或 `172.x.x.x` 範圍）

**檢查服務連接：**
- 瀏覽器訪問：`https://app.wuchang.org.tw`
- 應該可以看到 Odoo ERP 登入頁面

**執行檢查腳本：**
```powershell
python check_dns_status.py
```

---

## ✅ 驗證清單

完成設定後，確認：

- [ ] cloudflared 已安裝並可用
- [ ] Cloudflare 帳號已登入
- [ ] 隧道已建立（wuchang-tunnel）
- [ ] DNS 路由已設定（4 個域名）
- [ ] 憑證檔案已複製到 `cloudflared/credentials.json`
- [ ] 配置檔案中的 Tunnel ID 已更新
- [ ] 容器已重啟並正常運行
- [ ] DNS 解析成功
- [ ] HTTPS 服務可以訪問

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

### 問題 4: 服務無法連接

**檢查：**
1. 容器是否運行：`docker ps | Select-String cloudflared`
2. 容器日誌：`docker logs wuchangv510-cloudflared-1`
3. 配置檔案中的服務名稱是否正確

---

## 📊 服務訪問地址

設定完成後，商家和居民可以通過以下地址訪問：

- **Odoo ERP 系統：** https://app.wuchang.org.tw
- **AI 介面：** https://ai.wuchang.org.tw
- **容器管理：** https://admin.wuchang.org.tw
- **系統監控：** https://monitor.wuchang.org.tw

---

## 🎯 後續維護

### 定期檢查

1. **每日檢查：**
   - 執行 `python check_dns_status.py` 檢查狀態

2. **每週檢查：**
   - 查看容器日誌：`docker logs wuchangv510-cloudflared-1 --tail 50`

3. **每月檢查：**
   - 驗證所有服務可以訪問
   - 檢查 DNS 解析是否正常

### 監控建議

- 設定 Uptime Kuma 監控所有服務
- 設定郵件或簡訊告警
- 定期備份配置檔案

---

**設定指南產生時間：** 2026-01-20
**目的：** 為商家和居民提供穩定可靠的服務可見度
