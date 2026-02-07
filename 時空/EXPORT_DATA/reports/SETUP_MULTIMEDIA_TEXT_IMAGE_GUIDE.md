# 本系統圖文功能設定指南

**根據授權文件設定圖像與文字處理功能**

---

## 📋 概述

本指南說明如何根據兩份授權文件設定本系統的圖文功能：

1. **LITTLE_J_CREDENTIALS_SETUP.md** - Google OAuth 憑證設定
2. **MULTIMEDIA_AI_FEATURES.md** - 多媒體與 Google Workspace 整合功能

---

## 🚀 快速開始

### 執行自動設定腳本

```bash
python scripts/setup_multimedia_text_image_features.py
```

此腳本會自動：
1. ✅ 檢查授權文件
2. ✅ 檢查 Python 套件
3. ✅ 檢查 Google OAuth 憑證
4. ✅ 檢查服務帳戶設定
5. ✅ 建立上傳資料夾結構
6. ✅ 建立圖文功能配置檔案

---

## 📦 前置需求

### 1. 安裝 Python 套件

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client google-cloud-aiplatform
```

**必要套件：**
- `google-auth` - Google 認證庫
- `google-auth-oauthlib` - Google OAuth 認證
- `google-auth-httplib2` - Google HTTP 認證
- `google-api-python-client` - Google API 客戶端
- `google-cloud-aiplatform` - Vertex AI 平台

---

## 🔑 設定步驟

### 步驟 1：設定 Google OAuth 憑證

#### 1.1 下載憑證檔案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. 找到 OAuth 用戶端 ID：
   - **名稱**: Wuchang-life
   - **客戶端 ID**: `581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com`
3. 點擊下載按鈕（⬇️）下載 JSON 檔案

#### 1.2 複製並重新命名憑證檔案

**Windows PowerShell:**
```powershell
Copy-Item "$env:USERPROFILE\Downloads\client_secret_*.json" "G:\共用雲端硬碟\五常雲端空間\google_credentials.json"
```

**或手動操作：**
1. 找到下載的檔案（通常在 `C:\Users\您的使用者名稱\Downloads`）
2. 複製到專案根目錄：`G:\共用雲端硬碟\五常雲端空間\`
3. 重新命名為：`google_credentials.json`

#### 1.3 執行 OAuth 授權流程

```bash
python scripts/complete_authorization_and_setup.py
```

---

### 步驟 2：設定服務帳戶（用於 Google Workspace APIs）

#### 2.1 下載服務帳戶金鑰

1. 前往 [Google Cloud Console - IAM & Admin](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. 找到服務帳戶：`littlej-sa`
3. 建立並下載 JSON 金鑰檔案

#### 2.2 儲存服務帳戶金鑰

將下載的 JSON 檔案儲存到：
```
G:\共用雲端硬碟\五常雲端空間\config\gcp\littlej-sa.json
```

#### 2.3 設定服務帳戶權限

在 GCP Console 為服務帳戶添加角色：

```bash
# Google Drive
gcloud projects add-iam-policy-binding my-j-483304 \
  --member="serviceAccount:littlej-sa@my-j-483304.iam.gserviceaccount.com" \
  --role="roles/drive.admin"

# Vertex AI
gcloud projects add-iam-policy-binding my-j-483304 \
  --member="serviceAccount:littlej-sa@my-j-483304.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

---

### 步驟 3：啟用必要的 API

在 Google Cloud Console 啟用以下 API：

```bash
# Google Workspace APIs
gcloud services enable drive.googleapis.com
gcloud services enable docs.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable calendar-json.googleapis.com

# Vertex AI APIs
gcloud services enable aiplatform.googleapis.com
```

或透過網頁介面：
1. 前往 [API Library](https://console.cloud.google.com/apis/library)
2. 搜尋並啟用上述 API

---

### 步驟 4：建立資料夾結構

執行設定腳本會自動建立以下資料夾：

```
五常雲端空間/
├── uploads/
│   ├── images/      # 圖片上傳
│   ├── text/        # 文字檔案上傳
│   └── generated/   # AI 生成的圖片
└── containers/
    └── uploads/     # 容器共享上傳資料夾
```

---

## 🎨 圖文功能說明

### 1. 圖片上傳功能

**支援格式：**
- `.jpg`, `.jpeg` - JPEG 圖片
- `.png` - PNG 圖片
- `.gif` - GIF 動畫
- `.bmp` - BMP 圖片

**功能：**
- 多檔案上傳
- 自動複製到 `uploads/images/` 目錄
- 支援 Vertex AI Vision 圖片分析

**使用方式：**
```python
# 圖片會自動儲存到 uploads/images/
# 然後可以呼叫 Vertex AI Vision API 分析
```

---

### 2. AI 圖像生成功能

**模型：** Vertex AI Imagen (`imagegeneration@006`)

**使用方式：**
1. 輸入圖像描述（英文效果較佳）
2. 系統使用 Vertex AI Imagen 生成
3. 圖片儲存至 `uploads/generated/`

**範例提示詞：**
- `A beautiful sunset over mountains` - 山景夕陽
- `Modern minimalist office interior design` - 現代辦公室設計
- `Cute robot assistant with friendly expression` - 可愛機器人助手

**技術實現：**
```python
from vertexai.preview.vision_models import ImageGenerationModel

model = ImageGenerationModel.from_pretrained('imagegeneration@006')
response = model.generate_images(
    prompt='A beautiful sunset over mountains',
    number_of_images=1
)

if response.images:
    img_data = response.images[0]._image_bytes
    with open('uploads/generated/image.png', 'wb') as f:
        f.write(img_data)
```

---

### 3. 圖片分析功能（Vertex AI Vision）

**模型：** `imagetext@001`

**功能：**
- 圖片內容分析
- 物件識別
- 文字提取（OCR）
- 圖片標題生成

**使用方式：**
```python
from vertexai.vision_models import ImageTextModel

model = ImageTextModel.from_pretrained("imagetext@001")
response = model.get_captions(image="uploads/images/image.jpg")
caption = response.captions[0] if response.captions else "無法分析"
```

---

### 4. 文字處理功能

**支援格式：**
- `.txt` - 純文字檔案
- `.pdf` - PDF 文件
- `.docx` - Word 文件

**功能：**
- 文字檔案上傳
- 文字擷取與分析
- 整合 Google Docs API

---

### 5. Google Workspace 整合

**整合服務：**

| 服務 | API | 功能 |
|------|-----|------|
| Google Drive | Drive API v3 | 檔案儲存、分享、協作 |
| Google Docs | Docs API v1 | 文件建立、編輯、匯出 |
| Google Sheets | Sheets API v4 | 試算表自動化 |

**使用範例：**

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 使用服務帳戶認證
creds = service_account.Credentials.from_service_account_file(
    'config/gcp/littlej-sa.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

# 建立 Drive 服務
service = build('drive', 'v3', credentials=creds)

# 上傳圖片到 Google Drive
file_metadata = {'name': 'image.jpg'}
media = MediaFileUpload('uploads/images/image.jpg', mimetype='image/jpeg')
file = service.files().create(body=file_metadata, media_body=media).execute()
```

---

## 📁 檔案結構

設定完成後的檔案結構：

```
五常雲端空間/
├── google_credentials.json          # Google OAuth 憑證
├── google_token.json                # OAuth token（自動產生）
├── config/
│   ├── gcp/
│   │   └── littlej-sa.json         # 服務帳戶金鑰
│   └── multimedia_text_image_config.json  # 圖文功能配置
├── uploads/
│   ├── images/                      # 圖片上傳目錄
│   ├── text/                        # 文字檔案上傳目錄
│   └── generated/                   # AI 生成圖片目錄
├── containers/
│   └── uploads/                     # 容器共享上傳資料夾
└── scripts/
    └── setup_multimedia_text_image_features.py  # 設定腳本
```

---

## ✅ 驗證設定

### 檢查設定狀態

執行設定腳本會自動檢查：

1. ✅ 授權文件是否存在
2. ✅ Python 套件是否已安裝
3. ✅ Google OAuth 憑證是否設定
4. ✅ 服務帳戶是否設定
5. ✅ 上傳資料夾是否建立
6. ✅ 配置檔案是否建立

### 手動驗證

**1. 檢查 Python 套件：**
```bash
python -c "import google.auth; print('✓ google-auth 已安裝')"
python -c "import vertexai; print('✓ vertexai 已安裝')"
```

**2. 檢查憑證檔案：**
```bash
# Windows PowerShell
Test-Path "google_credentials.json"
Test-Path "config\gcp\littlej-sa.json"
```

**3. 檢查資料夾：**
```bash
# Windows PowerShell
Test-Path "uploads\images"
Test-Path "uploads\text"
Test-Path "uploads\generated"
```

---

## 🔧 故障排除

### 問題 1：找不到憑證檔案

**錯誤訊息：**
```
⚠ Google 憑證檔案不存在
```

**解決方法：**
1. 確認已從 Google Cloud Console 下載憑證
2. 確認檔案名稱正確：`google_credentials.json`
3. 確認檔案位置在專案根目錄

### 問題 2：Python 套件未安裝

**錯誤訊息：**
```
✗ google-auth - 未安裝
```

**解決方法：**
```bash
pip install google-auth google-auth-oauthlib google-api-python-client google-cloud-aiplatform
```

### 問題 3：Vertex AI API 未啟用

**錯誤訊息：**
```
圖像生成錯誤
```

**解決方法：**
```bash
gcloud services enable aiplatform.googleapis.com
```

### 問題 4：服務帳戶權限不足

**錯誤訊息：**
```
權限被拒絕
```

**解決方法：**
確認服務帳戶有以下角色：
- `roles/drive.admin` - Google Drive 管理
- `roles/aiplatform.user` - Vertex AI 使用

---

## 📊 設定摘要

設定完成後會產生設定摘要：

- **檔案位置**: `reports/multimedia_text_image_setup_summary.json`
- **配置檔案**: `config/multimedia_text_image_config.json`

---

## 🎯 後續使用

### 圖片上傳與分析

1. 上傳圖片到 `uploads/images/`
2. 使用 Vertex AI Vision 分析圖片內容
3. 將結果儲存或上傳到 Google Drive

### AI 圖像生成

1. 呼叫 Vertex AI Imagen API
2. 輸入圖片描述
3. 生成的圖片儲存到 `uploads/generated/`

### Google Workspace 整合

1. 使用服務帳戶認證
2. 上傳檔案到 Google Drive
3. 建立或編輯 Google Docs
4. 寫入 Google Sheets 資料

---

## 📝 授權資訊

**授權人：** 江政隆 F1247717117（系統創始人）  
**授權對象：** 五常非營利組織  
**系統版本：** 小 j AI 控制台 v5.1.0 / Wuchang OS v5.1.0  
**遵循條款：** Google Workspace for Nonprofits 使用條款

---

## 📞 支援

如有問題，請檢查：
1. 授權文件是否完整
2. Google Cloud Console 設定
3. Python 套件是否已安裝
4. 憑證檔案是否正確
5. API 是否已啟用

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
