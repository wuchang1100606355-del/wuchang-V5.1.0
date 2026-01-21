# JULES 任務訪問指南

## 任務 URL

您提供的任務 URL：
```
https://jules.google.com/task/18167513009276525148
```

任務 ID: `18167513009276525148`

## 訪問方式

### 方式 1: 直接瀏覽器訪問（推薦）

1. 在瀏覽器中開啟：https://jules.google.com/task/18167513009276525148
2. 登入您的 Google 帳號
3. 查看任務內容

### 方式 2: 通過 Google Tasks API（需要設定）

如果需要通過 API 自動獲取任務內容，需要先設定 OAuth 憑證：

#### 設定步驟

1. **建立 Google Cloud 專案**
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)
   - 建立新專案或選擇現有專案

2. **啟用 Google Tasks API**
   - 在 API 庫中搜尋 "Google Tasks API"
   - 啟用該 API

3. **建立 OAuth 2.0 憑證**
   - 前往「憑證」頁面
   - 建立 OAuth 2.0 用戶端 ID
   - 應用程式類型選擇「桌面應用程式」
   - 下載憑證 JSON 檔案

4. **儲存憑證**
   - 將下載的 JSON 檔案重新命名為 `google_credentials.json`
   - 放置在專案根目錄：`C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json`

5. **執行授權流程**
   ```powershell
   python google_tasks_integration.py
   ```
   - 首次執行會開啟瀏覽器要求授權
   - 授權後會自動儲存 token

6. **獲取任務**
   ```powershell
   python get_jules_task_direct.py "https://jules.google.com/task/18167513009276525148"
   ```

### 方式 3: 通過控制中心 API

如果控制中心正在運行且已設定 OAuth：

```powershell
# 檢查控制中心狀態
python -c "import requests; r = requests.get('http://127.0.0.1:8788/api/local/health'); print('狀態:', r.status_code)"

# 通過 API 獲取任務
python get_jules_task.py "https://jules.google.com/task/18167513009276525148"
```

## 相關文件

- `GOOGLE_TASKS_QUICK_SETUP.md` - Google Tasks API 快速設定指南
- `GOOGLE_TASKS_INTEGRATION.md` - Google Tasks 整合詳細說明

## 當前狀態

根據檢查結果：
- ❌ OAuth 憑證未設定
- ❌ 控制中心連接有問題
- ✅ 任務 URL 格式正確

## 建議

1. **立即查看任務**：直接在瀏覽器中開啟 URL
2. **設定 API 訪問**：如需自動化處理，請參考 `GOOGLE_TASKS_QUICK_SETUP.md`
3. **手動複製內容**：如果任務內容需要處理，可以手動複製到本地檔案

## 任務內容處理

如果任務包含需要執行的指令或檔案內容，您可以：

1. **手動複製任務內容**
2. **儲存到本地檔案**
3. **使用現有工具處理**

例如，如果任務包含檔案同步指令：
```powershell
# 手動執行指令
python sync_all_profiles.py
```

或如果任務包含配置內容：
```powershell
# 使用 sync_from_google_task.py（需要先設定 OAuth）
python sync_from_google_task.py "https://jules.google.com/task/18167513009276525148" target_file.txt
```
