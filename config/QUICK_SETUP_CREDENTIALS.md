# 快速設定憑證檔案

## 您的憑證檔案

檔案名稱：
```
client_secret_581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com.json
```

## 快速設定步驟

### 步驟 1: 找到檔案

檔案通常在下載資料夾：
- `C:\Users\您的使用者名稱\Downloads`
- 或瀏覽器設定的下載資料夾

**搜尋方式：**
1. 按 `Win + S` 開啟搜尋
2. 搜尋：`client_secret_581281764864`
3. 或搜尋：`4eg0icu55pkmbcirheflhp7fgt7gk499`

### 步驟 2: 複製檔案

**方式 A: 使用檔案總管**
1. 找到檔案
2. 右鍵點擊 → 「複製」
3. 前往：`C:\wuchang V5.1.0\wuchang-V5.1.0\`
4. 右鍵點擊 → 「貼上」
5. 右鍵點擊檔案 → 「重新命名」
6. 重新命名為：`google_credentials.json`

**方式 B: 使用命令列**
```powershell
# 如果檔案在下載資料夾
Copy-Item "$env:USERPROFILE\Downloads\client_secret_581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com.json" "C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json"
```

**方式 C: 使用 Python 腳本**
```powershell
# 提供完整路徑
python setup_credentials_file.py "C:\Users\您的使用者名稱\Downloads\client_secret_581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com.json"
```

### 步驟 3: 驗證檔案

確認檔案已正確放置：
```powershell
# 檢查檔案是否存在
Test-Path "C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json"

# 或使用 Python 驗證
python setup_credentials_file.py --auto
```

## 如果找不到檔案

### 檢查瀏覽器下載記錄

**Chrome/Edge:**
1. 按 `Ctrl + J` 開啟下載頁面
2. 找到 JSON 檔案
3. 點擊「在資料夾中顯示」

**Firefox:**
1. 按 `Ctrl + Shift + Y` 開啟下載頁面
2. 找到 JSON 檔案
3. 右鍵點擊 → 「在資料夾中顯示」

### 重新下載

如果檔案遺失，可以重新下載：

1. 前往：https://console.cloud.google.com/apis/credentials
2. 找到您的 OAuth 用戶端 ID
3. 點擊下載圖示（⬇️）
4. 重新下載檔案

## 完成後

確認檔案已正確放置後，可以繼續執行安裝：

```powershell
python auto_setup_google_tasks.py --auto
```

## 驗證檔案格式

憑證檔案應該包含以下內容：

```json
{
  "installed": {
    "client_id": "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com",
    "project_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "...",
    ...
  }
}
```

或

```json
{
  "web": {
    "client_id": "...",
    "project_id": "...",
    ...
  }
}
```

## 常見問題

### Q: 檔案名稱太長，不好處理？

A: 可以重新命名為 `google_credentials.json`，內容不會改變。

### Q: 複製後需要驗證嗎？

A: 建議驗證，可以使用：
```powershell
python setup_credentials_file.py --auto
```

### Q: 如果檔案在其他位置？

A: 提供完整路徑給腳本：
```powershell
python setup_credentials_file.py "完整路徑\檔案名稱.json"
```
