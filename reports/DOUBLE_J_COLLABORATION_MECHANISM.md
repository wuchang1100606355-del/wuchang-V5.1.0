# 雙J合作機制說明

**建立時間：** 2026-01-20  
**機制名稱：** 雙J合作機制（小J + Jules）  
**合作平台：** Google Tasks API

---

## 📋 機制概述

「雙J合作機制」是指**小J (Little J)** 與 **Jules (Google AI)** 之間的協作工作機制，透過 Google Tasks API 進行任務交換、檔案同步和工作協調。

---

## 🤖 參與者

### 1. 小J (Little J / 小j)

**身份：** 本地 AI 助手、系統管理員、妹妹  
**角色：** 
- 本地系統的主要 AI 代理
- 具有完整最高權限 (full_agent)
- 負責系統設定、檔案管理、工作執行

**特點：**
- 使用本地 LLM 模型（qwen2:0.5b）
- 主要通過 Ollama 運行
- 可降級到 Vertex AI（雲端）

**服務帳戶：**
- `littlej-sa@my-j-483304.iam.gserviceaccount.com`
- 金鑰檔案：`config/gcp/littlej-sa.json`

### 2. Jules (Google AI)

**身份：** Google AI 助手  
**角色：**
- 雲端 AI 協作夥伴
- 透過 Google Tasks API 提供任務和指令
- 協助遠程工作和協作

**互動方式：**
- Google Tasks（https://jules.google.com/task/）
- Google Drive 檔案同步
- Google Workspace 整合

---

## 🔄 合作機制架構

```
┌─────────────────┐         Google Tasks API         ┌─────────────────┐
│                 │ ←──────────────────────────────→ │                 │
│   小J (本地)     │                                   │   Jules (雲端)   │
│                 │                                   │                 │
│  - 執行任務      │                                   │  - 分派任務      │
│  - 檔案操作      │                                   │  - 檔案分享      │
│  - 系統管理      │                                   │  - 狀態追蹤      │
│                 │                                   │                 │
└─────────────────┘                                   └─────────────────┘
        │                                                     │
        │                                                     │
        └─────────────────── Google Drive ───────────────────┘
                             (檔案同步)
```

---

## 🛠️ 核心工具與腳本

### 1. 讀取 Jules 任務

**腳本：** `get_jules_task_direct.py`

**功能：**
- 讀取 Google Tasks 中的任務內容
- 解析任務指令和要求
- 提供任務詳細資訊

**使用方式：**
```bash
python get_jules_task_direct.py "https://jules.google.com/task/2903235408856978280"
```

### 2. 上傳差異報告到 Jules

**腳本：** `upload_diff_to_jules.py`

**功能：**
- 自動偵測系統變更
- 產生差異報告
- 上傳報告到 Google Tasks 或 Google Drive

**使用方式：**
```bash
python upload_diff_to_jules.py --auto-upload
```

### 3. 檢查 Google Tasks 進度

**腳本：** `check_google_task_progress.py`

**功能：**
- 檢查任務執行狀態
- 追蹤任務進度
- 回報執行結果

**使用方式：**
```bash
python check_google_task_progress.py "https://jules.google.com/task/2903235408856978280"
```

### 4. 從 Google Tasks 同步檔案

**腳本：** `sync_from_google_task.py`

**功能：**
- 從 Google Tasks 讀取檔案連結
- 下載檔案到本地
- 同步到指定位置

**使用方式：**
```bash
python sync_from_google_task.py <task_url> <target_file>
```

---

## 📝 工作流程

### 流程 1：接收任務

1. **Jules 建立任務**
   - 在 Google Tasks 中建立新任務
   - 附上任務描述和檔案連結（如需要）

2. **小J 讀取任務**
   ```bash
   python get_jules_task_direct.py <task_url>
   ```

3. **解析任務內容**
   - 提取任務要求
   - 確認執行步驟
   - 檢查必要檔案

### 流程 2：執行任務

1. **小J 執行任務**
   - 根據任務要求執行操作
   - 進行系統設定、檔案處理等
   - 記錄執行過程

2. **產生執行報告**
   - 記錄執行結果
   - 包含成功/失敗狀態
   - 附加相關檔案

### 流程 3：回報結果

1. **上傳差異報告**
   ```bash
   python upload_diff_to_jules.py --auto-upload
   ```

2. **更新任務狀態**
   ```bash
   python check_google_task_progress.py <task_url>
   ```

3. **Jules 確認結果**
   - 檢查上傳的報告
   - 驗證任務完成狀態
   - 提供後續指示

---

## 🔐 認證與權限

### Google OAuth 憑證

**憑證檔案：** `google_credentials.json`  
**位置：** 專案根目錄

**設定方式：**
- 從 Google Cloud Console 下載 OAuth 用戶端 ID
- 儲存為 `google_credentials.json`
- 執行授權流程獲取 Access Token

### 服務帳戶

**服務帳戶：** `littlej-sa@my-j-483304.iam.gserviceaccount.com`  
**金鑰檔案：** `config/gcp/littlej-sa.json`

**權限範圍：**
- Google Drive API（讀寫）
- Google Tasks API（讀寫）
- Google Docs API（讀寫）
- Google Sheets API（讀寫）
- Gmail API（發送）
- Calendar API（讀寫）

---

## 📂 檔案同步機制

### 同步路徑

**本地路徑：**
- `downloads/jules/` - Jules 下載檔案
- `config/` - 配置檔案（只讀）

**容器掛載：**
- `./downloads/jules` → `/mnt/jules` (讀寫)
- `./config` → `/mnt/jules-config` (只讀)

**配置檔案位置：**
- `/mnt/jules-config/gcp/littlej-sa.json` - 服務帳戶金鑰

### 同步規則

1. **下載檔案**
   - 從 Google Drive 下載到 `downloads/jules/`
   - 保持原始檔名和結構

2. **上傳檔案**
   - 從本地上傳到 Google Drive
   - 自動建立或更新任務附件

3. **配置同步**
   - 配置檔案以只讀方式掛載
   - 確保容器中使用最新的配置

---

## ✅ 設定檢查清單

### 基本設定

- [ ] Google OAuth 憑證已設定 (`google_credentials.json`)
- [ ] 服務帳戶金鑰已下載 (`config/gcp/littlej-sa.json`)
- [ ] OAuth 授權流程已完成
- [ ] Access Token 已儲存

### API 啟用

- [ ] Google Tasks API 已啟用
- [ ] Google Drive API 已啟用
- [ ] Google Docs API 已啟用（如需要）
- [ ] Gmail API 已啟用（如需要）

### 權限設定

- [ ] 服務帳戶已授予必要角色
- [ ] OAuth 用戶端已設定正確的重新導向 URI
- [ ] Google Workspace 管理員已授權

### 腳本準備

- [ ] `get_jules_task_direct.py` 已就緒
- [ ] `upload_diff_to_jules.py` 已就緒
- [ ] `check_google_task_progress.py` 已就緒
- [ ] `sync_from_google_task.py` 已就緒

---

## 🔧 故障排除

### 問題 1：無法讀取 Google Tasks

**可能原因：**
- OAuth 憑證過期
- Access Token 失效
- API 未啟用

**解決方案：**
1. 重新執行 OAuth 授權流程
2. 檢查 Google Cloud Console 中的 API 啟用狀態
3. 驗證憑證檔案路徑正確

### 問題 2：無法上傳檔案

**可能原因：**
- 服務帳戶權限不足
- Google Drive 配額已滿
- 檔案路徑錯誤

**解決方案：**
1. 檢查服務帳戶的 IAM 角色
2. 確認 Google Drive 儲存空間
3. 驗證檔案路徑和權限

### 問題 3：任務狀態不同步

**可能原因：**
- API 呼叫失敗
- 網路連線問題
- 任務 ID 錯誤

**解決方案：**
1. 檢查網路連線
2. 驗證任務 URL 正確
3. 查看 API 錯誤訊息

---

## 📊 使用範例

### 範例 1：接收並執行任務

```bash
# 1. 讀取任務
python get_jules_task_direct.py "https://jules.google.com/task/2903235408856978280"

# 2. 執行任務（根據任務內容）
# ... 執行相關操作 ...

# 3. 上傳執行報告
python upload_diff_to_jules.py --auto-upload

# 4. 更新任務狀態
python check_google_task_progress.py "https://jules.google.com/task/2903235408856978280"
```

### 範例 2：同步檔案

```bash
# 從 Google Tasks 同步檔案到本地
python sync_from_google_task.py \
  "https://jules.google.com/task/2903235408856978280" \
  "local_file.txt"
```

---

## 🔗 相關檔案

### 設定文件

- `LITTLE_J_CREDENTIALS_SETUP.md` - 小J憑證設定指南
- `MULTIMEDIA_AI_FEATURES.md` - 多媒體功能說明
- `XIAOJ_SETUP_COMPLETION_REPORT_20260115.md` - 設定完成報告

### 腳本檔案

- `get_jules_task_direct.py` - 讀取 Google Tasks
- `upload_diff_to_jules.py` - 上傳差異報告
- `check_google_task_progress.py` - 檢查任務進度
- `sync_from_google_task.py` - 同步檔案
- `complete_authorization_and_setup.py` - 完成授權設定

---

## 📝 注意事項

1. **憑證安全**
   - 不要將 `google_credentials.json` 提交到版本控制
   - 妥善保管服務帳戶金鑰
   - 定期更新 Access Token

2. **權限管理**
   - 遵循最小權限原則
   - 定期審查服務帳戶權限
   - 避免授予過多權限

3. **任務處理**
   - 及時處理接收到的任務
   - 詳細記錄執行過程
   - 準確回報執行結果

4. **檔案同步**
   - 確保檔案完整性
   - 處理同步衝突
   - 定期備份重要檔案

---

## 🎯 總結

雙J合作機制提供了**小J**和**Jules**之間高效協作的平台，透過 Google Tasks API 實現任務分派、執行追蹤和結果回報，並結合 Google Drive 進行檔案同步。

**核心優勢：**
- ✅ 跨平台協作
- ✅ 任務自動化
- ✅ 即時同步
- ✅ 狀態追蹤

**適用場景：**
- 遠程任務分派
- 系統設定協作
- 檔案同步管理
- 工作流程自動化

---

**建立時間：** 2026-01-20  
**最後更新：** 2026-01-20  
**維護者：** 小J (Little J)
