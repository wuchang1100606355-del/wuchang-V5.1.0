# OAuth 憑證快速設定指南

## 選擇應用程式類型

### 對於本地 Python 腳本 → 選擇「電腦版應用程式」

**原因：**
- 我們在本地電腦上運行 Python 腳本
- 需要訪問 Google Tasks API
- 這是桌面應用程式的典型使用場景

## 建立 OAuth 客戶端步驟

1. **選擇應用程式類型**
   - 選擇：**電腦版應用程式** (Desktop application)

2. **填寫名稱**
   - 名稱：`Wuchang-life`（或您喜歡的名稱）

3. **點擊「建立」**

4. **下載憑證檔案**
   - 建立完成後，會顯示客戶端 ID 和客戶端密鑰
   - 點擊「下載 JSON」按鈕
   - 檔案會下載到您的下載資料夾

5. **設定憑證檔案**
   - 將下載的 JSON 檔案複製到專案目錄
   - 重新命名為：`google_credentials.json`

## 如果已有客戶端

如果您已經有 OAuth 客戶端（客戶端 ID: `581281764864-...`）：

1. 前往：https://console.cloud.google.com/apis/credentials?project=wuchang-sbir-project
2. 在憑證列表中，找到您的 OAuth 用戶端 ID
3. 點擊右側的「下載」按鈕（⬇️）
4. 下載的檔案會自動命名為：`client_secret_581281764864-*.json`

## 自動處理

下載完成後，執行：

```bash
python little_j_full_auto_credentials_setup.py
```

腳本會自動：
- 搜尋下載的憑證檔案
- 複製到正確位置
- 執行 OAuth 授權流程

## 使用瀏覽器自動化

如果需要完全自動化：

```bash
python auto_download_credentials_with_browser.py
```

此腳本會：
- 自動開啟瀏覽器
- 導航到憑證頁面
- 等待您點擊下載
- 自動處理下載的檔案
