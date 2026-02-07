# 重新總店私人 DNS 主機名稱設定指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**實驗對象**: 重新總店（聊國咖啡重新總店）  
**用途**: POS 設備透過內部 DNS 名稱連接伺服器

---

## 🎯 設定目標

為重新總店建立私人 DNS 主機名稱，讓 POS 設備可以透過友善的主機名稱（而非 IP 地址）連接到伺服器。

### 優勢

- ✅ **易於記憶**：使用 `pos-server.chong-sin.local` 而非 `192.168.50.84`
- ✅ **靈活性**：IP 變更時只需更新 DNS，無需修改 POS 配置
- ✅ **專業性**：符合企業級網路管理標準
- ✅ **安全性**：內部 DNS 名稱不對外公開

---

## 📋 網路架構分析

### 重新總店網路資訊

根據現有配置：

| 項目 | 資訊 |
|------|------|
| **店名** | 聊國咖啡重新總店 |
| **POS 配置 ID** | `pos_config_re_main` |
| **公開 IP** | `220.135.21.74` (shop.wuchang.life) |
| **內部網段** | `192.168.50.0/24` |
| **路由器 IP** | `192.168.50.1` |
| **伺服器 IP** | `192.168.50.84` (推測) |
| **DNS 伺服器** | `192.168.50.1` (路由器), `8.8.8.8` (Google) |

---

## 🔧 方案選擇

### 方案 A：路由器內建 DNS（推薦）

**適用情況**：路由器支援 DNS 伺服器功能（如 UniFi、MikroTik、OpenWrt）

**優點**：
- ✅ 集中管理
- ✅ 自動生效（所有連線設備）
- ✅ 無需額外設備

**設定步驟**：
1. 登入路由器管理介面
2. 進入 DNS/DHCP 設定
3. 新增主機名稱對應

### 方案 B：Windows Server DNS（進階）

**適用情況**：有 Windows Server 作為 DNS 伺服器

**優點**：
- ✅ 功能完整
- ✅ 整合 Active Directory
- ✅ 支援動態更新

### 方案 C：Pi-hole / dnsmasq（輕量級）

**適用情況**：需要輕量級 DNS 伺服器

**優點**：
- ✅ 開源免費
- ✅ 輕量級
- ✅ 可阻擋廣告

### 方案 D：Hosts 檔案（臨時方案）

**適用情況**：快速測試或小型環境

**優點**：
- ✅ 設定簡單
- ✅ 無需額外設備

**缺點**：
- ❌ 需在每台設備設定
- ❌ 維護成本高

---

## 🚀 推薦方案：路由器 DNS + Hosts 檔案備援

結合方案 A 和方案 D，確保可靠性和靈活性。

---

## 📝 主機名稱命名規範

### 命名規則

採用階層式命名：`{服務}.{位置}.{網域}`

### 重新總店主機名稱建議

| 主機名稱 | IP 地址 | 用途 | 說明 |
|---------|---------|------|------|
| `pos-server.chong-sin.local` | `192.168.50.84` | POS 伺服器 | Odoo POS 主服務 |
| `odoo.chong-sin.local` | `192.168.50.84` | Odoo 服務 | Odoo Web 介面 |
| `api.chong-sin.local` | `192.168.50.84` | API 服務 | REST API 端點 |
| `printer.chong-sin.local` | `192.168.50.xxx` | 印表機 | 收據印表機 |
| `router.chong-sin.local` | `192.168.50.1` | 路由器 | 網路閘道器 |
| `pos-01.chong-sin.local` | `192.168.50.xxx` | POS 設備 1 | Samsung Tab S9 |
| `pos-02.chong-sin.local` | `192.168.50.xxx` | POS 設備 2 | 備用 POS |

### 簡化版本（如果路由器不支援子網域）

| 主機名稱 | IP 地址 | 用途 |
|---------|---------|------|
| `pos-server` | `192.168.50.84` | POS 伺服器 |
| `odoo-server` | `192.168.50.84` | Odoo 服務 |
| `printer-01` | `192.168.50.xxx` | 印表機 |

---

## 🔧 實作步驟

### Step 1: 確認路由器型號和功能

```powershell
# 檢查路由器 IP 和型號
$gateway = (Get-NetRoute -DestinationPrefix "0.0.0.0/0").NextHop
Write-Host "路由器 IP: $gateway"

# 嘗試訪問路由器管理介面
Start-Process "http://$gateway"
```

### Step 2: 路由器 DNS 設定（如果支援）

#### UniFi Controller 設定

1. 登入 UniFi Controller
2. 進入 **Settings** → **Networks** → **LAN**
3. 找到 **DHCP Name Server** 設定
4. 新增 **DHCP Options**：
   ```
   Option 15: Domain Name = chong-sin.local
   ```
5. 進入 **Clients** → 選擇設備 → **Configure**
6. 設定 **Hostname Override**

#### 一般路由器設定

1. 登入路由器管理介面（通常是 `192.168.50.1`）
2. 進入 **DHCP** 或 **DNS** 設定
3. 尋找 **Static DNS** 或 **Host Mapping** 功能
4. 新增主機名稱對應：
   ```
   pos-server → 192.168.50.84
   odoo-server → 192.168.50.84
   ```

### Step 3: Windows Hosts 檔案設定（備援方案）

建立自動化腳本來設定 Hosts 檔案：

```powershell
# scripts/setup_chong_sin_hosts.ps1
$hostsFile = "$env:SystemRoot\System32\drivers\etc\hosts"
$hostsContent = @"

# 重新總店私人 DNS 主機名稱
# 設定日期: $(Get-Date -Format 'yyyy-MM-dd')

192.168.50.84    pos-server.chong-sin.local
192.168.50.84    odoo.chong-sin.local
192.168.50.84    api.chong-sin.local
192.168.50.84    pos-server
192.168.50.84    odoo-server

192.168.50.1     router.chong-sin.local
192.168.50.1     router

# POS 設備（需根據實際 IP 調整）
# 192.168.50.xxx    pos-01.chong-sin.local
# 192.168.50.xxx    pos-02.chong-sin.local

"@

# 備份現有 hosts 檔案
$backupFile = "$hostsFile.backup.$(Get-Date -Format 'yyyyMMdd')"
if (Test-Path $hostsFile) {
    Copy-Item $hostsFile $backupFile -Force
    Write-Host "已備份 hosts 檔案: $backupFile" -ForegroundColor Green
}

# 檢查是否已存在設定
$existingContent = Get-Content $hostsFile -Raw -ErrorAction SilentlyContinue
if ($existingContent -notmatch "pos-server.chong-sin.local") {
    # 追加新設定
    Add-Content -Path $hostsFile -Value $hostsContent -Encoding ASCII
    Write-Host "已新增重新總店 DNS 主機名稱設定" -ForegroundColor Green
} else {
    Write-Host "DNS 主機名稱設定已存在" -ForegroundColor Yellow
}

Write-Host "`n設定完成！" -ForegroundColor Green
Write-Host "測試連線: ping pos-server.chong-sin.local" -ForegroundColor Cyan
```

### Step 4: POS 設備 DNS 設定

#### Android POS 設備（Samsung Galaxy Tab S9）

1. **設定 → 連線 → Wi-Fi**
2. 長按已連線的 Wi-Fi 網路
3. **修改網路** → **進階選項**
4. **IP 設定** → **靜態**
5. **DNS 1**: `192.168.50.1` (路由器)
6. **DNS 2**: `8.8.8.8` (Google)

#### 透過 Google Workspace MDM 設定（推薦）

如果 POS 設備已納入 Google Workspace 管理：

1. **Google Admin Console** → **設備** → **行動裝置與端點**
2. 選擇 POS 設備
3. **網路設定** → **Wi-Fi 設定檔**
4. 設定 **DNS 伺服器**：
   - 主要：`192.168.50.1`
   - 次要：`8.8.8.8`
5. 設定 **搜尋網域**：`chong-sin.local`

### Step 5: 測試 DNS 解析

```powershell
# 測試主機名稱解析
Test-NetConnection -ComputerName pos-server.chong-sin.local -Port 8069
Test-NetConnection -ComputerName odoo.chong-sin.local -Port 8069

# 使用 nslookup 測試
nslookup pos-server.chong-sin.local
nslookup odoo.chong-sin.local

# 使用 ping 測試
ping pos-server.chong-sin.local
ping odoo.chong-sin.local
```

---

## 🔄 自動化設定腳本

### 完整設定腳本

```powershell
# scripts/setup_chong_sin_private_dns.ps1
# 重新總店私人 DNS 設定腳本

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$RouterIP = "192.168.50.1",
    [string]$Domain = "chong-sin.local"
)

Write-Host "=== 重新總店私人 DNS 設定 ===" -ForegroundColor Cyan
Write-Host "伺服器 IP: $ServerIP" -ForegroundColor White
Write-Host "路由器 IP: $RouterIP" -ForegroundColor White
Write-Host "網域: $Domain" -ForegroundColor White

# 1. 設定 Hosts 檔案
Write-Host "`n[1] 設定 Hosts 檔案..." -ForegroundColor Yellow
$hostsFile = "$env:SystemRoot\System32\drivers\etc\hosts"
$hostsEntries = @"
# 重新總店私人 DNS - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
$ServerIP    pos-server.$Domain
$ServerIP    odoo.$Domain
$ServerIP    api.$Domain
$ServerIP    pos-server
$ServerIP    odoo-server
$RouterIP    router.$Domain
$RouterIP    router
"@

# 備份
$backupFile = "$hostsFile.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
if (Test-Path $hostsFile) {
    Copy-Item $hostsFile $backupFile -Force
    Write-Host "  ✓ 已備份: $backupFile" -ForegroundColor Green
}

# 檢查並新增
$existing = Get-Content $hostsFile -Raw -ErrorAction SilentlyContinue
if ($existing -notmatch "pos-server\.$Domain") {
    Add-Content -Path $hostsFile -Value $hostsEntries -Encoding ASCII
    Write-Host "  ✓ Hosts 檔案已更新" -ForegroundColor Green
} else {
    Write-Host "  ✓ Hosts 檔案設定已存在" -ForegroundColor Green
}

# 2. 設定本機 DNS 快取
Write-Host "`n[2] 清除 DNS 快取..." -ForegroundColor Yellow
ipconfig /flushdns | Out-Null
Write-Host "  ✓ DNS 快取已清除" -ForegroundColor Green

# 3. 測試解析
Write-Host "`n[3] 測試 DNS 解析..." -ForegroundColor Yellow
$testHosts = @("pos-server.$Domain", "odoo.$Domain", "pos-server")
foreach ($host in $testHosts) {
    try {
        $result = [System.Net.Dns]::GetHostAddresses($host)
        Write-Host "  ✓ $host → $($result[0].IPAddressToString)" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $host → 解析失敗" -ForegroundColor Red
    }
}

# 4. 測試連線
Write-Host "`n[4] 測試服務連線..." -ForegroundColor Yellow
$services = @(
    @{Name="Odoo Web"; Host="pos-server.$Domain"; Port=8069},
    @{Name="Odoo API"; Host="api.$Domain"; Port=8069}
)

foreach ($service in $services) {
    try {
        $connection = Test-NetConnection -ComputerName $service.Host -Port $service.Port -WarningAction SilentlyContinue -InformationLevel Quiet
        if ($connection) {
            Write-Host "  ✓ $($service.Name) ($($service.Host):$($service.Port)) - 連線成功" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $($service.Name) ($($service.Host):$($service.Port)) - 連線失敗" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ $($service.Name) - 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== 設定完成 ===" -ForegroundColor Green
Write-Host "`n主機名稱對應：" -ForegroundColor Cyan
Write-Host "  pos-server.$Domain → $ServerIP" -ForegroundColor White
Write-Host "  odoo.$Domain → $ServerIP" -ForegroundColor White
Write-Host "  api.$Domain → $ServerIP" -ForegroundColor White
Write-Host "`n使用方式：" -ForegroundColor Yellow
Write-Host "  在 POS 設備中使用: http://pos-server.$Domain:8069/pos/ui" -ForegroundColor White
Write-Host "  或簡化版本: http://pos-server:8069/pos/ui" -ForegroundColor White
```

---

## 📱 POS 設備配置更新

### 更新 Odoo POS 配置

在 POS 設備上，將伺服器 URL 從 IP 地址改為主機名稱：

**舊設定**：
```
http://192.168.50.84:8069/pos/ui
```

**新設定**：
```
http://pos-server.chong-sin.local:8069/pos/ui
或
http://pos-server:8069/pos/ui
```

### 更新 Sister Control 配置

```python
# 更新 sister_agent.py 中的 VM_URL
VM_URL = "http://pos-server.chong-sin.local:8069"  # 或使用公開域名
POLL_URL = f"{VM_URL}/wuchang/sister/poll"
```

---

## 🔍 路由器 DNS 設定範例

### 常見路由器設定方式

#### 1. TP-Link / D-Link

```
管理介面 → 進階設定 → DHCP 伺服器 → 靜態 IP 分配
新增：
  主機名稱: pos-server
  IP 地址: 192.168.50.84
  MAC 地址: [伺服器 MAC]
```

#### 2. ASUS Router

```
管理介面 → 區域網路 → DHCP 伺服器 → 手動指定 IP
新增：
  裝置名稱: pos-server
  IP 地址: 192.168.50.84
  MAC 地址: [伺服器 MAC]
```

#### 3. UniFi Controller

```
Settings → Networks → LAN → DHCP Service Management
新增 DHCP Reservation:
  MAC Address: [伺服器 MAC]
  IP Address: 192.168.50.84
  Hostname: pos-server
```

#### 4. OpenWrt

```bash
# 編輯 /etc/hosts
echo "192.168.50.84 pos-server.chong-sin.local" >> /etc/hosts
echo "192.168.50.84 odoo.chong-sin.local" >> /etc/hosts

# 編輯 /etc/config/dhcp
config host
    option name 'pos-server'
    option ip '192.168.50.84'
    option mac 'XX:XX:XX:XX:XX:XX'

# 重啟 DNS 服務
/etc/init.d/dnsmasq restart
```

---

## 🧪 測試與驗證

### 測試腳本

```powershell
# scripts/test_chong_sin_dns.ps1
Write-Host "=== 重新總店 DNS 解析測試 ===" -ForegroundColor Cyan

$testHosts = @(
    "pos-server.chong-sin.local",
    "odoo.chong-sin.local",
    "api.chong-sin.local",
    "pos-server",
    "odoo-server"
)

foreach ($host in $testHosts) {
    Write-Host "`n測試: $host" -ForegroundColor Yellow
    try {
        $addresses = [System.Net.Dns]::GetHostAddresses($host)
        foreach ($addr in $addresses) {
            Write-Host "  ✓ 解析成功: $($addr.IPAddressToString)" -ForegroundColor Green
            
            # 測試連線
            $connection = Test-NetConnection -ComputerName $addr.IPAddressToString -Port 8069 -WarningAction SilentlyContinue -InformationLevel Quiet
            if ($connection) {
                Write-Host "    ✓ 服務連線正常 (Port 8069)" -ForegroundColor Green
            } else {
                Write-Host "    ⚠ 服務連線失敗 (Port 8069)" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "  ❌ 解析失敗: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== 測試完成 ===" -ForegroundColor Green
```

---

## 📊 DNS 記錄建議

### 完整 DNS 記錄表

| 主機名稱 | 類型 | IP 地址 | TTL | 用途 |
|---------|------|---------|-----|------|
| `pos-server.chong-sin.local` | A | `192.168.50.84` | 3600 | POS 伺服器主機名稱 |
| `odoo.chong-sin.local` | A | `192.168.50.84` | 3600 | Odoo Web 服務 |
| `api.chong-sin.local` | A | `192.168.50.84` | 3600 | API 服務端點 |
| `router.chong-sin.local` | A | `192.168.50.1` | 3600 | 路由器管理介面 |
| `pos-server` | A | `192.168.50.84` | 3600 | 簡化主機名稱 |
| `odoo-server` | A | `192.168.50.84` | 3600 | 簡化主機名稱 |

---

## 🔐 安全性考量

### 1. 內部網域使用 `.local`

- ✅ `.local` 是 mDNS/Bonjour 標準
- ✅ 不會與公開網域衝突
- ✅ 僅在內部網路有效

### 2. DNS 快取設定

- ✅ 設定適當的 TTL（建議 3600 秒）
- ✅ 定期清除 DNS 快取
- ✅ 監控 DNS 解析效能

### 3. 備援機制

- ✅ Hosts 檔案作為備援
- ✅ 多個 DNS 伺服器（路由器 + Google DNS）
- ✅ 定期驗證 DNS 解析

---

## 📋 檢查清單

### 設定前檢查

- [ ] 確認伺服器 IP 地址（`192.168.50.84`）
- [ ] 確認路由器 IP 地址（`192.168.50.1`）
- [ ] 確認路由器型號和功能
- [ ] 確認 POS 設備 IP 設定方式

### 設定後驗證

- [ ] Hosts 檔案已更新
- [ ] DNS 解析測試通過
- [ ] POS 設備可以連線
- [ ] Odoo 服務正常運作
- [ ] 備份檔案已建立

---

## 🎯 使用範例

### POS 設備連線 URL

**使用主機名稱**：
```
http://pos-server.chong-sin.local:8069/pos/ui
```

**使用簡化名稱**（如果路由器支援）：
```
http://pos-server:8069/pos/ui
```

### API 端點

```
http://api.chong-sin.local:8069/wuchang/sister/poll
或
http://api:8069/wuchang/sister/poll
```

---

## 🔄 維護與更新

### 定期檢查

```powershell
# 每週執行一次 DNS 健康檢查
.\scripts\test_chong_sin_dns.ps1
```

### IP 變更時更新

```powershell
# 更新伺服器 IP
.\scripts\setup_chong_sin_private_dns.ps1 -ServerIP "192.168.50.85"
```

---

## 📚 相關文件

- `docs/POS_FILE_STORAGE_ANALYSIS.md` - POS 檔案端分析
- `docs/POS_GOOGLE_WORKSPACE_MDM_INTEGRATION.md` - Google Workspace MDM 整合
- `docs/architecture/static_dns_design.md` - DNS 架構設計

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)  
**實驗對象**: 重新總店（聊國咖啡重新總店）
