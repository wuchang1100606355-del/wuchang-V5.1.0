# Google Tasks API 用途說明

## 概述

Google Tasks API 在這個系統中主要用於**與 JULES 任務管理系統整合**，實現以下功能：

## 主要用途

### 1. **從 JULES 獲取任務內容**

JULES 會將任務和指令放在 Google Tasks 中，系統可以：
- 讀取任務內容
- 獲取任務詳情（標題、備註、到期時間等）
- 自動處理任務指令

**使用場景：**
```bash
# 從 Google Tasks URL 獲取任務
python get_jules_task_direct.py "https://jules.google.com/task/18167513009276525148"
```

### 2. **上傳系統報告和差異**

系統可以將執行結果、差異報告等資訊上傳到 Google Tasks，供 JULES 查看：

**使用場景：**
```bash
# 自動上傳檔案比對差異報告
python upload_diff_to_jules.py --auto-upload
```

**實際用途：**
- 檔案同步差異報告
- 系統狀態報告
- 執行結果回報
- 需要 JULES 處理的問題清單

### 3. **從 Google Tasks 同步檔案內容**

JULES 可以在 Google Tasks 的任務備註中放置檔案內容，系統可以：
- 讀取任務備註中的內容
- 自動覆蓋本地檔案
- 實現雙向同步

**使用場景：**
```bash
# 從 Google Tasks 任務同步並覆蓋本地檔案
python sync_from_google_task.py "https://jules.google.com/task/XXX" "target_file.txt"
```

### 4. **任務進度追蹤**

系統可以：
- 檢查任務狀態（完成/待處理）
- 更新任務進度
- 標記任務為已完成

**使用場景：**
```bash
# 檢查任務進度
python check_google_task_progress.py "https://jules.google.com/task/XXX"
```

## 與 JULES 的整合流程

```
JULES (Google Tasks)
    ↓
    建立任務（包含指令或檔案內容）
    ↓
系統讀取任務
    ↓
    執行指令/處理檔案
    ↓
系統上傳結果報告
    ↓
JULES 查看結果
```

## 實際應用範例

### 範例 1：檔案同步指令

1. **JULES 在 Google Tasks 中建立任務：**
   - 標題：「執行檔案同步」
   - 備註：包含需要同步的檔案清單或配置

2. **系統讀取任務：**
   ```bash
   python get_jules_task_direct.py <task_url>
   ```

3. **系統執行同步：**
   - 根據任務內容執行檔案比對
   - 生成差異報告

4. **系統上傳結果：**
   ```bash
   python upload_diff_to_jules.py --auto-upload
   ```

### 範例 2：配置檔案更新

1. **JULES 在任務備註中放置新的配置內容**

2. **系統讀取並同步：**
   ```bash
   python sync_from_google_task.py <task_url> "config.json"
   ```

3. **本地檔案自動更新為任務中的內容**

### 範例 3：問題回報

1. **系統檢測到問題**

2. **自動生成報告並上傳：**
   ```bash
   python generate_diff_report_for_jules.py
   python upload_diff_to_jules.py --auto-upload
   ```

3. **JULES 在 Google Tasks 中查看問題清單**

## 為什麼使用 Google Tasks？

1. **統一管理：** JULES 可以在一個地方管理所有任務
2. **易於追蹤：** 可以查看任務狀態、到期時間等
3. **雙向溝通：** 系統可以讀取任務，也可以上傳結果
4. **整合方便：** Google Workspace for Nonprofits 已驗證，無需額外費用
5. **可訪問性：** 可以在任何設備上查看和管理任務

## 相關檔案

- `google_tasks_integration.py` - Google Tasks API 整合模組
- `get_jules_task_direct.py` - 從 Google Tasks URL 獲取任務
- `upload_diff_to_jules.py` - 上傳差異報告到 Google Tasks
- `sync_from_google_task.py` - 從 Google Tasks 同步檔案
- `check_google_task_progress.py` - 檢查任務進度

## 總結

Google Tasks API 在這個系統中主要作為**與 JULES 任務管理系統的溝通橋樑**，實現：
- 📥 **接收指令**：從 JULES 獲取任務和指令
- 📤 **回報結果**：上傳執行結果和報告
- 🔄 **雙向同步**：檔案內容的雙向同步
- 📊 **進度追蹤**：任務狀態和進度管理

這樣可以讓 JULES 遠程管理系統，系統也可以自動回報狀態，實現自動化的任務管理流程。
