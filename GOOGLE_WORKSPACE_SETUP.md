# Google Workspace 非營利版設定指南

## 優勢說明

使用 Google Workspace 非營利版設定 Google Tasks API 有以下優勢：

### ✅ 內部應用程式（推薦）

1. **更快速**：不需要 Google 驗證流程
2. **更安全**：僅限您的組織內使用
3. **更簡單**：不需要公開應用程式資訊
4. **免費**：Google Workspace 非營利版完全免費

### 與外部應用程式的差異

| 項目 | 內部應用程式 | 外部應用程式 |
|------|------------|------------|
| 驗證需求 | ❌ 不需要 | ✅ 需要 Google 驗證 |
| 使用範圍 | 僅限組織內 | 可公開使用 |
| 設定時間 | 約 3-5 分鐘 | 約 10-15 分鐘 |
| 安全性 | 更高 | 較低 |

## 設定步驟（Google Workspace 非營利版）

### 步驟 1: 建立專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 確認使用您的 Google Workspace 帳號登入
3. 建立新專案或選擇現有專案
4. 專案名稱：例如「五常系統 Google Tasks」

### 步驟 2: 啟用 Google Tasks API

1. 前往「API 和服務」→「程式庫」
2. 搜尋「Google Tasks API」
3. 點擊「啟用」

### 步驟 3: 設定 OAuth 同意畫面（內部）

1. 前往「API 和服務」→「OAuth 同意畫面」
2. **選擇「內部」**（重要！）
3. 點擊「建立」
4. 填寫資訊：
   - **應用程式名稱**：五常系統
   - **使用者支援電子郵件**：選擇您的 Google Workspace 電子郵件
   - **開發人員聯絡資訊**：輸入您的 Google Workspace 電子郵件
   - **授權網域**：自動顯示您的 Google Workspace 網域
5. 點擊「儲存並繼續」
6. 在「範圍」頁面，點擊「儲存並繼續」（使用預設）
7. 在「摘要」頁面，點擊「返回資訊主頁」

### 步驟 4: 建立 OAuth 用戶端 ID

1. 前往「API 和服務」→「憑證」
2. 點擊「建立憑證」→「OAuth 用戶端 ID」
3. 應用程式類型：選擇「桌面應用程式」
4. 名稱：輸入「五常系統 Google Tasks 整合」
5. 點擊「建立」
6. 下載 JSON 憑證檔案

### 步驟 5: 放置憑證檔案

1. 將下載的 JSON 檔案重新命名為：`google_credentials.json`
2. 放置在專案目錄：`C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json`

## 權限說明

### Google Workspace 非營利版權限

- ✅ 可以使用所有 Google API（包括 Google Tasks API）
- ✅ 可以使用內部應用程式（不需要驗證）
- ✅ 完全免費
- ✅ 無使用限制

### 應用程式權限範圍

設定完成後，應用程式可以：
- ✅ 讀取 Google Tasks 任務
- ✅ 建立/更新/刪除任務
- ✅ 管理任務列表
- ✅ 僅限您的 Google Workspace 組織內使用

## 常見問題

### Q: 為什麼選擇「內部」而不是「外部」？

A: 因為您有 Google Workspace 非營利版：
- 不需要 Google 驗證流程（更快速）
- 僅限組織內使用（更安全）
- 不需要公開應用程式資訊

### Q: 如果選擇「外部」會怎樣？

A: 需要：
- Google 驗證（可能需要幾天時間）
- 公開應用程式資訊
- 更複雜的設定流程

### Q: 其他組織成員可以使用嗎？

A: 如果選擇「內部」：
- 僅限您的 Google Workspace 組織內的成員可以使用
- 需要授權才能存取

### Q: 需要付費嗎？

A: 不需要，Google Workspace 非營利版完全免費，包括：
- Google Tasks API
- 所有 Google API
- 無使用限制

## 驗證設定

設定完成後，可以測試：

```powershell
# 測試獲取任務
python get_jules_task_direct.py "https://jules.google.com/task/18167513009276525148"
```

如果成功，表示設定完成！

## 相關文件

- `USER_ACTION_REQUIRED.md` - 詳細操作步驟
- `GOOGLE_TASKS_QUICK_SETUP.md` - 快速設定指南
- `SETUP_AND_WORKFLOW_GUIDE.md` - 完整工作流程
