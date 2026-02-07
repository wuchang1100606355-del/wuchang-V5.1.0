# 小J全自動憑證設定（無人職守，獨斷專行）

## 概述

此腳本授予小J最高權限（full_agent），全自動執行憑證設定任務，包括：
- 自動清理舊憑證檔案
- 自動搜尋並設定新憑證
- 自動執行 OAuth 授權流程
- 完全自動化，無需人工干預

## 使用方式

### 快速開始

```bash
python little_j_full_auto_credentials_setup.py
```

### 配置自動登入（可選）

如果需要通過控制中心獲取 full_agent 權限，請建立 `auto_auth_config.json`：

```json
{
  "account_id": "your_account_id",
  "pin": "your_pin",
  "auto_approve": true,
  "default_permission": "full_agent",
  "default_ttl_hours": 24
}
```

## 功能說明

### 1. 自動清理舊憑證

腳本會自動刪除以下舊檔案：
- `google_credentials.json`
- `google_token.json`
- `client_secret_*.json`

**注意：** 這是「獨斷專行」權限，會直接刪除，不詢問確認。

### 2. 自動搜尋憑證檔案

腳本會在以下位置搜尋憑證檔案：
- `%USERPROFILE%\Downloads`
- `%USERPROFILE%\下載`
- `%USERPROFILE%\Desktop`
- `%USERPROFILE%\桌面`
- 專案目錄

搜尋模式：
- `client_secret_*{CLIENT_ID}*.json`
- `client_secret_*.json`
- `*credentials*.json`
- `*google*.json`

### 3. 自動執行 OAuth 授權

如果找到憑證檔案，腳本會自動執行：
- OAuth 授權流程
- Token 生成
- 驗證設定

### 4. 驗證設定

腳本會自動驗證：
- 憑證檔案是否存在且有效
- Token 檔案是否存在且有效
- 控制中心是否運行

## 執行流程

```
1. 檢查並啟動控制中心（如果需要）
2. 登入並獲取 full_agent 權限（如果配置）
3. 清理舊憑證檔案（獨斷專行）
4. 搜尋並設定新憑證檔案
5. 執行 OAuth 授權流程
6. 驗證設定
7. 生成執行報告
```

## 日誌輸出

腳本會輸出詳細的日誌，包括：
- `[INFO]` - 資訊訊息
- `[OK]` - 成功操作
- `[WARN]` - 警告訊息
- `[ERROR]` - 錯誤訊息

## 故障排除

### 問題 1：憑證檔案未找到

**解決方案：**
1. 手動下載憑證檔案：
   - 前往：https://console.cloud.google.com/apis/credentials
   - 下載 OAuth 憑證 JSON 檔案
   - 放置到下載資料夾或專案目錄

2. 重新執行腳本，它會自動搜尋並設定

### 問題 2：登入失敗

**解決方案：**
- 登入是可選的，不影響憑證設定
- 如果需要 full_agent 權限，請檢查 `auto_auth_config.json` 配置
- 或手動登入控制中心後再執行腳本

### 問題 3：OAuth 授權失敗

**解決方案：**
1. 確認憑證檔案格式正確
2. 檢查 Google Cloud Console 中的 OAuth 設定
3. 確認已啟用 Google Tasks API
4. 重新執行授權流程

## 注意事項

1. **獨斷專行權限：**
   - 腳本會自動刪除舊憑證檔案，不詢問確認
   - 請確保已備份重要檔案

2. **憑證檔案安全：**
   - 不要將憑證檔案提交到版本控制系統
   - 妥善保管憑證檔案，避免洩露

3. **自動核准：**
   - 如果配置 `auto_approve: true`，權限請求會自動核准
   - 請謹慎使用此功能

## 相關檔案

- `little_j_full_auto_credentials_setup.py` - 全自動憑證設定腳本
- `auto_auth_config.json` - 自動登入配置（可選）
- `google_credentials.json` - Google OAuth 憑證檔案（自動生成）
- `google_token.json` - OAuth Token 檔案（自動生成）

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
