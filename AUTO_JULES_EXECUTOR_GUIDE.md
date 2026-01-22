# JULES 任務自動執行器使用指南

## 概述

自動執行器會定期檢查 Google Tasks 中的新任務，自動執行並回報結果。

## 使用方式

### 方式 1：單次檢查（測試用）

```bash
python auto_jules_task_executor.py --once
```

### 方式 2：背景運行（推薦）

```bash
# Windows
start_auto_jules_executor.bat

# 或直接執行
python auto_jules_task_executor.py --interval 60
```

### 方式 3：自訂檢查間隔

```bash
# 每 30 秒檢查一次
python auto_jules_task_executor.py --interval 30

# 每 5 分鐘檢查一次
python auto_jules_task_executor.py --interval 300
```

## 功能說明

### 自動檢查
- 定期檢查 Google Tasks 中的新任務
- 只處理未完成的任務
- 自動跳過已處理的任務

### 自動執行
支援的指令類型：
- **execute** - 執行命令（Python 腳本、PowerShell 等）
- **sync** - 檔案同步
- **check** - 系統檢查
- **upload** - 上傳檔案
- **download** - 下載檔案

### 自動回報
- 執行結果自動附加到任務備註
- 成功任務自動標記為完成
- 失敗任務保留錯誤資訊

## 狀態檔案

- `jules_task_executor_state.json` - 執行狀態（已處理任務、上次檢查時間等）
- `jules_task_executor.log` - 執行日誌

## 日誌查看

```bash
# 查看最新日誌
type jules_task_executor.log

# 查看最後 50 行
powershell "Get-Content jules_task_executor.log -Tail 50"
```

## 停止執行器

### Windows
1. 開啟任務管理器
2. 找到 `python auto_jules_task_executor.py` 進程
3. 結束進程

### 或使用命令
```powershell
# 找到進程
Get-Process python | Where-Object {$_.CommandLine -like "*auto_jules_task_executor*"}

# 結束進程
Stop-Process -Name python -Force
```

## 注意事項

1. **伺服器同帳號**：由於伺服器使用相同帳號，網路共享應該更容易訪問
2. **權限**：確保有執行腳本的權限
3. **網路**：確保可以訪問 Google Tasks API
4. **日誌**：定期檢查日誌檔案，確認執行正常

## 範例：JULES 如何下指令

JULES 在 Google Tasks 中建立任務：

**標題**：執行檔案同步

**備註**：
```
請執行檔案同步

指令類型: sync
```

系統會自動：
1. 檢查到新任務
2. 識別為 sync 類型
3. 執行 `sync_all_profiles.py`
4. 回報結果
5. 標記為完成

## 故障排除

### 問題 1：找不到任務
- 確認任務在正確的任務列表中（包含 "Wuchang" 或 "File Sync"）
- 確認任務未標記為完成

### 問題 2：執行失敗
- 檢查日誌檔案：`jules_task_executor.log`
- 確認腳本路徑正確
- 確認有執行權限

### 問題 3：無法回報結果
- 確認 OAuth 憑證有效
- 檢查 Google Tasks API 連接
