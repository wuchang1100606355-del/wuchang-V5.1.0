# Google Workspace 檔案搜尋工具使用指南

## 📋 概述

`search_google_workspace_files.py` 是一個用於從 Google Workspace 組織空間中搜尋檔案的 Python 腳本。

## 🎯 功能

- ✅ 使用 Google Drive API 搜尋檔案
- ✅ 支援多種搜尋條件：
  - 檔名關鍵字
  - 檔案類型（MIME type）
  - 修改時間範圍
  - 特定資料夾
  - 擁有者
  - 共享狀態
- ✅ 顯示檔案詳細資訊
- ✅ 匯出搜尋結果為 JSON 格式

## 📦 前置需求

### 1. Python 套件

安裝必要的 Google API 套件：

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Google Cloud Console 設定

#### 步驟 1：建立專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Drive API

#### 步驟 2：建立 OAuth 2.0 憑證

1. 前往「API 和服務」>「憑證」
2. 點擊「建立憑證」>「OAuth 用戶端 ID」
3. 選擇應用程式類型：「桌面應用程式」
4. 設定名稱（例如：Google Workspace 檔案搜尋）
5. 下載憑證 JSON 檔案

#### 步驟 3：設定 OAuth 同意畫面

1. 前往「OAuth 同意畫面」
2. 選擇使用者類型（內部或外部）
3. 填寫應用程式資訊
4. 新增範圍：`https://www.googleapis.com/auth/drive.readonly`
5. 儲存並繼續

#### 步驟 4：儲存憑證檔案

將下載的憑證 JSON 檔案重新命名為 `google_credentials.json`，並放置在專案根目錄：

```
五常雲端空間/
├── google_credentials.json  ← 放在這裡
├── scripts/
│   └── search_google_workspace_files.py
└── ...
```

## 🚀 使用方法

### 基本使用

```bash
cd scripts
python search_google_workspace_files.py
```

### 搜尋選項

執行腳本後，會提示輸入搜尋條件：

1. **檔名關鍵字**
   - 輸入檔名中的關鍵字（部分匹配）
   - 例如：`報告`、`會議記錄`

2. **檔案類型**
   - 輸入 MIME 類型
   - 常見類型：
     - `application/pdf` - PDF 檔案
     - `application/vnd.google-apps.document` - Google Docs
     - `application/vnd.google-apps.spreadsheet` - Google Sheets
     - `image/jpeg` - JPEG 圖片
     - `image/png` - PNG 圖片
     - `text/plain` - 純文字檔案

3. **修改時間**
   - 輸入天數（例如：`7` 表示 7 天內修改的檔案）

4. **資料夾 ID**
   - 輸入特定資料夾的 ID（留空搜尋全部）

### 搜尋範例

#### 範例 1：搜尋包含「報告」的檔案

```
檔名關鍵字: 報告
檔案類型: （留空）
修改時間：幾天內: （留空）
資料夾 ID: （留空）
```

#### 範例 2：搜尋最近 30 天修改的 PDF 檔案

```
檔名關鍵字: （留空）
檔案類型: application/pdf
修改時間：幾天內: 30
資料夾 ID: （留空）
```

#### 範例 3：搜尋特定資料夾中的 Google Docs

```
檔名關鍵字: （留空）
檔案類型: application/vnd.google-apps.document
修改時間：幾天內: （留空）
資料夾 ID: 1abc123def456ghi789
```

## 📊 輸出結果

### 螢幕輸出

腳本會顯示找到的檔案列表，包含：

- 檔案名稱
- 檔案 ID
- MIME 類型
- 檔案大小
- 修改時間
- 擁有者
- 共享狀態
- 網頁連結

### JSON 匯出

搜尋完成後，可以選擇匯出結果為 JSON 檔案：

- 檔案位置：`reports/google_workspace_search_YYYYMMDD_HHMMSS.json`
- 包含完整的檔案資訊和搜尋時間

## 🔐 認證流程

### 首次使用

1. 執行腳本
2. 如果沒有認證資訊，會自動開啟瀏覽器
3. 登入 Google 帳號
4. 授權應用程式存取 Google Drive
5. 認證資訊會自動儲存為 `google_token.json`

### 後續使用

- 認證資訊已儲存，會自動使用
- 如果 token 過期，會自動重新整理
- 如果重新整理失敗，會要求重新授權

## 📁 檔案結構

```
五常雲端空間/
├── google_credentials.json      # OAuth 2.0 憑證（需手動建立）
├── google_token.json             # 認證 token（自動產生）
├── scripts/
│   └── search_google_workspace_files.py
└── reports/
    └── google_workspace_search_*.json  # 搜尋結果（自動產生）
```

## ⚠️ 注意事項

1. **權限範圍**
   - 腳本使用 `drive.readonly` 權限，只能讀取檔案資訊
   - 不會修改或刪除任何檔案

2. **搜尋限制**
   - Google Drive API 有搜尋結果數量限制
   - 預設最多搜尋 100 個檔案
   - 可在程式碼中調整 `max_results` 參數

3. **認證檔案安全**
   - `google_credentials.json` 和 `google_token.json` 包含敏感資訊
   - 請勿分享或提交到版本控制系統
   - 建議加入 `.gitignore`

4. **組織空間存取**
   - 確保使用的 Google 帳號有權限存取組織空間
   - 某些檔案可能需要特定權限才能搜尋

## 🐛 疑難排解

### 問題 1：找不到認證檔案

**錯誤訊息：**
```
❌ 認證檔案不存在: google_credentials.json
```

**解決方法：**
1. 確認已從 Google Cloud Console 下載憑證
2. 確認檔案名稱正確：`google_credentials.json`
3. 確認檔案位置在專案根目錄

### 問題 2：認證失敗

**錯誤訊息：**
```
❌ OAuth 認證失敗
```

**解決方法：**
1. 確認已啟用 Google Drive API
2. 確認 OAuth 同意畫面已設定
3. 確認憑證類型為「桌面應用程式」
4. 檢查網路連線

### 問題 3：找不到檔案

**可能原因：**
1. 搜尋條件太嚴格
2. 檔案在垃圾桶中（腳本會自動排除）
3. 沒有存取權限
4. 檔案在共享資料夾中，需要調整搜尋條件

### 問題 4：缺少 Python 套件

**錯誤訊息：**
```
❌ 缺少必要的 Google API 套件
```

**解決方法：**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 📝 進階使用

### 修改搜尋參數

可以在程式碼中修改 `build_search_query()` 函數來新增更多搜尋條件：

```python
# 搜尋特定擁有者的檔案
query = build_search_query(owner="user@example.com")

# 搜尋共享的檔案
query = build_search_query(shared=True)

# 組合多個條件
query = build_search_query(
    name="報告",
    mime_type="application/pdf",
    modified_after=datetime.now() - timedelta(days=30)
)
```

### 批次搜尋

可以修改腳本來執行多個搜尋：

```python
search_queries = [
    {"name": "報告", "mime_type": "application/pdf"},
    {"name": "會議", "mime_type": "application/vnd.google-apps.document"},
]

for query_params in search_queries:
    query = build_search_query(**query_params)
    files = search_files(service, query)
    display_files(files)
```

## 🔗 相關資源

- [Google Drive API 文件](https://developers.google.com/drive/api/v3/about-sdk)
- [OAuth 2.0 設定指南](https://developers.google.com/identity/protocols/oauth2)
- [MIME 類型參考](https://developers.google.com/drive/api/v3/mime-types)

## 📞 支援

如有問題，請檢查：
1. Google Cloud Console 設定
2. 認證檔案是否正確
3. Python 套件是否已安裝
4. 網路連線是否正常

---

**建立時間：** 2026-01-20  
**最後更新：** 2026-01-20
