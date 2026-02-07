# 每小時時間排程工作指南

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 📋 功能概述

本指南說明如何設定和管理每小時時間排程工作（使用 Windows Task Scheduler）。

---

## 🔧 已建立的工具

### 1. 設定腳本

**文件**: `scripts/setup_hourly_scheduled_task.ps1`

**功能**:
- ✅ 建立 Windows 工作排程器任務
- ✅ 設定每小時執行一次
- ✅ 自動設定任務權限
- ✅ 支援強制重新建立（-Force）

**使用方式**:
```powershell
# 建立任務
.\scripts\setup_hourly_scheduled_task.ps1

# 強制重新建立（刪除現有任務）
.\scripts\setup_hourly_scheduled_task.ps1 -Force

# 自訂任務名稱和腳本路徑
.\scripts\setup_hourly_scheduled_task.ps1 -TaskName "MyHourlyTask" -ScriptPath "scripts\my_script.bat"
```

### 2. 管理腳本

**文件**: `scripts/manage_hourly_task.ps1`

**功能**:
- ✅ 查看任務狀態
- ✅ 啟用/停用任務
- ✅ 手動執行任務
- ✅ 刪除任務
- ✅ 查看詳細資訊

**使用方式**:
```powershell
# 查看任務狀態
.\scripts\manage_hourly_task.ps1 -Action status

# 啟用任務
.\scripts\manage_hourly_task.ps1 -Action enable

# 停用任務
.\scripts\manage_hourly_task.ps1 -Action disable

# 手動執行任務
.\scripts\manage_hourly_task.ps1 -Action run

# 刪除任務
.\scripts\manage_hourly_task.ps1 -Action delete

# 查看詳細資訊
.\scripts\manage_hourly_task.ps1 -Action info
```

### 3. 執行腳本

**文件**: `scripts/run_hourly_check.bat`

**功能**:
- ✅ 執行每小時檢查
- ✅ 記錄日誌
- ✅ 處理錯誤

**內容**:
- 執行 Python 腳本: `scripts/hourly_deployment_check.py`
- 記錄日誌: `logs/hourly_check_YYYYMMDD_HHMMSS.log`
- 處理退出碼和錯誤

---

## 🚀 設定流程

### 步驟 1: 建立任務

```powershell
.\scripts\setup_hourly_scheduled_task.ps1
```

此腳本會：
1. 檢查腳本檔案是否存在
2. 檢查是否已有現有任務
3. 建立任務動作
4. 建立觸發器（每小時執行一次）
5. 設定任務設定
6. 註冊任務

### 步驟 2: 驗證任務

```powershell
.\scripts\manage_hourly_task.ps1 -Action status
```

### 步驟 3: 啟用任務（如果需要）

```powershell
.\scripts\manage_hourly_task.ps1 -Action enable
```

---

## 📊 任務資訊

### 當前任務

- **任務名稱**: `WuchangHourlyCheck`
- **執行腳本**: `scripts\run_hourly_check.bat`
- **執行頻率**: 每小時一次
- **任務狀態**: Ready（就緒）
- **下次執行時間**: 2026/1/12 上午 04:27:27

### 任務設定

- **執行使用者**: 當前使用者
- **登入類型**: S4U (Service-for-User)
- **允許在電池供電時執行**: 是
- **多個實例**: 忽略新實例
- **持續時間**: 365 天

---

## ⚙️ 配置選項

### 任務名稱

預設：`WuchangHourlyCheck`

可以自訂：
```powershell
.\scripts\setup_hourly_scheduled_task.ps1 -TaskName "MyCustomTask"
```

### 執行腳本

預設：`scripts\run_hourly_check.bat`

可以自訂：
```powershell
.\scripts\setup_hourly_scheduled_task.ps1 -ScriptPath "scripts\my_script.bat"
```

### 工作目錄

預設：當前目錄（`C:\wuchang V5.1.0`）

可以自訂：
```powershell
.\scripts\setup_hourly_scheduled_task.ps1 -WorkingDirectory "C:\MyProject"
```

---

## 📄 日誌檔案

### 日誌位置

任務執行的日誌檔案會儲存在：
```
logs/hourly_check_YYYYMMDD_HHMMSS.log
```

例如：
```
logs/hourly_check_20260112_042727.log
```

### 日誌內容

- 執行開始時間
- Python 腳本輸出
- 執行結束時間
- 退出碼

---

## 🔍 管理命令

### 使用 PowerShell 管理

```powershell
# 查看任務
Get-ScheduledTask -TaskName WuchangHourlyCheck

# 查看任務資訊
Get-ScheduledTaskInfo -TaskName WuchangHourlyCheck

# 啟用任務
Enable-ScheduledTask -TaskName WuchangHourlyCheck

# 停用任務
Disable-ScheduledTask -TaskName WuchangHourlyCheck

# 手動執行任務
Start-ScheduledTask -TaskName WuchangHourlyCheck

# 刪除任務
Unregister-ScheduledTask -TaskName WuchangHourlyCheck -Confirm:$false
```

### 使用管理腳本

```powershell
# 查看狀態
.\scripts\manage_hourly_task.ps1 -Action status

# 啟用
.\scripts\manage_hourly_task.ps1 -Action enable

# 停用
.\scripts\manage_hourly_task.ps1 -Action disable

# 執行
.\scripts\manage_hourly_task.ps1 -Action run

# 刪除
.\scripts\manage_hourly_task.ps1 -Action delete

# 詳細資訊
.\scripts\manage_hourly_task.ps1 -Action info
```

---

## ⚠️ 注意事項

1. **權限**: 需要管理員權限才能建立和管理任務
2. **腳本路徑**: 確保執行腳本路徑正確
3. **Python 環境**: 確保 Python 已安裝並在 PATH 中
4. **日誌目錄**: 確保 `logs` 目錄存在或有寫入權限

---

## 💡 使用建議

1. **首次設定**: 建議先手動執行腳本測試
2. **驗證任務**: 設定後使用 `status` 動作驗證
3. **監控日誌**: 定期檢查日誌檔案確認執行正常
4. **測試執行**: 使用 `run` 動作測試任務是否正常

---

## 🚀 快速開始

```powershell
# 1. 設定任務
.\scripts\setup_hourly_scheduled_task.ps1

# 2. 查看狀態
.\scripts\manage_hourly_task.ps1 -Action status

# 3. 測試執行
.\scripts\manage_hourly_task.ps1 -Action run

# 4. 查看日誌
Get-Content logs\hourly_check_*.log | Select-Object -Last 50
```

---

**報告生成時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「每小時時間排程工作已設定完成，系統會自動每小時執行檢查！」* ✨
