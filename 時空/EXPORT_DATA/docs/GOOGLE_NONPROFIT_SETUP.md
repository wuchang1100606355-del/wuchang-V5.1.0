# Google for Nonprofits 申請與整合指南

## 專案資訊

-   **組織名稱**: 五常（待註冊）
-   **創始人**: 江政隆 F1247717117
-   **網域**: wuchang.life
-   **Google Cloud 專案**: my-j-483304
-   **服務帳戶**: littlej-sa@my-j-483304.iam.gserviceaccount.com

---

## 一、Google for Nonprofits 申請流程

### 申請資格（台灣）

根據 Google for Nonprofits 台灣資格：

✅ **符合資格的組織**：

-   內政部立案之社團法人、財團法人
-   教育部立案之私立學校（需符合特定條件）
-   衛福部立案之醫療財團法人（需符合條件）
-   具備免稅資格（財政部認證）

❌ **不符合資格**：

-   政府機關
-   醫院與醫療機構（營利性質）
-   學校與學術機構（一般高中大學）
-   政黨與政治組織

### 申請步驟

#### 第一階段：組織驗證

1. **前往申請網站**

    ```
    https://www.google.com/nonprofits
    ```

2. **選擇國家/地區**

    - 選擇「台灣」
    - 閱讀資格要求

3. **準備文件**

    - 內政部立案證明（掃描檔）
    - 財團法人/社團法人登記證書
    - 組織章程
    - 免稅證明（財政部核發）

4. **填寫申請表**

    - 組織全名
    - 統一編號
    - 聯絡人：江政隆 F1247717117
    - 聯絡信箱：admin@wuchang.life
    - 組織網站：https://wuchang.life

5. **提交審核**
    - 一般審核時間：7-14 個工作天
    - 可能需要補件（準備英文翻譯）

#### 第二階段：啟用服務

通過驗證後可啟用：

| 服務                               | 免費額度   | 商業價值    |
| ---------------------------------- | ---------- | ----------- |
| Google Workspace Business Standard | 完全免費   | $12/用戶/月 |
| Google Ad Grants                   | $10,000/月 | $10,000/月  |
| YouTube Nonprofit Program          | 免費       | -           |
| Google Earth & Maps                | 進階功能   | $200/月+    |

---

## 二、Google Workspace for Nonprofits 設定

### 1. 建立組織帳號

通過驗證後：

1. 收到 Google 的啟用連結
2. 使用 admin@wuchang.life 登入
3. 完成 Workspace 初始設定

### 2. 網域驗證

**方法 A：DNS TXT 記錄**（推薦）

```bash
# 在 Cloudflare DNS 添加
# 類型：TXT
# 名稱：@
# 內容：google-site-verification=XXXXXXXXXXXXX
```

**方法 B：HTML 檔案驗證**

上傳到 `wuchang.life/google-verification.html`

### 3. 建立使用者

```
admin@wuchang.life      # 管理員（江政隆）
littlej@wuchang.life    # AI 服務帳戶（可選）
team@wuchang.life       # 團隊信箱
```

### 4. 設定 MX 記錄（Gmail）

在 Cloudflare DNS 添加：

```
# 優先順序 1
ASPMX.L.GOOGLE.COM

# 優先順序 5
ALT1.ASPMX.L.GOOGLE.COM
ALT2.ASPMX.L.GOOGLE.COM

# 優先順序 10
ALT3.ASPMX.L.GOOGLE.COM
ALT4.ASPMX.L.GOOGLE.COM
```

---

## 三、服務帳戶與 API 整合

### 1. 建立服務帳戶（已完成）

```bash
# 已存在: littlej-sa@my-j-483304.iam.gserviceaccount.com
gcloud iam service-accounts describe littlej-sa@my-j-483304.iam.gserviceaccount.com
```

### 2. 啟用必要 APIs

```bash
# Vertex AI（已啟用）
gcloud services enable aiplatform.googleapis.com

# Google Workspace APIs
gcloud services enable admin.googleapis.com        # Admin SDK
gcloud services enable drive.googleapis.com        # Google Drive
gcloud services enable docs.googleapis.com         # Google Docs
gcloud services enable sheets.googleapis.com       # Google Sheets
gcloud services enable gmail.googleapis.com        # Gmail
gcloud services enable calendar-json.googleapis.com # Calendar

# 額外服務
gcloud services enable youtube.googleapis.com      # YouTube
gcloud services enable analytics.googleapis.com    # Google Analytics
```

### 3. 授予 Workspace Admin 權限

**重要：Domain-wide Delegation**

因為服務帳戶需要代表組織用戶操作，必須設定全網域委派：

1. **取得 Client ID**

    ```bash
    gcloud iam service-accounts describe littlej-sa@my-j-483304.iam.gserviceaccount.com \
      --format="value(oauth2ClientId)"
    ```

2. **前往 Google Workspace Admin Console**

    ```
    https://admin.google.com
    → 安全性 (Security)
    → 存取權和資料控管 (Access and data control)
    → API 控制項 (API controls)
    → 管理全網域委派 (Manage Domain-wide Delegation)
    ```

3. **新增 API 用戶端**

    - Client ID: `從上面取得`
    - OAuth Scopes:
        ```
        https://www.googleapis.com/auth/drive
        https://www.googleapis.com/auth/documents
        https://www.googleapis.com/auth/spreadsheets
        https://www.googleapis.com/auth/gmail.send
        https://www.googleapis.com/auth/gmail.readonly
        https://www.googleapis.com/auth/calendar
        https://www.googleapis.com/auth/admin.directory.user.readonly
        ```

4. **授權並儲存**

### 4. 更新服務帳戶金鑰

如需重新生成金鑰（含 Workspace 權限）：

```bash
gcloud iam service-accounts keys create config/gcp/littlej-sa.json \
  --iam-account=littlej-sa@my-j-483304.iam.gserviceaccount.com

# 確認檔案存在
ls -lh config/gcp/littlej-sa.json
```

---

## 四、五常本機總控整合配置

### 1. 驗證環境變數

檢查 `docker-compose.yml`：

```yaml
services:
    wuchang-web:
        environment:
            - GOOGLE_APPLICATION_CREDENTIALS=/mnt/jules-config/gcp/littlej-sa.json
            - GOOGLE_CLOUD_PROJECT=my-j-483304
            - GOOGLE_WORKSPACE_DOMAIN=wuchang.life
            - GOOGLE_WORKSPACE_ADMIN=admin@wuchang.life
```

### 2. 寫入 Odoo 參數

```bash
docker exec -it wuchangv510-wuchang-web-1 bash -lc "odoo shell -d admin --db_host=db --db_user=odoo --db_password=odoo <<'PY'
env = env['ir.config_parameter'].sudo()
env.set_param('wuchang.google.workspace_domain', 'wuchang.life')
env.set_param('wuchang.google.workspace_admin', 'admin@wuchang.life')
env.set_param('wuchang.google.nonprofit_enabled', 'true')
print('Google Workspace 參數已設定')
PY"
```

### 3. 測試 API 連線

執行測試腳本：

```powershell
# 測試 Drive API
docker exec wuchangv510-wuchang-web-1 python3 -c "
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

creds = service_account.Credentials.from_service_account_file(
    os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
    scopes=['https://www.googleapis.com/auth/drive'],
    subject='admin@wuchang.life'
)

service = build('drive', 'v3', credentials=creds)
results = service.files().list(pageSize=10).execute()
print('成功連接 Google Drive API')
print(f'找到 {len(results.get(\"files\", []))} 個檔案')
"
```

---

## 五、GUI 控制台使用

### 啟動控制台

```powershell
# 以管理員身份執行
powershell.exe -NoLogo -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\tools\local_root_control_gui.ps1"
```

### Google Workspace 功能測試

#### 測試 1：Drive API

```
1. 點擊「☁️ Google 服務」
2. 選擇 1 (Drive)
3. 應顯示：[小j] drive API 已就緒！
```

#### 測試 2：上傳檔案到 Drive

```python
# 在 Odoo shell 執行
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

service = build('drive', 'v3', credentials=creds)
file_metadata = {'name': 'test.txt'}
media = MediaFileUpload('/mnt/uploads/test.txt', mimetype='text/plain')
file = service.files().create(body=file_metadata, media_body=media).execute()
print(f'檔案 ID: {file.get("id")}')
```

#### 測試 3：建立 Google Docs

```python
from googleapiclient.discovery import build

service = build('docs', 'v1', credentials=creds)
doc = service.documents().create(body={'title': '五常系統測試文件'}).execute()
print(f'文件 URL: https://docs.google.com/document/d/{doc["documentId"]}/edit')
```

---

## 六、常見問題

### Q1: 非營利組織驗證需要多久？

**A:** 台灣地區通常 7-14 個工作天，最長可能 30 天。建議提前準備所有文件的英文翻譯。

### Q2: 五常尚未正式立案，可以申請嗎？

**A:** 不可以。必須先完成內政部立案登記，取得正式的社團法人或財團法人身分。

**替代方案：**

-   先使用一般 Google Cloud 免費方案
-   申請 Google Cloud 試用額度（$300）
-   待組織正式立案後再申請 Nonprofits

### Q3: 服務帳戶與 Workspace 帳號的差異？

**A:**

-   **服務帳戶（littlej-sa）**：用於程式自動化呼叫 API，無需人工登入
-   **Workspace 帳號（admin@wuchang.life）**：人類使用者，可登入 Gmail、Drive 等

**使用場景：**

-   自動化工作流 → 服務帳戶
-   人工操作 → Workspace 帳號

### Q4: Domain-wide Delegation 有安全風險嗎？

**A:** 有一定風險，因為服務帳戶可代表任何組織成員操作。

**安全措施：**

1. 僅授予必要的 scopes
2. 定期輪換服務帳戶金鑰
3. 啟用 Cloud Audit Logs 監控
4. 金鑰存放於安全位置（不上傳 Git）

### Q5: 免費額度有使用期限嗎？

**A:** 只要組織維持非營利身分且符合資格，Google Workspace for Nonprofits **永久免費**。

**注意事項：**

-   若組織轉為營利，必須轉換為付費方案
-   若濫用資源，Google 有權終止服務

---

## 七、擴展應用

### 整合建議

#### 1. 自動化報表系統

```python
# 每日自動生成 Google Sheets 報表
def generate_daily_report():
    service = build('sheets', 'v4', credentials=creds)
    spreadsheet = {
        'properties': {'title': f'五常日報 {date.today()}'}
    }
    sheet = service.spreadsheets().create(body=spreadsheet).execute()
    # 寫入數據...
```

#### 2. 智能郵件助理

```python
# 使用 AI 撰寫郵件並透過 Gmail 發送
def send_ai_email(to, subject, ai_generated_body):
    service = build('gmail', 'v1', credentials=creds)
    message = create_message('admin@wuchang.life', to, subject, ai_generated_body)
    service.users().messages().send(userId='me', body=message).execute()
```

#### 3. 雲端備份系統

```python
# 自動備份 Odoo 資料庫到 Google Drive
def backup_to_drive():
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': f'odoo_backup_{datetime.now().strftime("%Y%m%d")}.sql',
        'parents': ['BACKUP_FOLDER_ID']
    }
    media = MediaFileUpload('backup.sql', mimetype='application/sql')
    service.files().create(body=file_metadata, media_body=media).execute()
```

---

## 八、成本分析

### 若無 Nonprofits 方案的成本

| 服務                               | 商業價格    | Nonprofit 價格 | 年度節省             |
| ---------------------------------- | ----------- | -------------- | -------------------- |
| Google Workspace Business Standard | $12/用戶/月 | **免費**       | $1,440/年（10 用戶） |
| Google Ad Grants                   | -           | $10,000/月     | $120,000/年          |
| Google Cloud（基礎使用）           | ~$100/月    | 試用額度       | $1,200/年            |
| **總計**                           | -           | -              | **~$122,640/年**     |

**結論：申請 Google for Nonprofits 可為組織節省超過 10 萬/年的雲端服務成本。**

---

## 九、行動清單

### 立即可執行

-   [x] 啟用 Vertex AI API（已完成）
-   [x] 建立服務帳戶 littlej-sa（已完成）
-   [ ] 測試 Imagen 圖像生成功能
-   [ ] 驗證 Drive/Docs/Sheets API 連線

### 待組織立案後

-   [ ] 準備內政部立案證明
-   [ ] 申請 Google for Nonprofits 驗證
-   [ ] 設定 Google Workspace 帳號
-   [ ] 配置 Domain-wide Delegation
-   [ ] 完整測試所有 Workspace APIs

### 長期規劃

-   [ ] 開發自動化報表系統
-   [ ] 整合 Gmail 智能郵件助理
-   [ ] 建立雲端備份機制
-   [ ] 申請 Google Ad Grants 推廣組織
-   [ ] 整合 YouTube Nonprofit Program

---

## 十、支援資源

### 官方文件

-   Google for Nonprofits: https://www.google.com/nonprofits
-   Workspace Admin Help: https://support.google.com/a
-   Google Cloud APIs: https://cloud.google.com/apis/docs
-   Vertex AI 文件: https://cloud.google.com/vertex-ai/docs

### 社群資源

-   Google Cloud Community: https://www.googlecloudcommunity.com
-   Stack Overflow - Google APIs: https://stackoverflow.com/questions/tagged/google-api

### 聯絡方式

**技術支援：**

-   Google Cloud Support（若有付費方案）
-   Nonprofits Support: nonprofits@google.com

**五常系統創始人：**

-   江政隆 F1247717117
-   admin@wuchang.life

---

**最後更新：2026-01-08**  
**文件版本：v1.0**  
**Powered by 小 j AI 🤖 | Wuchang OS v5.1.0**


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:22:40
---
