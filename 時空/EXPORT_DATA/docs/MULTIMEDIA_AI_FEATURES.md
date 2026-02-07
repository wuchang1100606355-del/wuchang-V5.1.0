# 五常 AI 多媒體與 Google Workspace 整合功能

## 功能總覽

小 j AI 控制台 v5.1.0 現已整合完整的多媒體處理與 Google Workspace APIs，支援：

-   📁 **檔案上傳**：圖片、音訊、影片等多媒體檔案
-   📂 **資料夾上傳**：批次上傳整個目錄
-   🎨 **AI 圖像生成**：使用 Vertex AI Imagen 生成圖片
-   ☁️ **Google Workspace APIs**：Drive、Docs、Sheets、Gmail、Calendar

---

## 1. 檔案上傳功能

### 使用方式

1. 點擊 **「📁 上傳檔案」** 按鈕
2. 選擇檔案（支援多選）
3. 系統自動複製到 `uploads/` 目錄
4. 通知 Odoo AI 邏輯處理

### 支援格式

| 類型 | 副檔名                 | 備註                       |
| ---- | ---------------------- | -------------------------- |
| 圖片 | .jpg, .png, .gif, .bmp | 支援 Vertex AI Vision 分析 |
| 音訊 | .mp3, .wav, .m4a, .aac | 未來支援語音轉文字         |
| 影片 | .mp4, .avi, .mkv, .mov | 未來支援影片分析           |
| 文件 | .pdf, .docx, .txt      | 支援文字擷取與分析         |

### 技術實現

```powershell
$openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
$openFileDialog.Filter = "所有檔案 (*.*)|*.*|圖片 (*.jpg;*.png;*.gif)|*.jpg;*.png;*.gif"
$openFileDialog.Multiselect = $true

if ($openFileDialog.ShowDialog() -eq 'OK') {
    foreach ($file in $openFileDialog.FileNames) {
        $destPath = "$workspace\uploads\$fileName"
        Copy-Item -Path $file -Destination $destPath -Force
        # 通知 Odoo 處理...
    }
}
```

### Odoo 整合

上傳後自動呼叫 Odoo shell：

```python
ai_logic = env['wuchang.ai.logic']
file_path = '/mnt/jules-config/../uploads/image.jpg'
file_type = '.jpg'

# 未來擴展：
# - 圖片：使用 Vertex AI Vision 分析內容
# - 音訊：使用 Speech-to-Text 轉文字
# - 文件：使用 Document AI 擷取文字
```

---

## 2. 資料夾上傳功能

### 使用方式

1. 點擊 **「📂 上傳資料夾」** 按鈕
2. 選擇資料夾
3. 系統遞迴複製所有檔案到 `uploads/資料夾名稱/`
4. 顯示檔案總數

### 應用場景

-   批次處理圖片集
-   上傳專案資料夾供 AI 分析
-   整合外部數據集

### 技術實現

```powershell
$folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
$folderBrowser.Description = "選擇要上傳的資料夾"

if ($folderBrowser.ShowDialog() -eq 'OK') {
    $sourceFolder = $folderBrowser.SelectedPath
    $folderName = [System.IO.Path]::GetFileName($sourceFolder)
    $destFolder = "$workspace\uploads\$folderName"

    Copy-Item -Path $sourceFolder -Destination $destFolder -Recurse -Force
    $fileCount = (Get-ChildItem -Path $destFolder -Recurse -File).Count
}
```

---

## 3. AI 圖像生成功能

### 使用方式

1. 點擊 **「🎨 生成圖像」** 按鈕
2. 輸入圖像描述（英文效果較佳）
3. 系統使用 Vertex AI Imagen 生成
4. 圖片儲存至 `uploads/generated_image.png`

### 範例提示詞

| 提示詞                                          | 說明           |
| ----------------------------------------------- | -------------- |
| `A beautiful sunset over mountains`             | 山景夕陽       |
| `Modern minimalist office interior design`      | 現代辦公室設計 |
| `Cute robot assistant with friendly expression` | 可愛機器人助手 |
| `Abstract art with blue and gold colors`        | 藍金抽象藝術   |

### 技術實現

```python
from vertexai.preview.vision_models import ImageGenerationModel

model = ImageGenerationModel.from_pretrained('imagegeneration@006')
response = model.generate_images(
    prompt='A beautiful sunset over mountains',
    number_of_images=1
)

if response.images:
    img_data = response.images[0]._image_bytes
    with open('uploads/generated_image.png', 'wb') as f:
        f.write(img_data)
```

### 注意事項

-   **需要 Vertex AI API 啟用**：請至 [Google Cloud Console](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com) 啟用
-   **配額限制**：免費方案有每日生成限制
-   **非營利優惠**：Google for Nonprofits 可申請額外配額

---

## 4. Google Workspace APIs

### 功能簡介

整合 Google Workspace for Nonprofits 免費服務：

| 編號 | 服務          | API             | 功能                 |
| ---- | ------------- | --------------- | -------------------- |
| 1    | Google Drive  | Drive API v3    | 檔案儲存、分享、協作 |
| 2    | Google Docs   | Docs API v1     | 文件建立、編輯、匯出 |
| 3    | Google Sheets | Sheets API v4   | 試算表自動化         |
| 4    | Gmail         | Gmail API v1    | 郵件發送、接收、管理 |
| 5    | Calendar      | Calendar API v3 | 行事曆、會議排程     |

### 使用方式

1. 點擊 **「☁️ Google 服務」** 按鈕
2. 選擇服務編號（1-5）
3. 系統自動初始化對應 API
4. 使用服務帳戶 ADC 認證

### 技術實現

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file(
    '/mnt/jules-config/gcp/littlej-sa.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

service = build('drive', 'v3', credentials=creds)
# 使用 Drive API...
```

### 必要設定

#### 1. 服務帳戶權限

在 GCP Console 為 `littlej-sa` 添加以下角色：

```bash
# Google Drive
gcloud projects add-iam-policy-binding my-j-483304 \
  --member="serviceAccount:littlej-sa@my-j-483304.iam.gserviceaccount.com" \
  --role="roles/drive.admin"

# Gmail (需 Workspace 管理員授權)
# 至 admin.google.com → Security → API controls → Domain-wide delegation
# 授權 Client ID 和 Scopes
```

#### 2. API 啟用

```bash
gcloud services enable drive.googleapis.com
gcloud services enable docs.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable calendar-json.googleapis.com
```

#### 3. Google for Nonprofits 申請

1. 前往 [google.com/nonprofits](https://www.google.com/nonprofits)
2. 驗證非營利組織身分（台灣：內政部立案證明）
3. 申請 Google Workspace for Nonprofits（免費 Business Standard）
4. 獲得：
    - 無限 Google Drive 儲存空間
    - 完整 Workspace 功能
    - 進階安全與管理工具

---

## 5. 應用場景與整合

### 場景 1：自動化內容生成

```
[小j] → 生成圖像 → 上傳至 Google Drive → 插入 Google Docs → 分享連結
```

**實現步驟：**

1. 使用「生成圖像」功能創建視覺素材
2. 點擊「Google 服務」→ Drive → 上傳圖片
3. 點擊「Google 服務」→ Docs → 插入圖片到文件
4. 自動產生分享連結供外部使用

### 場景 2：多媒體分析工作流

```
[上傳圖片] → Vertex AI Vision 分析 → 生成描述 → 儲存至 Sheets
```

**實現步驟：**

1. 上傳圖片到 `uploads/`
2. Odoo AI 邏輯自動呼叫 Vision API
3. 提取標籤、物件、文字、情緒
4. 使用 Sheets API 寫入試算表

### 場景 3：智能郵件助理

```
[與小j對話] → 撰寫郵件內容 → Gmail API 發送 → Calendar 排程追蹤
```

**實現步驟：**

1. 向小 j 說明郵件需求
2. AI 生成專業郵件內容
3. 透過 Gmail API 發送
4. 若涉及會議，自動建立 Calendar 事件

---

## 6. 安全與隱私設計

### 檔案儲存策略

-   **本地優先**：所有上傳檔案先儲存至本機 `uploads/`
-   **容器掛載**：透過 Docker volume 映射供 Odoo 訪問
-   **權限控制**：僅管理員可上傳，系統自動驗證

### 服務帳戶安全

-   **ADC 認證**：使用 `littlej-sa.json` 服務帳戶
-   **最小權限**：僅授予必要的 API scopes
-   **金鑰保護**：金鑰存放於 `config/gcp/`，.gitignore 排除

### Google Workspace 整合

-   **Domain-wide Delegation**：非營利組織管理員授權
-   **Audit Logs**：所有 API 呼叫記錄於 Cloud Logging
-   **資料主權**：數據存放於 Google 台灣機房（可選）

---

## 7. 擴展開發指南

### 新增檔案處理功能

在 `wuchang_os/addons/wuchang_core/models/ai_logic.py` 添加：

```python
def process_uploaded_file(self, file_path, file_type):
    """處理上傳的檔案"""
    if file_type in ['.jpg', '.png', '.gif']:
        return self._analyze_image(file_path)
    elif file_type in ['.mp3', '.wav']:
        return self._transcribe_audio(file_path)
    elif file_type == '.pdf':
        return self._extract_pdf_text(file_path)
    else:
        return f"檔案類型 {file_type} 尚未支援"

def _analyze_image(self, image_path):
    """使用 Vertex AI Vision 分析圖片"""
    from vertexai.vision_models import ImageTextModel
    model = ImageTextModel.from_pretrained("imagetext@001")
    response = model.get_captions(image=image_path)
    return response.captions[0] if response.captions else "無法分析"
```

### 新增 Google API 整合

```python
def create_google_doc(self, title, content):
    """建立 Google Docs 文件"""
    from googleapiclient.discovery import build

    service = build('docs', 'v1', credentials=self._get_google_creds())
    doc = service.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']

    # 插入內容
    requests = [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]
    service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"
```

---

## 8. 故障排除

### 圖像生成失敗

**症狀：** 顯示「圖像生成錯誤」

**原因：**

-   Vertex AI Imagen API 未啟用
-   服務帳戶缺少 `aiplatform.user` 角色
-   專案配額不足

**解決：**

```bash
# 啟用 API
gcloud services enable aiplatform.googleapis.com

# 授予角色
gcloud projects add-iam-policy-binding my-j-483304 \
  --member="serviceAccount:littlej-sa@my-j-483304.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# 檢查配額
gcloud compute project-info describe --project=my-j-483304
```

### Google API 初始化失敗

**症狀：** 顯示「找不到服務帳戶金鑰」

**原因：**

-   `config/gcp/littlej-sa.json` 不存在
-   環境變數 `GOOGLE_APPLICATION_CREDENTIALS` 未設定

**解決：**

1. 下載服務帳戶金鑰到 `config/gcp/littlej-sa.json`
2. 確認 `docker-compose.yml` 已設定環境變數
3. 重啟容器：`docker-compose restart wuchang-web`

### 檔案上傳後 Odoo 無法讀取

**症狀：** 檔案存在於 `uploads/` 但 Odoo 報錯

**原因：**

-   Docker volume 映射問題
-   檔案權限不足

**解決：**

```yaml
# docker-compose.yml
services:
    wuchang-web:
        volumes:
            - ./uploads:/mnt/uploads:rw # 確保讀寫權限
```

```bash
# 修正權限
chmod -R 755 uploads/
```

---

## 9. 最佳實踐

### 檔案命名規範

-   使用英文與數字（避免中文路徑問題）
-   加上時間戳記：`image_20260108_143022.jpg`
-   分類存放：`uploads/images/`, `uploads/audio/`

### API 配額管理

-   **監控使用量**：使用 Cloud Monitoring 追蹤 API 呼叫
-   **實施快取**：重複請求使用本地快取
-   **批次處理**：合併多個 API 請求減少呼叫次數

### 非營利資源利用

Google for Nonprofits 包含：

-   ✅ Google Workspace Business Standard（免費）
-   ✅ Google Ad Grants（每月 $10,000 廣告額度）
-   ✅ YouTube Nonprofit Program（捐款功能）
-   ✅ Google Earth and Maps（進階功能）

---

## 10. 未來擴展

### 計畫中功能

-   🎤 **語音輸入**：使用 Speech-to-Text API
-   📹 **影片分析**：使用 Video Intelligence API
-   📊 **自動化報表**：定期生成 Sheets 報表
-   📧 **郵件模板**：Gmail 自動回覆與追蹤
-   🗓️ **智能排程**：Calendar AI 排程建議

### 整合建議

-   **Zapier/Make**：連接更多第三方服務
-   **Power Automate**：Microsoft 生態整合
-   **n8n**：開源自動化工作流
-   **Airbyte**：數據同步與 ETL

---

## 版本歷史

### v5.1.0 (2026-01-08)

-   ✅ 新增檔案上傳功能（多檔案支援）
-   ✅ 新增資料夾上傳功能
-   ✅ 整合 Vertex AI Imagen 圖像生成
-   ✅ 整合 Google Workspace APIs (Drive/Docs/Sheets/Gmail/Calendar)
-   ✅ 支援 Google for Nonprofits 免費方案
-   ✅ 優化 GUI 視窗布局（1200x800）

---

## 權限聲明

此功能由 **江政隆 F1247717117**（系統創始人）授權開發，專為五常非營利組織設計，遵循 Google Workspace for Nonprofits 使用條款。

**申請資格：** 台灣內政部立案之非營利組織

**申請網址：** https://www.google.com/nonprofits

---

**Powered by 小 j AI 🤖 | Wuchang OS v5.1.0 | Google for Nonprofits ☁️**


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:22:40
---
