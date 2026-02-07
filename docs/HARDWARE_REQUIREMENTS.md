# 五常 POS 系統硬體需求評估

## 📋 最低硬體需求（Odoo 17 POS）

### POS 主機（收銀端）

**最低配置**

-   CPU: Intel Core i3 第 8 代 / AMD Ryzen 3 或更高
-   RAM: 4GB（建議 8GB）
-   儲存: 64GB SSD（建議 128GB）
-   網路: 有線乙太網路或 WiFi 5
-   作業系統: Windows 10/11, Ubuntu 20.04+, macOS 10.15+

**流暢使用建議**

-   CPU: Intel Core i5 第 10 代 / AMD Ryzen 5 或更高
-   RAM: 8GB+
-   儲存: 256GB SSD
-   螢幕: 1920x1080 觸控螢幕（選配）

### 客顯端（顧客顯示）

**最低配置（Chrome OS 開發者模式）**

-   CPU: Intel Celeron N3450 / ARM Cortex-A72 或更高
-   RAM: 2GB（建議 4GB）
-   儲存: 16GB eMMC
-   螢幕: 1280x720 或更高
-   網路: WiFi 或乙太網路

**支援的 Chrome OS 裝置**

-   Chromebook (2018+)
-   Chromebox
-   Chromebase
-   任何支援 Linux (Crostini) 的 Chrome OS 裝置

---

## 🔍 舊電腦評估標準

### 檢查方式（Windows POS 主機）

開啟「系統資訊」：

```powershell
# 取得 CPU 資訊
Get-WmiObject -Class Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

# 取得記憶體資訊
Get-WmiObject -Class Win32_ComputerSystem | Select-Object TotalPhysicalMemory | ForEach-Object { [math]::Round($_.TotalPhysicalMemory / 1GB, 2) }

# 取得硬碟資訊
Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | Select-Object DeviceID, @{Name="Size(GB)";Expression={[math]::Round($_.Size / 1GB, 2)}}, @{Name="FreeSpace(GB)";Expression={[math]::Round($_.FreeSpace / 1GB, 2)}}
```

### 判斷標準

| 項目     | 可用 ✅             | 勉強 ⚠️                    | 不建議 ❌         |
| -------- | ------------------- | -------------------------- | ----------------- |
| **CPU**  | i5 8 代+ / Ryzen 5+ | i3 7-8 代 / Celeron N 系列 | Core 2 Duo / Atom |
| **RAM**  | 8GB+                | 4GB                        | < 4GB             |
| **儲存** | SSD 128GB+          | HDD 500GB+ / SSD 64GB      | HDD < 250GB       |
| **年份** | 2018+               | 2015-2017                  | < 2015            |

---

## 🛠️ 優化舊電腦建議

### 立即可行（免費）

1. **清理系統**

    ```powershell
    # 清理暫存檔案
    Cleanmgr /d C:
    # 停用不必要的啟動程式
    msconfig
    ```

2. **瀏覽器最佳化**

    - Chrome: 停用不必要的擴充功能
    - 啟用硬體加速：`chrome://settings/system`
    - 限制分頁數量（POS 只需 1-2 分頁）

3. **輕量化作業系統**
    - Windows: 停用視覺效果、索引服務、OneDrive 同步
    - Linux: 使用 Lubuntu/Xubuntu 替代 Ubuntu

### 經濟升級（<5000 元）

1. **RAM 升級**: 4GB → 8GB（約 1000-2000 元）
2. **SSD 替換**: HDD → 128GB SSD（約 800-1500 元）
3. **網路卡**: USB 有線網卡（約 300 元，穩定性提升）

### 硬體更換時機

-   **CPU 風扇異音/過熱**: 清潔或更換散熱膏（約 500 元）
-   **硬碟壞軌**: 立即換 SSD
-   **記憶體錯誤**: 執行 Windows 記憶體診斷工具
-   **螢幕閃爍**: 檢查排線或更換螢幕

---

## ⚡ 輕量化 POS 部署方案

### 方案 A：瘦客戶端模式

-   POS 主機只跑瀏覽器（Chrome Kiosk）
-   Odoo 伺服器在 192.168.50.249 運行
-   優點：任何能跑 Chrome 的裝置都可用
-   最低需求：2GB RAM + SSD

### 方案 B：Docker 容器化

-   在伺服器集中運行 Odoo + PostgreSQL
-   POS/客顯只需瀏覽器
-   統一管理、易於備份

### 方案 C：漸進式升級

1. **階段 1**: 現有硬體 + 清理優化（0 元）
2. **階段 2**: 升級 RAM/SSD（約 3000 元）
3. **階段 3**: 更換主機（視需要，約 15000 元起）

---

## 📱 Chrome OS 客顯特別說明

### 開發者模式啟用後優勢

-   完整 Linux 環境（Crostini）
-   可執行 Python 代理程式
-   內建 Chrome 瀏覽器（最佳化）
-   自動更新、安全性高
-   低功耗、無風扇設計（多數機型）

### Kiosk 模式設定

```bash
# 方式1：使用提供的腳本
bash run_agent_chromeos.sh

# 方式2：手動啟動 Chrome Kiosk
google-chrome --kiosk --no-first-run \
  http://192.168.50.249:8069/pos/customer_display
```

### 建議 Chrome OS 客顯機型

-   **Acer Chromebox CXI4**: Intel i3/i5（約 8000-12000 元）
-   **HP Chromebox G4**: Intel Celeron/i3（約 6000-10000 元）
-   **ASUS Chromebox 4**: 各規格可選（約 7000-15000 元）
-   **二手 Chromebook**: 2018+ 機型（約 3000-6000 元）

---

## 🔧 快速檢測腳本

將以下腳本儲存為 `check_hardware.ps1` 並執行：

```powershell
Write-Host "=== 五常 POS 硬體檢測 ===" -ForegroundColor Cyan

# CPU
$cpu = Get-WmiObject -Class Win32_Processor
Write-Host "`nCPU: $($cpu.Name)" -ForegroundColor Yellow
Write-Host "核心數: $($cpu.NumberOfCores) / 邏輯處理器: $($cpu.NumberOfLogicalProcessors)"

# RAM
$ram = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
Write-Host "`nRAM: $ram GB" -ForegroundColor Yellow
if ($ram -ge 8) { Write-Host "✅ 充足" -ForegroundColor Green }
elseif ($ram -ge 4) { Write-Host "⚠️ 勉強可用" -ForegroundColor Yellow }
else { Write-Host "❌ 不足" -ForegroundColor Red }

# 儲存
$disk = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3 -and $_.DeviceID -eq "C:"}
$diskSize = [math]::Round($disk.Size / 1GB, 2)
$diskFree = [math]::Round($disk.FreeSpace / 1GB, 2)
Write-Host "`n儲存: $diskSize GB (剩餘 $diskFree GB)" -ForegroundColor Yellow

# 網路
$network = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
Write-Host "`n網路介面卡:" -ForegroundColor Yellow
$network | ForEach-Object { Write-Host "  - $($_.Name): $($_.LinkSpeed)" }

# 建議
Write-Host "`n=== 建議 ===" -ForegroundColor Cyan
if ($ram -lt 8) { Write-Host "⚠️ 建議升級 RAM 至 8GB" -ForegroundColor Yellow }
if ($diskSize -lt 128) { Write-Host "⚠️ 建議更換為 128GB+ SSD" -ForegroundColor Yellow }
if ($cpu.NumberOfCores -lt 4) { Write-Host "⚠️ CPU 效能可能不足，建議測試實際使用" -ForegroundColor Yellow }
```

---

## 📞 需要協助？

如您的 POS 電腦規格不確定，請執行上述檢測腳本並提供結果，我將給予具體建議。

**快速檢測指令**：

```powershell
systeminfo | findstr /C:"處理器" /C:"實體記憶體總計"
wmic diskdrive get model,size
```
