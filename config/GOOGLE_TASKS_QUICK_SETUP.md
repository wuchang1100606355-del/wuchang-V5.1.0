# Google Tasks 快速設定指南

## 從 URL 獲取任務：`https://jules.google.com/task/9554046612705221251`

### 當前狀態
- ✅ Google API Client Library：已安裝
- ❌ OAuth 憑證：未設定

## 快速設定步驟

### 步驟 1：建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊專案選擇器，建立新專案或選擇現有專案
3. 專案名稱：例如「五常系統 Google Tasks」

### 步驟 2：啟用 Google Tasks API

1. 在 Google Cloud Console 中，導航至「API 和服務」>「程式庫」
2. 搜尋「Google Tasks API」
3. 點擊「Google Tasks API」結果
4. 點擊「啟用」按鈕

### 步驟 3：建立 OAuth 2.0 憑證

1. 導航至「API 和服務」>「憑證」
2. 點擊「建立憑證」>「OAuth 用戶端 ID」
3. 如果是首次建立，需要先設定「OAuth 同意畫面」：
   - 使用者類型：選擇「外部」（除非您有 Google Workspace）
   - 應用程式名稱：輸入「五常系統」
   - 使用者支援電子郵件：選擇您的電子郵件
   - 開發人員聯絡資訊：輸入您的電子郵件
   - 點擊「儲存並繼續」
   - 範圍：點擊「儲存並繼續」（使用預設）
   - 測試使用者：點擊「儲存並繼續」（可選）
   - 摘要：點擊「返回資訊主頁」
4. 回到「憑證」頁面，點擊「建立憑證」>「OAuth 用戶端 ID」
5. 應用程式類型：選擇「桌面應用程式」
6. 名稱：輸入「五常系統 Google Tasks 整合」
7. 點擊「建立」
8. 下載 JSON 憑證檔案

### 步驟 4：放置憑證檔案

1. 將下載的 JSON 檔案重新命名為 `google_credentials.json`
2. 放置在專案根目錄：`C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json`

### 步驟 5：執行授權

```bash
python get_google_task_from_url.py "https://jules.google.com/task/9554046612705221251"
```

首次執行時會：
1. 自動開啟瀏覽器
2. 要求您登入 Google 帳號
3. 確認授權權限
4. 自動儲存 Token 到 `google_token.json`

## 使用方式

### 方式一：使用便捷工具

```bash
python get_google_task_from_url.py "https://jules.google.com/task/9554046612705221251"
```

### 方式二：使用 API 端點（如果控制中心正在運行）

#### 啟動控制中心

```bash
python local_control_center.py
```

#### 使用 API

**PowerShell:**
```powershell
$body = @{
    url = "https://jules.google.com/task/9554046612705221251"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8788/api/google-tasks/tasks/from-url" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**curl:**
```bash
curl -X POST http://127.0.0.1:8788/api/google-tasks/tasks/from-url \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://jules.google.com/task/9554046612705221251\"}"
```

**Python:**
```python
import requests

response = requests.post(
    "http://127.0.0.1:8788/api/google-tasks/tasks/from-url",
    json={"url": "https://jules.google.com/task/9554046612705221251"}
)
print(response.json())
```

### 方式三：在 Python 程式中使用

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

## 支援的 URL 格式

- `https://jules.google.com/task/{task_id}`
- `https://tasks.google.com/embed/list/{task_list_id}/{task_id}`

## 常見問題

### Q: 授權後 Token 會過期嗎？
A: Token 會自動刷新，無需手動管理。Token 儲存在 `google_token.json`。

### Q: 可以存取多個 Google 帳號的任務嗎？
A: 目前一次只能授權一個帳號。如需切換帳號，刪除 `google_token.json` 並重新授權。

### Q: 如何確認設定是否成功？
A: 執行測試腳本：
```bash
python get_google_task_from_url.py "https://jules.google.com/task/9554046612705221251"
```

### Q: 遇到「權限不足」錯誤？
A: 確認：
1. 已啟用 Google Tasks API
2. OAuth 憑證設定正確
3. 已授權正確的 Google 帳號
4. 該帳號有權限存取該任務

## 相關文件

- `GOOGLE_TASKS_INTEGRATION.md` - 完整整合文件
- `google_tasks_integration.py` - 整合模組原始碼
