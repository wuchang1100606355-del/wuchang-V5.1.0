# Google Workspace 應用軟體全自動設定指南

**建立時間：** 2026-01-20  
**狀態：** ✅ 已建立自動設定工具

---

## 📋 概述

根據授權文件（`LITTLE_J_CREDENTIALS_SETUP.md` 和 `MULTIMEDIA_AI_FEATURES.md`）自動設定 Google Workspace 應用軟體整合。

---

## 🚀 快速開始

### 執行自動設定腳本

```bash
python scripts/auto_setup_google_workspace.py
```

此腳本會自動：
1. ✅ 檢查授權文件
2. ✅ 檢查 Python 套件
3. ✅ 檢查 Google OAuth 憑證
4. ✅ 檢查服務帳戶
5. ✅ 建立配置檔案
6. ✅ 建立 OAuth 設定腳本
7. ✅ 建立 API 檢查腳本

---

## 📦 自動設定項目

### 1. Google OAuth 憑證設定

**檢查項目：**
- OAuth 憑證檔案是否存在
- 憑證格式是否正確

**設定資訊：**
- OAuth 應用名稱：`Wuchang-life`
- 客戶端 ID：`581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com`
- 憑證檔案：`google_credentials.json`
- Token 檔案：`google_token.json`

### 2. 服務帳戶設定

**檢查項目：**
- 服務帳戶金鑰是否存在
- 服務帳戶格式是否正確

**設定資訊：**
- 服務帳戶：`littlej-sa@my-j-483304.iam.gserviceaccount.com`
- 金鑰檔案：`config/gcp/littlej-sa.json`
- 專案 ID：`my-j-483304`

### 3. Google Workspace APIs 設定

**需要啟用的 API：**
- `drive.googleapis.com` - Google Drive API v3
- `docs.googleapis.com` - Google Docs API v1
- `sheets.googleapis.com` - Google Sheets API v4
- `gmail.googleapis.com` - Gmail API v1
- `calendar-json.googleapis.com` - Calendar API v3
- `aiplatform.googleapis.com` - Vertex AI Platform
- `cloudbuild.googleapis.com` - Cloud Build API

### 4. Python 套件檢查

**必要套件：**
- `google-auth` - Google 認證庫
- `google-auth-oauthlib` - Google OAuth 認證
- `google-api-python-client` - Google API 客戶端
- `google-cloud-aiplatform` - Vertex AI Platform

### 5. 配置檔案建立

**自動建立的配置檔案：**
- `config/google_workspace_config.json` - Google Workspace 完整配置

**自動建立的腳本：**
- `scripts/complete_authorization_and_setup.py` - OAuth 授權腳本
- `scripts/check_google_apis_status.py` - API 狀態檢查腳本

---

## 📁 建立的檔案

### 配置檔案

| 檔案 | 位置 | 說明 |
|------|------|------|
| `config/google_workspace_config.json` | config/ | Google Workspace 完整配置 |
| `google_credentials.json` | 根目錄 | OAuth 憑證（需手動下載） |
| `google_token.json` | 根目錄 | OAuth Token（自動產生） |
| `config/gcp/littlej-sa.json` | config/gcp/ | 服務帳戶金鑰（需手動下載） |

### 腳本檔案

| 檔案 | 位置 | 說明 |
|------|------|------|
| `scripts/auto_setup_google_workspace.py` | scripts/ | 自動設定主腳本 |
| `scripts/complete_authorization_and_setup.py` | scripts/ | OAuth 授權腳本 |
| `scripts/check_google_apis_status.py` | scripts/ | API 狀態檢查腳本 |

---

## 🔧 設定步驟

### 步驟 1：執行自動設定

```bash
python scripts/auto_setup_google_workspace.py
```

### 步驟 2：安裝缺少的 Python 套件（如需要）

```bash
pip install google-auth google-auth-oauthlib google-api-python-client google-cloud-aiplatform
```

### 步驟 3：下載 Google OAuth 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. 找到 OAuth 用戶端 ID：`Wuchang-life`
3. 下載 JSON 憑證檔案
4. 儲存為：`google_credentials.json`

### 步驟 4：下載服務帳戶金鑰

1. 前往 [IAM & Admin - Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. 找到服務帳戶：`littlej-sa`
3. 建立並下載 JSON 金鑰
4. 儲存為：`config/gcp/littlej-sa.json`

### 步驟 5：執行 OAuth 授權流程

```bash
python scripts/complete_authorization_and_setup.py
```

### 步驟 6：啟用必要的 API

前往 [API Library](https://console.cloud.google.com/apis/library) 啟用以下 API：
- Google Drive API
- Google Docs API
- Google Sheets API
- Gmail API
- Calendar API
- Vertex AI Platform API

或使用 gcloud CLI：

```bash
gcloud services enable drive.googleapis.com
gcloud services enable docs.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable calendar-json.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

---

## ✅ 驗證設定

### 檢查設定狀態

執行自動設定腳本會產生設定報告：

```
reports/google_workspace_auto_setup_report.json
```

### 測試 Google Workspace 功能

設定完成後，可以測試：

1. **搜尋 Google Workspace 檔案**
   ```bash
   python scripts/search_google_workspace_files.py
   ```

2. **檢查 API 狀態**
   ```bash
   python scripts/check_google_apis_status.py
   ```

3. **測試 OAuth 認證**
   ```bash
   python scripts/check_google_workspace_setup.py
   ```

---

## 📊 設定結果

執行自動設定腳本後，會顯示以下結果：

### ✅ 完成的項目

- 授權文件檢查
- Python 套件檢查
- Google OAuth 憑證檢查
- 服務帳戶檢查
- 配置檔案建立
- OAuth 設定腳本建立
- API 檢查腳本建立
- 設定報告產生

### ⚠️ 需要手動完成的項目

根據檢查結果，可能需要：

1. **下載 Google OAuth 憑證**（如果不存在）
2. **下載服務帳戶金鑰**（如果不存在）
3. **安裝 Python 套件**（如果缺少）
4. **執行 OAuth 授權流程**
5. **啟用必要的 API**

---

## 🔄 同步規則

根據系統同步規則，所有寫入操作會同時寫入：
- 雲端空間：`G:\共用雲端硬碟\五常雲端空間`
- 外接硬碟：`E:\wuchang V5.1.0`（如果存在）

---

## 📝 授權資訊

**授權人：** 江政隆 F1247717117（系統創始人）  
**授權對象：** 五常非營利組織  
**系統版本：** 小 j AI 控制台 v5.1.0  
**遵循條款：** Google Workspace for Nonprofits 使用條款

---

## 🔗 相關檔案

- **自動設定腳本：** `scripts/auto_setup_google_workspace.py`
- **OAuth 授權腳本：** `scripts/complete_authorization_and_setup.py`
- **API 檢查腳本：** `scripts/check_google_apis_status.py`
- **配置檔案：** `config/google_workspace_config.json`
- **設定報告：** `reports/google_workspace_auto_setup_report.json`
- **本指南：** `reports/GOOGLE_WORKSPACE_AUTO_SETUP_GUIDE.md`

---

**建立時間：** 2026-01-20  
**最後更新：** 2026-01-20


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:04:41
---
