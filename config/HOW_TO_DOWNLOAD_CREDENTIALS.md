# 如何下載 OAuth 憑證 JSON 檔案

## 問題：找不到 JSON 檔案

如果您在 Google Cloud Console 下載了憑證檔案但找不到，請按照以下步驟操作：

## 方法 1: 重新下載（推薦）

### 步驟 1: 前往憑證頁面

1. 開啟瀏覽器，前往：
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. 確認已登入您的 Google Workspace 帳號

### 步驟 2: 找到您的 OAuth 用戶端 ID

1. 在憑證列表中，找到您建立的 OAuth 用戶端 ID
2. 名稱應該是：「五常系統 Google Tasks 整合」或類似
3. 如果看不到，確認：
   - 已選擇正確的專案
   - 已建立 OAuth 用戶端 ID

### 步驟 3: 下載憑證檔案

**方式 A: 從憑證列表下載**
1. 在憑證列表中，找到您的 OAuth 用戶端 ID
2. 點擊右側的**下載圖示（⬇️）**
3. 檔案會自動下載

**方式 B: 從詳情頁面下載**
1. 點擊憑證名稱進入詳情頁面
2. 在詳情頁面中，找到「下載 JSON」按鈕
3. 點擊下載

### 步驟 4: 確認下載位置

下載的檔案通常會儲存在：

**Windows:**
- `C:\Users\您的使用者名稱\Downloads`
- `C:\Users\您的使用者名稱\下載`
- 或瀏覽器設定的下載資料夾

**檢查方式：**
1. 開啟檔案總管
2. 前往「下載」資料夾
3. 尋找最近下載的 JSON 檔案
4. 檔案名稱可能是：
   - `client_secret_XXXXXX.json`
   - 或其他類似名稱

### 步驟 5: 複製到專案目錄

1. 找到下載的 JSON 檔案
2. 將檔案重新命名為：`google_credentials.json`
3. 複製或移動到專案目錄：
   ```
   C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json
   ```

## 方法 2: 使用檔案搜尋

### Windows 搜尋

1. 按 `Win + S` 開啟搜尋
2. 搜尋：`client_secret` 或 `credentials`
3. 選擇「檔案」標籤
4. 查看搜尋結果中的 JSON 檔案

### 檔案總管搜尋

1. 開啟檔案總管
2. 前往「下載」資料夾
3. 在搜尋框中輸入：`*.json`
4. 按修改日期排序，查看最新的檔案

## 方法 3: 檢查瀏覽器下載記錄

### Chrome/Edge
1. 按 `Ctrl + J` 開啟下載頁面
2. 查看最近的下載檔案
3. 點擊「在資料夾中顯示」找到檔案位置

### Firefox
1. 按 `Ctrl + Shift + Y` 開啟下載頁面
2. 查看最近的下載檔案
3. 右鍵點擊檔案 → 「在資料夾中顯示」

## 驗證憑證檔案

下載後，請確認檔案內容正確：

1. 用文字編輯器開啟 JSON 檔案
2. 確認包含以下內容：
   ```json
   {
     "installed": {
       "client_id": "...",
       "project_id": "...",
       "auth_uri": "...",
       "token_uri": "...",
       "client_secret": "..."
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

### Q: 下載按鈕在哪裡？

A: 
- 在憑證列表中，每個憑證右側都有下載圖示（⬇️）
- 或點擊憑證名稱進入詳情頁面，在詳情頁面有「下載 JSON」按鈕

### Q: 下載的檔案名稱是什麼？

A: 
- 通常是 `client_secret_XXXXXX.json`
- 其中 `XXXXXX` 是隨機字串
- 您可以重新命名為 `google_credentials.json`

### Q: 檔案下載到哪裡了？

A: 
- 通常是瀏覽器的預設下載資料夾
- Windows 預設：`C:\Users\您的使用者名稱\Downloads`
- 可以檢查瀏覽器的下載設定

### Q: 可以重新下載嗎？

A: 
- 可以，隨時可以從 Google Cloud Console 重新下載
- 不會影響已建立的憑證

## 快速檢查清單

- [ ] 已前往 Google Cloud Console 憑證頁面
- [ ] 已找到 OAuth 用戶端 ID
- [ ] 已點擊下載按鈕
- [ ] 已確認檔案下載完成
- [ ] 已在「下載」資料夾中找到 JSON 檔案
- [ ] 已將檔案重新命名為 `google_credentials.json`
- [ ] 已複製到專案目錄：`C:\wuchang V5.1.0\wuchang-V5.1.0\`

## 完成後

確認檔案已放置在正確位置後，可以：

1. **驗證檔案**：
   ```powershell
   python help_find_credentials_json.py
   ```

2. **繼續安裝**：
   ```powershell
   python auto_setup_google_tasks.py --auto
   ```

## 需要協助？

如果仍然找不到檔案，請：

1. 檢查瀏覽器的下載設定
2. 確認下載是否被瀏覽器阻擋
3. 嘗試使用不同的瀏覽器下載
4. 檢查防毒軟體是否阻擋下載
