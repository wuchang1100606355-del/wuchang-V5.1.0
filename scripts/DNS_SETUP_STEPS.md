# DNS 設定執行步驟

**執行時間：** 2026-01-20  
**目標：** 為商家和居民提供穩定的服務可見度

---

## 📋 執行步驟

### 步驟 1: 檢查 cloudflared 安裝

```powershell
cloudflared --version
```

**如果未安裝：**
1. 下載：https://github.com/cloudflare/cloudflared/releases/latest
2. 下載 `cloudflared-windows-amd64.exe`
3. 重新命名為 `cloudflared.exe`
4. 放到 `C:\Windows\System32\` 或 PATH 中的目錄

---

### 步驟 2: 登入 Cloudflare

```powershell
cloudflared tunnel login
```

**說明：**
- 會開啟瀏覽器讓您登入 Cloudflare
- 選擇網域：**wuchang.org.tw**
- 完成後會產生憑證檔案

**檢查憑證：**
```powershell
dir %USERPROFILE%\.cloudflared
```

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

**記下 ID：** `abc123-4567-8901-2345-6789abcdef12`

---

### 步驟 4: 配置 DNS 路由

```powershell
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

**驗證：**
```powershell
cloudflared tunnel route dns list
```

---

### 步驟 5: 複製憑證檔案

```powershell
# 替換 <tunnel-id> 為步驟 3 記下的實際 ID
Copy-Item "$env:USERPROFILE\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"
```

**或手動複製：**
- 來源：`C:\Users\<您的用戶名>\.cloudflared\<tunnel-id>.json`
- 目標：`C:\wuchang V5.1.0\wuchang-V5.1.0\cloudflared\credentials.json`

---

### 步驟 6: 更新配置檔案

編輯 `cloudflared/config.yml`，將 `<tunnel-id>` 替換為步驟 3 記下的實際 Tunnel ID。

**使用以下命令（替換實際 ID）：**
```powershell
# 替換 <實際-tunnel-id> 為步驟 3 的 ID
(Get-Content cloudflared\config.yml) -replace '<tunnel-id>', '<實際-tunnel-id>' | Set-Content cloudflared\config.yml
```

**或手動編輯：**
```yaml
tunnel: abc123-4567-8901-2345-6789abcdef12  # 替換這裡
```

---

### 步驟 7: 重啟容器

```powershell
docker restart wuchangv510-cloudflared-1
```

**查看日誌：**
```powershell
docker logs wuchangv510-cloudflared-1 --tail 20
```

應該看到 `Registered tunnel connection` ✅

---

### 步驟 8: 驗證設定

```powershell
python check_dns_status.py
```

**瀏覽器測試：**
- https://app.wuchang.org.tw

---

## ✅ 完成檢查清單

- [ ] cloudflared 已安裝
- [ ] 已登入 Cloudflare
- [ ] 隧道已建立（記下 ID）
- [ ] DNS 路由已設定（4 個）
- [ ] 憑證檔案已複製
- [ ] 配置檔案已更新（Tunnel ID）
- [ ] 容器已重啟
- [ ] DNS 解析成功
- [ ] 服務可以訪問

---

**詳細指南：** `DNS_SETUP_COMPLETE_GUIDE.md`
