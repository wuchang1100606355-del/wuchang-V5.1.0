## 🔓 IP 192.18.50.249 連入許可設定

**配置完成時間**: 2026-01-11 01:10:00  
**配置目標 IP**: 192.18.50.249  
**配置狀態**: ✅ COMPLETED

---

### 📋 開放的埤列表

| 埤   | 服務        | 描述               | 狀態 |
| ---- | ----------- | ------------------ | ---- |
| 8069 | Odoo ERP    | 企業資源規劃系統   | ✅   |
| 8080 | AI Service  | 妹妹 AI 服務       | ✅   |
| 3001 | Uptime Kuma | 服務監控系統       | ✅   |
| 80   | HTTP        | 超文字傳輸協議     | ✅   |
| 443  | HTTPS       | 安全超文字傳輸協議 | ✅   |
| 5432 | PostgreSQL  | 資料庫服務         | ✅   |

---

### 🔗 連線方式

#### 從 192.18.50.249 連線到本機

**Odoo ERP:**

```
URL: http://192.168.50.84:8069
或
URL: https://wuchang.life/odoo (透過CloudFlare Tunnel)
```

**AI 服務:**

```
URL: http://192.168.50.84:8080
或
URL: https://ai.wuchang.life (透過CloudFlare Tunnel)
```

**Uptime Kuma 監控:**

```
URL: http://192.168.50.84:3001
或
URL: https://status.wuchang.life (透過CloudFlare Tunnel)
```

**PostgreSQL 資料庫:**

```
連接字串: postgresql://user@192.168.50.84:5432/odoo
```

---

### 🛡️ 安全性說明

✅ **只允許該特定 IP 連入**

-   防火牆規則限制遠程地址為 192.18.50.249
-   其他 IP 地址被拒絕

✅ **指定埤限制**

-   只開放必要的埤
-   其他埤保持關閉

✅ **使用身份驗證**

-   設備必須通過身份驗證系統
-   本機唯一碼 + 約定金令牌驗證

---

### 🔍 防火牆規則驗證

#### 查看已添加的規則

```powershell
netsh advfirewall firewall show rule name="Allow-*-192.18.50.249"
```

#### 查看所有入站規則

```powershell
netsh advfirewall firewall show rule dir=in action=allow
```

#### 測試連線（從 192.18.50.249）

```powershell
Test-NetConnection -ComputerName 192.168.50.84 -Port 8069
Test-NetConnection -ComputerName 192.168.50.84 -Port 8080
Test-NetConnection -ComputerName 192.168.50.84 -Port 3001
```

---

### 📊 網路架構

```
192.18.50.249 (遠程設備)
     ↓
[防火牆 - 允許入站]
     ↓
192.168.50.84:8069 (Odoo)
192.168.50.84:8080 (AI Service)
192.168.50.84:3001 (Kuma)
192.168.50.84:80 (HTTP)
192.168.50.84:443 (HTTPS)
192.168.50.84:5432 (PostgreSQL)
```

---

### 🔐 連線認證流程

```
1. 遠程設備 (192.18.50.249) 發起連線
   ↓
2. 防火牆檢查
   • IP 地址: ✓ 192.18.50.249 (允許)
   • 埤: ✓ 8069/8080/3001 等 (允許)
   ↓
3. 連接到本機服務
   ↓
4. 設備身份驗證
   • 發送設備 ID
   • 發送本機唯一碼
   • 發送約定金令牌
   ↓
5. 驗證通過 → 授予訪問權限
```

---

### 🛠️ 管理命令

#### 添加新規則

```batch
netsh advfirewall firewall add rule name="Rule-Name" dir=in action=allow protocol=tcp localport=PORT remoteip=192.18.50.249
```

#### 刪除規則

```batch
netsh advfirewall firewall delete rule name="Allow-8069-192.18.50.249"
```

#### 禁用所有入站規則

```batch
netsh advfirewall firewall set rule dir=in action=block
```

#### 啟用所有入站規則

```batch
netsh advfirewall firewall set rule dir=in action=allow
```

---

### ⚠️ 重要說明

1. **防火牆規則需要管理員權限才能配置**

    - 執行 `configure_firewall.bat` 時需選擇「以管理員身分執行」

2. **Windows 防火牆狀態檢查**

    ```powershell
    Get-NetFirewallProfile -All | Select-Object Name, Enabled
    ```

3. **重啟防火牆服務（如需要）**

    ```powershell
    Restart-Service -Name mpssvc -Force
    ```

4. **如果規則未生效**
    - 檢查 Windows Defender 防火牆是否啟用
    - 檢查組策略限制
    - 檢查第三方防火牆軟體

---

### ✅ 完成清單

-   [x] 為 192.18.50.249 添加防火牆入站規則
-   [x] 開放所有必要埤 (8069, 8080, 3001, 80, 443, 5432)
-   [x] 驗證防火牆規則配置
-   [x] 建立身份驗證機制
-   [x] 文檔化連線方式
-   [x] 提供管理命令

---

**IP 192.18.50.249 現已獲得本機連入許可！** 🎉
