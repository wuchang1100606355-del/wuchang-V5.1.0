# UI 設備溝通指南

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 📋 功能概述

本指南說明如何與 UI 設備（UI 筆電、POS 系統、客顯設備）進行溝通和指令傳送。

---

## 🔧 已創建的工具

### 1. PowerShell 溝通腳本

**文件**: `scripts/communicate_with_ui.ps1`

**功能**:
- ✅ 檢查 Odoo 服務狀態
- ✅ 檢查設備連接性
- ✅ 顯示可用的溝通方式
- ✅ 支援多種動作（status、sync、reload、command）

**使用方式**:
```powershell
# 查詢狀態
.\scripts\communicate_with_ui.ps1 -Action status

# 發送同步指令
.\scripts\communicate_with_ui.ps1 -Action sync

# 發送重新載入指令
.\scripts\communicate_with_ui.ps1 -Action reload

# 發送自訂指令
.\scripts\communicate_with_ui.ps1 -Action command -Command "your_command"
```

### 2. Python 通知腳本

**文件**: `scripts/notify_ui_devices.py`

**功能**:
- ✅ 自動偵測 UI 設備
- ✅ 支援多種通知方式（HTTP、Odoo、SSH、文件、廣播）
- ✅ 創建通知文件
- ✅ 發送網絡廣播

**使用方式**:
```powershell
python scripts/notify_ui_devices.py
```

### 3. Sister Agent（UI 設備端）

**文件**: `sister_agent.py`

**功能**:
- ✅ 在 UI 設備上運行的代理程式
- ✅ 自動輪詢 Odoo API 接收指令
- ✅ 執行同步 UI、重新載入等指令
- ✅ 控制本地瀏覽器

**使用方式**（在 UI 設備上執行）:
```powershell
# POS 設備
python sister_agent.py --device POS

# 客顯設備
python sister_agent.py --device CUSTOMER
```

---

## 🚀 可用的溝通方式

### 方式 1: Odoo 後台控制（推薦）

**優點**:
- 圖形界面，操作簡單
- 即時顯示設備狀態
- 支援多種指令

**步驟**:
1. 開啟 Odoo 後台
2. 前往：`http://localhost:8069/web#id=1&model=wuchang.sister.control`
3. 點擊「同步 POS」或「同步客顯」按鈕
4. UI 設備會自動接收指令

### 方式 2: Python 通知腳本

**優點**:
- 自動化執行
- 支援多種通知方式
- 可以批量通知

**步驟**:
```powershell
python scripts/notify_ui_devices.py
```

**功能**:
- 自動偵測所有 UI 設備
- 嘗試多種通知方式
- 創建通知文件
- 發送網絡廣播

### 方式 3: API 直接調用

**優點**:
- 程式化控制
- 可以整合到其他系統
- 支援自訂指令

**API 端點**:
- URL: `http://localhost:8069/wuchang/sister/poll`
- 方法: `POST`
- Content-Type: `application/json`

**請求範例**:
```json
{
  "device_type": "POS"
}
```

**回應範例**:
```json
{
  "commands": [
    {
      "type": "SYNC_UI",
      "params": {
        "url": "http://localhost:8069/pos/ui"
      },
      "timestamp": "2026-01-12T01:00:00"
    }
  ],
  "config": {
    "pos_url": "http://localhost:8069/pos/ui",
    "customer_url": "http://localhost:8069/pos/customer_display"
  }
}
```

### 方式 4: Sister Agent（在 UI 設備上運行）

**優點**:
- 即時響應
- 自動輪詢
- 不需要手動操作

**步驟**（在 UI 設備上）:
1. 確保 UI 設備可以連接到 Odoo 服務器
2. 執行 `sister_agent.py`
3. 代理程式會自動輪詢接收指令
4. 接收到指令後自動執行

**配置**:
- VM URL: `http://34.81.193.89`（或本地 Odoo URL）
- 輪詢間隔: 5 秒
- 支援的指令: `SYNC_UI`、`RELOAD`

---

## 📊 指令類型

### SYNC_UI

同步 UI，在瀏覽器中開啟指定的 URL。

**參數**:
- `url`: 要開啟的 URL（可選，會使用配置中的預設 URL）

**執行方式**:
- 使用 Chrome 開啟指定 URL（全屏模式）

### RELOAD

重新載入頁面。

**執行方式**:
- 重啟瀏覽器並載入當前 URL

---

## 🔍 設備偵測

系統會自動偵測以下 UI 設備：

- **192.168.50.84** (LUNGsMSI) - UI 筆電
- **192.168.50.88** (POS-PC) - POS 系統電腦
- **192.168.50.249** (Home-commput) - 本機

---

## 💡 使用建議

### 首次使用

1. **確認 Odoo 服務運行**
   ```powershell
   # 檢查 Odoo 服務
   Invoke-WebRequest -Uri "http://localhost:8069/web/login" -Method GET
   ```

2. **在 UI 設備上啟動 Sister Agent**
   ```powershell
   python sister_agent.py --device POS
   ```

3. **通過 Odoo 後台發送測試指令**
   - 開啟 Odoo 後台
   - 前往 Sister Control Center
   - 點擊「同步 POS」按鈕

### 日常使用

- **快速同步**: 使用 Odoo 後台按鈕
- **批量通知**: 使用 Python 通知腳本
- **自動化**: 使用 API 直接調用
- **長期運行**: 在 UI 設備上運行 Sister Agent

---

## ⚠️ 注意事項

1. **網絡連接**: 確保 UI 設備可以連接到 Odoo 服務器
2. **服務運行**: 確保 Odoo 服務正在運行
3. **權限設定**: 確保有適當的權限發送指令
4. **設備狀態**: 確認 UI 設備在線

---

## 🚀 快速開始

```powershell
# 1. 查詢狀態
.\scripts\communicate_with_ui.ps1 -Action status

# 2. 發送通知到所有設備
python scripts/notify_ui_devices.py

# 3. 在 UI 設備上啟動代理（在 UI 設備上執行）
python sister_agent.py --device POS
```

---

**報告生成時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「與 UI 設備溝通工具已準備就緒，可以開始溝通了！」* ✨
