# 獲取 Google Tasks 任務：https://jules.google.com/task/9554046612705221251

## 當前狀態

- ✅ 控制中心：運行中 (http://127.0.0.1:8788/)
- ✅ Google API Client Library：已安裝
- ❌ OAuth 憑證：未設定

## 快速獲取任務的方式

### 方式一：設定 OAuth 憑證後使用（推薦）

#### 步驟 1：建立 OAuth 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立或選擇專案
3. 啟用 **Google Tasks API**
4. 建立 **OAuth 2.0 憑證**（桌面應用程式）
5. 下載 JSON 憑證檔案
6. 重新命名為 `google_credentials.json` 並放置在專案根目錄

#### 步驟 2：執行授權並獲取任務

```bash
python get_google_task_from_url.py "https://jules.google.com/task/9554046612705221251"
```

首次執行會自動開啟瀏覽器進行 OAuth 授權。

### 方式二：通過控制中心 API（需要 OAuth 憑證）

如果已設定 OAuth 憑證，可以使用控制中心 API：

#### PowerShell

```powershell
$body = @{
    url = "https://jules.google.com/task/9554046612705221251"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8788/api/google-tasks/tasks/from-url" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

#### curl

```bash
curl -X POST http://127.0.0.1:8788/api/google-tasks/tasks/from-url \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://jules.google.com/task/9554046612705221251\"}"
```

#### Python

```python
import requests

response = requests.post(
    "http://127.0.0.1:8788/api/google-tasks/tasks/from-url",
    json={"url": "https://jules.google.com/task/9554046612705221251"}
)
print(response.json())
```

### 方式三：在 Python 程式中直接使用

```python
from google_tasks_integration import get_google_tasks_integration

integration = get_google_tasks_integration()
task = integration.get_task_by_url("https://jules.google.com/task/9554046612705221251")

if task:
    print(f"任務標題: {task.title}")
    print(f"狀態: {task.status}")
    if task.notes:
        print(f"備註: {task.notes}")
```

## 詳細設定指引

請參考 `GOOGLE_TASKS_QUICK_SETUP.md` 獲取完整的設定步驟。

## 已建立的工具

1. ✅ `get_google_task_from_url.py` - 便捷獲取工具
2. ✅ `google_tasks_integration.py` - 整合模組
3. ✅ `GOOGLE_TASKS_QUICK_SETUP.md` - 快速設定指南
4. ✅ 控制中心 API 端點：`/api/google-tasks/tasks/from-url`

## 下一步

1. 設定 OAuth 憑證（參考 `GOOGLE_TASKS_QUICK_SETUP.md`）
2. 執行授權流程
3. 獲取任務內容
