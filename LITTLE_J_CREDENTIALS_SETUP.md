# 小J代理執行憑證設定指南

## 概述

本指南說明如何授予小J（Little J）最高權限，並代理執行 Google OAuth 憑證設定和後續作業。

## 快速開始

### 方式 1：自動執行（推薦）

```bash
python little_j_setup_credentials_now.py
```

此腳本會：
1. 自動搜尋並設定憑證檔案
2. 執行 OAuth 授權流程
3. 完成後續作業

### 方式 2：完整流程（包含權限管理）

```bash
python full_agent_setup_credentials_complete.py
```

此腳本會：
1. 檢查並啟動控制中心（如果未運行）
2. 自動登入
3. 請求並獲得 full_agent 權限
4. 執行憑證設定
5. 執行授權和後續作業

## 手動設定步驟

如果自動腳本無法完成，請按照以下步驟手動設定：

### 步驟 1：下載憑證檔案

1. 前往 Google Cloud Console：
   https://console.cloud.google.com/apis/credentials

2. 找到 OAuth 用戶端 ID：
   - 名稱: Wuchang-life
   - 客戶端 ID: `581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com`

3. 點擊下載按鈕（⬇️）下載 JSON 檔案

4. 下載的檔案名稱通常是：
   `client_secret_581281764864-*.json`

### 步驟 2：複製並重新命名憑證檔案

將下載的檔案複製到專案目錄並重新命名：

**Windows PowerShell:**
```powershell
Copy-Item "$env:USERPROFILE\Downloads\client_secret_*.json" "C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json"
```

**或手動操作：**
1. 找到下載的檔案（通常在 `C:\Users\您的使用者名稱\Downloads`）
2. 複製到 `C:\wuchang V5.1.0\wuchang-V5.1.0\`
3. 重新命名為 `google_credentials.json`

### 步驟 3：執行授權流程

```bash
python complete_authorization_and_setup.py
```

此腳本會：
- 開啟瀏覽器進行 OAuth 授權
- 完成授權後儲存 token
- 驗證設定是否成功

## 權限管理

### 授予 full_agent 權限

如果需要通過控制中心授予最高權限：

1. **確保控制中心運行：**
   ```bash
   python local_control_center.py
   ```

2. **建立授權配置檔案：**
   建立 `auto_auth_config.json`：
   ```json
   {
     "account_id": "your_account_id",
     "pin": "your_pin",
     "auto_approve": true,
     "default_permission": "full_agent",
     "default_ttl_hours": 24
   }
   ```

3. **執行授權腳本：**
   ```bash
   python grant_little_j_full_agent_for_credentials.py
   ```

## 驗證設定

設定完成後，可以使用以下腳本驗證：

```bash
# 測試 Google Tasks API
python get_jules_task_direct.py "https://jules.google.com/task/2903235408856978280"

# 檢查授權狀態
python check_google_task_progress.py "https://jules.google.com/task/2903235408856978280"
```

## 故障排除

### 問題 1：控制中心未運行

**解決方案：**
```bash
# 啟動控制中心
python local_control_center.py

# 或使用啟動腳本
start_servers.bat
```

### 問題 2：找不到憑證檔案

**解決方案：**
1. 確認已從 Google Cloud Console 下載憑證檔案
2. 檢查下載資料夾：`C:\Users\您的使用者名稱\Downloads`
3. 使用 `download_credentials_from_console.py` 自動搜尋

### 問題 3：OAuth 授權失敗

**解決方案：**
1. 確認憑證檔案路徑正確
2. 檢查 Google Cloud Console 中的 OAuth 同意畫面設定
3. 確認已啟用 Google Tasks API
4. 重新執行 `complete_authorization_and_setup.py`

### 問題 4：權限請求未核准

**解決方案：**
1. 檢查 `auto_auth_config.json` 中的 `auto_approve` 設定
2. 手動核准權限請求：
   - 通過控制中心 API：`POST /api/authz/requests/approve`
   - 或使用管理介面

## 相關檔案

- `little_j_setup_credentials_now.py` - 直接執行憑證設定（不依賴控制中心）
- `full_agent_setup_credentials_complete.py` - 完整流程（包含權限管理）
- `grant_little_j_full_agent_for_credentials.py` - 授予最高權限
- `download_credentials_from_console.py` - 搜尋並設定憑證檔案
- `complete_authorization_and_setup.py` - 執行 OAuth 授權和後續作業
- `QUICK_SETUP_CREDENTIALS.md` - 快速設定指南

## 注意事項

1. **憑證檔案安全：**
   - 不要將 `google_credentials.json` 提交到版本控制系統
   - 妥善保管憑證檔案，避免洩露

2. **權限管理：**
   - `full_agent` 權限具有最高權限，請謹慎使用
   - 建議設定適當的 TTL（生存時間）

3. **Google Workspace for Nonprofits：**
   - 本系統已通過 Google for Nonprofits 驗證
   - OAuth 同意畫面應設定為「內部」用戶類型

## 後續作業

設定完成後，可以使用：

- **讀取 Google Tasks：**
  ```bash
  python get_jules_task_direct.py <task_url>
  ```

- **上傳差異報告：**
  ```bash
  python upload_diff_to_jules.py --auto-upload
  ```

- **從 Google Tasks 同步檔案：**
  ```bash
  python sync_from_google_task.py <task_url> <target_file>
  ```
