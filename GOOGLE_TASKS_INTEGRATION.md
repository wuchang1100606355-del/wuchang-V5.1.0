# Google Tasks API 整合指南

## 概述

本模組提供 Google Tasks API 的完整整合功能，支援讀取、建立、更新、刪除任務，以及管理任務列表。

## 功能特性

- ✅ 讀取 Google Tasks 任務
- ✅ 建立/更新/刪除任務
- ✅ 管理任務列表
- ✅ OAuth 2.0 自動認證與 Token 刷新
- ✅ 從 Google Tasks URL 直接獲取任務
- ✅ 支援任務完成狀態管理

## 安裝依賴

```bash
pip install -r requirements.txt
```

或單獨安裝：

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 設定步驟

### 1. 建立 Google Cloud 專案並啟用 Tasks API

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 **Google Tasks API**：
   - 導航至「API 和服務」>「程式庫」
   - 搜尋「Google Tasks API」
   - 點擊「啟用」

### 2. 建立 OAuth 2.0 憑證

1. 導航至「API 和服務」>「憑證」
2. 點擊「建立憑證」>「OAuth 用戶端 ID」
3. 應用程式類型選擇「桌面應用程式」
4. 輸入名稱（例如：「五常系統 Google Tasks 整合」）
5. 點擊「建立」
6. 下載 JSON 憑證檔案
7. 將憑證檔案重新命名為 `google_credentials.json` 並放置在專案根目錄

### 3. 設定環境變數（可選）

```powershell
# 設定 OAuth 憑證路徑（可選，預設為 ./google_credentials.json）
$env:WUCHANG_GOOGLE_CREDENTIALS_PATH = "C:\path\to\google_credentials.json"

# 設定 Token 儲存路徑（可選，預設為 ./google_token.json）
$env:WUCHANG_GOOGLE_TOKEN_PATH = "C:\path\to\google_token.json"
```

## 使用方式

### 基本使用

```python
from google_tasks_integration import get_google_tasks_integration

# 獲取整合實例
integration = get_google_tasks_integration()

# 列出所有任務列表
task_lists = integration.list_task_lists()
for task_list in task_lists:
    print(f"{task_list.title} (ID: {task_list.id})")

# 列出特定任務列表的任務
if task_lists:
    tasks = integration.list_tasks(task_lists[0].id)
    for task in tasks:
        print(f"{task.title} - {task.status}")
```

### 建立任務

```python
# 建立新任務列表
new_list = integration.create_task_list("工作清單")

# 建立新任務
task = integration.create_task(
    task_list_id=new_list.id,
    title="完成系統整合",
    notes="整合 Google Tasks API",
    due="2026-01-31T23:59:59Z"  # RFC3339 格式
)
```

### 更新任務

```python
# 更新任務標題和狀態
updated_task = integration.update_task(
    task_list_id=task_list_id,
    task_id=task_id,
    title="更新後的標題",
    status="completed"  # 標記為完成
)

# 或使用便捷方法
completed_task = integration.complete_task(task_list_id, task_id)
```

### 從 URL 獲取任務

```python
# 從 Google Tasks URL 獲取任務
task_url = "https://jules.google.com/task/9554046612705221251"
task = integration.get_task_by_url(task_url)

if task:
    print(f"任務標題: {task.title}")
    print(f"狀態: {task.status}")
    if task.notes:
        print(f"備註: {task.notes}")
```

### 刪除任務

```python
# 刪除任務
success = integration.delete_task(task_list_id, task_id)
```

## API 端點整合

模組已整合到 `local_control_center.py`，提供以下 API 端點：

### GET /api/google-tasks/lists
列出所有任務列表

### GET /api/google-tasks/lists/{list_id}
獲取特定任務列表

### POST /api/google-tasks/lists
建立新任務列表
```json
{
  "title": "任務列表名稱"
}
```

### GET /api/google-tasks/lists/{list_id}/tasks
列出任務列表中的所有任務
- 查詢參數：`show_completed` (true/false)

### GET /api/google-tasks/lists/{list_id}/tasks/{task_id}
獲取特定任務

### POST /api/google-tasks/lists/{list_id}/tasks
建立新任務
```json
{
  "title": "任務標題",
  "notes": "任務備註（可選）",
  "due": "2026-01-31T23:59:59Z（可選，RFC3339 格式）"
}
```

### PUT /api/google-tasks/lists/{list_id}/tasks/{task_id}
更新任務
```json
{
  "title": "新標題（可選）",
  "notes": "新備註（可選）",
  "status": "completed" 或 "needsAction（可選）",
  "due": "2026-01-31T23:59:59Z（可選）"
}
```

### DELETE /api/google-tasks/lists/{list_id}/tasks/{task_id}
刪除任務

### POST /api/google-tasks/tasks/from-url
從 URL 獲取任務
```json
{
  "url": "https://jules.google.com/task/9554046612705221251"
}
```

## OAuth 認證流程

首次使用時，系統會自動開啟瀏覽器進行 OAuth 授權：

1. 執行任何 API 操作時，如果尚未授權，會自動啟動 OAuth 流程
2. 瀏覽器會開啟 Google 登入頁面
3. 選擇要授權的 Google 帳號
4. 確認授權權限
5. Token 會自動儲存到 `google_token.json`
6. 後續使用時會自動使用已儲存的 Token
7. Token 過期時會自動刷新

## 注意事項

### 安全性

- `google_credentials.json` 和 `google_token.json` 包含敏感資訊，請勿提交到版本控制系統
- 建議將這些檔案加入 `.gitignore`
- Token 檔案會自動刷新，無需手動管理

### 合規性

- 本系統已完成 Google for Nonprofits 驗證
- 所有 API 操作均遵循 Google API 使用規範
- 不儲存任何個資（可究責自然人除外）

### 錯誤處理

所有 API 操作都可能拋出異常，建議使用 try-except 處理：

```python
try:
    task = integration.get_task_by_url(task_url)
except Exception as e:
    print(f"錯誤: {e}")
```

## 疑難排解

### 問題：ImportError: No module named 'google.auth'

**解決方案**：安裝 Google API Client Library
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 問題：FileNotFoundError: 找不到 OAuth 憑證檔案

**解決方案**：
1. 確認已從 Google Cloud Console 下載 OAuth 憑證
2. 將憑證檔案命名為 `google_credentials.json`
3. 放置在專案根目錄，或設定 `WUCHANG_GOOGLE_CREDENTIALS_PATH` 環境變數

### 問題：Token 過期

**解決方案**：系統會自動刷新 Token，如果持續失敗：
1. 刪除 `google_token.json` 檔案
2. 重新執行授權流程

### 問題：權限不足

**解決方案**：
1. 確認已啟用 Google Tasks API
2. 確認 OAuth 憑證設定正確
3. 確認已授權正確的 Google 帳號

## 參考資源

- [Google Tasks API 文件](https://developers.google.com/tasks)
- [Google OAuth 2.0 文件](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
