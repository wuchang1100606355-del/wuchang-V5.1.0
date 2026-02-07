# DNS 設定開始 - 執行步驟

**執行時間：** 2026-01-20  
**目標：** 為商家和居民提供穩定的服務可見度

---

## 📋 執行步驟

### ✅ 步驟 1: 安裝 cloudflared

**方法 A: 使用安裝腳本（推薦）**
```powershell
.\install_cloudflared.ps1
```

**方法 B: 手動下載安裝**
1. 下載：https://github.com/cloudflare/cloudflared/releases/latest
2. 下載 `cloudflared-windows-amd64.exe`
3. 重新命名為 `cloudflared.exe`
4. 放到 `C:\Windows\System32\` 或 PATH 中的目錄

**驗證安裝：**
```powershell
cloudflared --version
```

---

### ✅ 步驟 2: 登入 Cloudflare

```powershell
cloudflared tunnel login
```

**說明：**
- 會開啟瀏覽器讓您登入 Cloudflare 帳號
- **選擇網域：wuchang.org.tw**
- 完成後會在 `%USERPROFILE%\.cloudflared` 產生憑證檔案

**檢查憑證：**
```powershell
dir %USERPROFILE%\.cloudflared
```

應該看到 `cert.pem` 檔案。

---

### ✅ 步驟 3: 建立命名隧道

```powershell
cloudflared tunnel create wuchang-tunnel
```

**重要：** 記下產生的 **Tunnel ID**！

例如輸出：
```
Created tunnel wuchang-tunnel with id abc123-4567-8901-2345-6789abcdef12
```

**記下這個 ID：** `abc123-4567-8901-2345-6789abcdef12`

**列出所有隧道（確認）：**
```powershell
cloudflared tunnel list
```

---

### ✅ 步驟 4: 配置 DNS 路由

為所有服務配置 DNS 路由：

```powershell
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

**驗證 DNS 路由：**
```powershell
cloudflared tunnel route dns list
```

應該看到所有 4 個域名的路由配置。

---

### ✅ 步驟 5: 複製憑證檔案

**找到憑證檔案：**
憑證檔案位置：`%USERPROFILE%\.cloudflared\<tunnel-id>.json`

**使用 PowerShell 複製（替換 <tunnel-id> 為步驟 3 記下的實際 ID）：**
```powershell
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

### ✅ 步驟 6: 更新配置檔案

編輯 `cloudflared/config.yml`，將 `<tunnel-id>` 替換為步驟 3 記下的實際 Tunnel ID。

**方法 A: 使用 PowerShell（替換 <實際-tunnel-id>）：**
```powershell
(Get-Content cloudflared\config.yml) -replace '<tunnel-id>', '<實際-tunnel-id>' | Set-Content cloudflared\config.yml
```

**方法 B: 手動編輯：**
打開 `cloudflared/config.yml`，找到：
```yaml
tunnel: <tunnel-id>
```

替換為：
```yaml
tunnel: abc123-4567-8901-2345-6789abcdef12  # 步驟 3 記下的實際 ID
```

---

### ✅ 步驟 7: 重啟 Cloudflare Tunnel 容器

```powershell
docker restart wuchangv510-cloudflared-1
```

**查看容器狀態：**
```powershell
docker ps | Select-String cloudflared
```

**查看容器日誌（確認正常）：**
```powershell
docker logs wuchangv510-cloudflared-1 --tail 20
```

應該看到：
- ✅ `Registered tunnel connection`
- ✅ 沒有錯誤訊息

---

### ✅ 步驟 8: 驗證設定

**檢查 DNS 解析：**
```powershell
nslookup app.wuchang.org.tw
```

應該解析到 Cloudflare IP（通常是 `104.x.x.x` 或 `172.x.x.x` 範圍）

**執行檢查腳本：**
```powershell
python check_dns_status.py
```

應該看到：
- ✅ DNS 解析成功（4/4）
- ✅ 服務連接成功（4/4）

**瀏覽器測試：**
訪問：`https://app.wuchang.org.tw`  
應該可以看到 Odoo ERP 登入頁面 ✅

---

## ✅ 完成檢查清單

完成所有步驟後，請確認：

- [ ] cloudflared 已安裝並可用
- [ ] Cloudflare 帳號已登入
- [ ] 隧道已建立（wuchang-tunnel）並記下 ID
- [ ] DNS 路由已設定（4 個域名）
- [ ] 憑證檔案已複製到 `cloudflared/credentials.json`
- [ ] 配置檔案中的 Tunnel ID 已更新
- [ ] 容器已重啟並正常運行
- [ ] DNS 解析成功（所有域名）
- [ ] HTTPS 服務可以訪問（所有服務）

---

## 📊 設定完成後的服務地址

商家和居民可以通過以下地址訪問：

- **Odoo ERP 系統：** https://app.wuchang.org.tw
- **AI 介面：** https://ai.wuchang.org.tw
- **容器管理：** https://admin.wuchang.org.tw
- **系統監控：** https://monitor.wuchang.org.tw

---

## 🔧 需要協助？

如果遇到問題，請查看：
- 詳細指南：`DNS_SETUP_COMPLETE_GUIDE.md`
- 疑難排解：`DNS_FIX_GUIDE.md`

---

**開始執行時間：** 2026-01-20  
**目標：** 為商家和居民提供穩定可靠的服務可見度
