# 修復無法訪問問題指南

**診斷時間：** 2026-01-20  
**優先目標：** 確保 www.wuchang.life 可以訪問

---

## 🔍 診斷結果

### ✅ 正常狀態

- ✅ **Cloudflare Tunnel 容器運行中**
- ✅ **所有本地服務運行正常**（Caddy, Odoo, WebUI 等）
- ✅ **配置檔案已準備**（包含 www.wuchang.life）
- ✅ **本地服務可訪問**（localhost:80, localhost:8069 等）

### ❌ 發現的問題

1. **Tunnel ID 未設定** - 配置檔案中仍是佔位符 `<tunnel-id>`
2. **憑證檔案不存在** - `cloudflared/credentials.json` 不存在
3. **DNS 路由未設定** - 所有域名無法解析

---

## 🚀 立即修復步驟（按順序執行）

### 步驟 1: 登入 Cloudflare（使用 Docker）

```powershell
docker run --rm -it `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel login
```

**說明：**
- 會開啟瀏覽器讓您登入 Cloudflare
- **選擇網域：wuchang.life**（如果有）或 **wuchang.org.tw**
- 完成後會產生憑證檔案

**檢查憑證：**
```powershell
dir ${env:USERPROFILE}\.cloudflared
```

應該看到 `cert.pem` 檔案。

---

### 步驟 2: 建立命名隧道

```powershell
docker run --rm -it `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel create wuchang-tunnel
```

**重要：** 記下產生的 **Tunnel ID**！

例如：
```
Created tunnel wuchang-tunnel with id abc123-4567-8901-2345-6789abcdef12
```

**記下 ID：** `abc123-4567-8901-2345-6789abcdef12`

**列出所有隧道確認：**
```powershell
docker run --rm `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel list
```

---

### 步驟 3: 設定 DNS 路由（優先：www.wuchang.life）

```powershell
# 首頁（必須，優先執行）
docker run --rm `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.life
```

**驗證 DNS 路由：**
```powershell
docker run --rm `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel route dns list
```

應該看到 `www.wuchang.life` 在列表中。

---

### 步驟 4: 複製憑證檔案

**找到憑證檔案：**
憑證檔案位置：`%USERPROFILE%\.cloudflared\<tunnel-id>.json`

**使用 PowerShell 複製（替換 <tunnel-id> 為步驟 2 記下的實際 ID）：**
```powershell
Copy-Item "${env:USERPROFILE}\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"
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

### 步驟 5: 更新配置檔案

編輯 `cloudflared/config.yml`，將 `<tunnel-id>` 替換為步驟 2 記下的實際 Tunnel ID。

**方法 A: 使用 PowerShell（替換 <實際-tunnel-id>）：**
```powershell
(Get-Content cloudflared\config.yml -Encoding UTF8) -replace '<tunnel-id>', '<實際-tunnel-id>' | Set-Content cloudflared\config.yml -Encoding UTF8
```

**方法 B: 手動編輯：**
打開 `cloudflared/config.yml`，找到：
```yaml
tunnel: <tunnel-id>
```

替換為：
```yaml
tunnel: abc123-4567-8901-2345-6789abcdef12  # 步驟 2 記下的實際 ID
```

**確認配置：**
```yaml
tunnel: abc123-4567-8901-2345-6789abcdef12  # ← 確認已更新
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # 首頁（主域名）
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  
  # ... 其他服務 ...
```

---

### 步驟 6: 重啟 Cloudflare Tunnel 容器

```powershell
docker restart wuchangv510-cloudflared-1
```

**查看日誌確認：**
```powershell
docker logs wuchangv510-cloudflared-1 --tail 20
```

**應該看到：**
- ✅ `Registered tunnel connection`
- ✅ 沒有 `Cannot determine default configuration path` 錯誤
- ✅ 沒有 `Cannot determine default origin certificate path` 錯誤
- ✅ 沒有 `<tunnel-id>` 錯誤

---

### 步驟 7: 等待 DNS 傳播

DNS 設定後，可能需要 **幾分鐘到幾小時** 才能生效。

**建議：**
- 等待 5-10 分鐘
- 然後再測試訪問

---

### 步驟 8: 驗證訪問

**檢查 DNS 解析：**
```powershell
nslookup www.wuchang.life
```

應該解析到 Cloudflare IP（通常是 `104.x.x.x` 或 `172.x.x.x` 範圍）。

**檢查服務訪問：**
```powershell
# HTTP 訪問
curl -I http://www.wuchang.life

# 或直接在瀏覽器訪問
http://www.wuchang.life
```

**應該看到：**
- ✅ HTTP 200 狀態碼
- ✅ 首頁內容正常顯示

**執行診斷腳本：**
```powershell
python diagnose_access_issues.py
```

---

## 📋 快速修復命令（一次執行）

**如果已經有 Cloudflare 帳號，可以依次執行：**

```powershell
# 1. 登入（會開啟瀏覽器）
docker run --rm -it `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel login

# 2. 建立隧道（記下 ID）
docker run --rm -it `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel create wuchang-tunnel

# 3. 設定 DNS 路由（優先：首頁）
docker run --rm `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.life

# 4. 複製憑證（替換 <tunnel-id> 為步驟 2 的實際 ID）
Copy-Item "${env:USERPROFILE}\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"

# 5. 更新配置檔案（替換 <實際-tunnel-id>）
(Get-Content cloudflared\config.yml -Encoding UTF8) -replace '<tunnel-id>', '<實際-tunnel-id>' | Set-Content cloudflared\config.yml -Encoding UTF8

# 6. 重啟容器
docker restart wuchangv510-cloudflared-1

# 7. 等待 5-10 分鐘（DNS 傳播）

# 8. 驗證
nslookup www.wuchang.life
curl -I http://www.wuchang.life
```

---

## ⚠️ 常見問題

### 問題 1: 無法登入 Cloudflare

**可能原因：**
- 瀏覽器未自動開啟
- 網路連接問題

**解決方案：**
- 手動訪問 Cloudflare Dashboard 登入
- 檢查網路連接

### 問題 2: 建立隧道失敗

**可能原因：**
- 隧道名稱已存在
- 權限不足

**解決方案：**
```powershell
# 列出現有隧道
docker run --rm `
  -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
  cloudflare/cloudflared:latest tunnel list

# 如果已存在，使用現有的隧道名稱和 ID
```

### 問題 3: DNS 路由設定失敗

**可能原因：**
- 域名不在 Cloudflare 管理下
- 權限不足

**解決方案：**
- 確認 `wuchang.life` 域名已在 Cloudflare 管理
- 確認使用的 Cloudflare 帳號有管理該域名的權限

### 問題 4: 容器重啟後仍無法訪問

**可能原因：**
- DNS 尚未傳播
- 配置檔案錯誤
- 憑證檔案錯誤

**解決方案：**
1. 等待更長時間（最多可能需要幾小時）
2. 檢查容器日誌是否有錯誤
3. 確認配置檔案和憑證檔案正確

---

## ✅ 完成檢查清單

修復完成後，確認：

- [ ] Cloudflare 帳號已登入
- [ ] 隧道已建立（記下 Tunnel ID）
- [ ] DNS 路由已設定（www.wuchang.life）
- [ ] 憑證檔案已複製（cloudflared/credentials.json）
- [ ] 配置檔案已更新（Tunnel ID）
- [ ] 容器已重啟並正常運行
- [ ] 容器日誌沒有錯誤
- [ ] 等待 DNS 傳播（5-10 分鐘）
- [ ] DNS 解析成功（nslookup www.wuchang.life）
- [ ] 服務可以訪問（http://www.wuchang.life）

---

## 📝 相關檔案

- `diagnose_access_issues.py` - 訪問問題診斷腳本
- `cloudflared/config.yml` - Cloudflare 配置（需更新 Tunnel ID）
- `WWW_WUCHANG_LIFE_PRIORITY_SETUP.md` - 優先設定指南

---

**修復指南產生時間：** 2026-01-20  
**優先目標：** 確保 www.wuchang.life 可以訪問
