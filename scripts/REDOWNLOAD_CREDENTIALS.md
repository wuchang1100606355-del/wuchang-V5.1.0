# 重新下載憑證檔案

## 您的客戶端 ID

```
581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com
```

## 快速重新下載步驟

### 步驟 1: 前往憑證頁面

1. 開啟瀏覽器，前往：
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. 確認已登入您的 Google Workspace 帳號
3. 確認已選擇正確的專案

### 步驟 2: 找到您的 OAuth 用戶端 ID

1. 在憑證列表中，找到客戶端 ID 為：
   ```
   581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com
   ```
2. 或找到名稱為「五常系統 Google Tasks 整合」的憑證

### 步驟 3: 下載憑證檔案

**方式 A: 從憑證列表下載**
1. 在憑證列表中，找到您的 OAuth 用戶端 ID
2. 點擊右側的**下載圖示（⬇️）**
3. 檔案會自動下載

**方式 B: 從詳情頁面下載**
1. 點擊憑證名稱進入詳情頁面
2. 在詳情頁面中，找到「下載 JSON」按鈕
3. 點擊下載

### 步驟 4: 確認下載

下載的檔案名稱應該是：
```
client_secret_581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com.json
```

### 步驟 5: 複製到專案目錄

**使用命令列（如果檔案在下載資料夾）：**
```powershell
Copy-Item "$env:USERPROFILE\Downloads\client_secret_581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com.json" "C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json"
```

**或手動操作：**
1. 找到下載的檔案
2. 複製到：`C:\wuchang V5.1.0\wuchang-V5.1.0\`
3. 重新命名為：`google_credentials.json`

## 驗證檔案

下載後，確認檔案內容包含您的客戶端 ID：

```json
{
  "installed": {
    "client_id": "581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com",
    "project_id": "...",
    ...
  }
}
```

## 完成後

設定好憑證檔案後，執行：

```powershell
python complete_authorization_and_setup.py
```

或

```powershell
python full_setup_and_authorization.py
```

## 如果找不到憑證

如果憑證列表中沒有這個客戶端 ID，可能需要：

1. **重新建立 OAuth 用戶端 ID**
   - 前往：https://console.cloud.google.com/apis/credentials
   - 點擊「建立憑證」→「OAuth 用戶端 ID」
   - 應用程式類型：選擇「桌面應用程式」
   - 名稱：輸入「五常系統 Google Tasks 整合」
   - 點擊「建立」
   - 下載新的憑證檔案

2. **確認專案正確**
   - 確認已選擇正確的 Google Cloud 專案
   - 確認 Google Tasks API 已啟用
