# 雲端同步配置說明

## 概述

本系統支援**雙向同步**模式：
- **雲端 → 本機**：本地端夾下載五常雲端空間變更
- **本機 → 雲端**：本地進行變更上傳雲端空間
- **僅同步「五常雲端空間」目錄**
- **智能同步**：根據檔案修改時間自動決定同步方向

## 配置方式

### 1. 環境變數配置（推薦）

設定 `WUCHANG_CLOUD_PATH` 環境變數指向五常雲端空間：

**Windows (PowerShell):**
```powershell
$env:WUCHANG_CLOUD_PATH = "J:\共用雲端硬碟\五常雲端空間"
# 或永久設定
[System.Environment]::SetEnvironmentVariable("WUCHANG_CLOUD_PATH", "J:\共用雲端硬碟\五常雲端空間", "User")
```

**Windows (CMD):**
```cmd
setx WUCHANG_CLOUD_PATH "J:\共用雲端硬碟\五常雲端空間"
```

### 2. 自動偵測路徑

如果未設定環境變數，系統會自動嘗試以下路徑：

**Windows:**
- `J:\共用雲端硬碟\五常雲端空間`
- `J:\我的雲端硬碟\五常雲端空間`
- `%USERPROFILE%\Google Drive\五常雲端空間`
- `%USERPROFILE%\Google 雲端硬碟\五常雲端空間`
- `G:\Google Drive\五常雲端空間`
- `G:\Google 雲端硬碟\五常雲端空間`

**Linux/Mac:**
- `~/Google Drive/五常雲端空間`
- `/mnt/google-drive/五常雲端空間`

## 目錄結構

五常雲端空間的標準目錄結構：

```
五常雲端空間/
├── reports/          # 報告檔案
├── scripts/          # 腳本檔案
├── database/
│   └── backups/      # 資料庫備份
├── uploads/          # 上傳檔案
├── config/           # 配置檔案
└── backups/          # 其他備份
```

## 相關腳本

### 1. `cloud_sync_config.py`
統一配置模組，提供：
- `get_wuchang_cloud_path()` - 獲取五常雲端空間路徑
- `ensure_wuchang_cloud_path()` - 確保路徑存在
- `validate_cloud_path(path)` - 驗證路徑是否在五常雲端空間內
- `get_sync_directories()` - 獲取同步目錄結構
- `get_sync_config()` - 獲取同步配置

### 2. `backup_to_gdrive.py`
備份本地儲存到五常雲端空間（單向）

### 3. `auto_upload_reports_to_cloud.py`
自動上傳報告檔案到五常雲端空間（單向）

### 4. `upload_files_to_cloud.py`
上傳檔案到五常雲端空間（單向）

### 5. `smart_sync.py`
擇優同步工具（支援雙向同步）

### 6. `cloud_bidirectional_sync.py`
雙向同步工具（新增）
- 從雲端下載變更到本機
- 從本機上傳變更到雲端
- 支援選擇性同步（下載/上傳/雙向）
- 支援僅下載模式（非鏡像：不覆蓋本機較新檔案）
- 支援僅上傳模式（非鏡像：不覆蓋雲端較新檔案）

### 7. `sync_wuchang_to_cloud.py`
C:\wuchang V5.1.0 專用同步工具（新增）
- 專門同步 `C:\wuchang V5.1.0\wuchang-V5.1.0` 與五常雲端空間
- 預設使用雙向增量同步（互相增加變更，不覆蓋較新檔案）
- 自動配置目錄映射
- 支援分類同步（local_storage, scripts, reports, config）
- 支援所有同步模式（雙向增量/雙向/僅下載/僅上傳）

## 同步模式

### 雙向同步
- **下載**：從雲端下載變更到本機（雲端 → 本機）
- **上傳**：從本機上傳變更到雲端（本機 → 雲端）
- **智能判斷**：根據檔案修改時間自動決定同步方向

### 安全限制

1. **路徑限制**：僅允許同步到「五常雲端空間」目錄
2. **路徑驗證**：所有同步操作都會驗證目標路徑
3. **備份保護**：下載時會自動備份現有本機檔案

## 測試配置

執行以下命令測試配置：

```bash
python cloud_sync_config.py
```

## 備份策略

**重要：所有備份檔案僅存於雲端，本機不保留副本**

- ✅ 備份操作直接寫入雲端（五常雲端空間）
- ✅ 本機不保留備份檔案的副本
- ✅ 節省本機磁碟空間
- ✅ 所有備份統一管理於雲端

## 使用方式

### 雙向同步

```bash
# 雙向同步（自動判斷方向）
python cloud_bidirectional_sync.py --direction both

# 僅下載（雲端 -> 本機）
python cloud_bidirectional_sync.py --direction download --cloud-dir reports

# 僅上傳（本機 -> 雲端）
python cloud_bidirectional_sync.py --direction upload --local-dir ./local_data

# 同步特定檔案類型
python cloud_bidirectional_sync.py --pattern "*.json" --direction both

# 僅下載模式（非鏡像：不覆蓋本機較新檔案）
python cloud_bidirectional_sync.py --download-only

# 僅上傳模式（非鏡像：不覆蓋雲端較新檔案）
python cloud_bidirectional_sync.py --upload-only
```

### C:\wuchang V5.1.0 專用同步

```bash
# 雙向增量同步 C:\wuchang V5.1.0 與五常雲端空間（預設：互相增加變更）
python sync_wuchang_to_cloud.py

# 或明確指定雙向增量模式
python sync_wuchang_to_cloud.py --mode incremental-both

# 僅下載變更（非鏡像）
python sync_wuchang_to_cloud.py --mode download-only

# 僅上傳變更（非鏡像）
python sync_wuchang_to_cloud.py --mode upload-only

# 只同步本地儲存
python sync_wuchang_to_cloud.py --category local_storage
```

### 其他目錄同步策略

對於非 C:\wuchang V5.1.0 的目錄，使用僅下載模式（本地不再增加檔案）：

```bash
# 只從雲端下載，本地不再增加檔案
python cloud_bidirectional_sync.py --download-only --cloud-dir other_dir
```

## 注意事項

1. **雙向同步**：系統支援從雲端下載和從本機上傳
2. **僅同步五常雲端空間**：所有同步操作都限制在「五常雲端空間」目錄內
3. **Google Drive 同步**：確保 Google Drive 桌面應用程式已安裝並正常同步
4. **路徑驗證**：如果目標路徑不在五常雲端空間內，系統會發出警告
5. **備份僅存雲端**：所有備份檔案直接寫入雲端，本機不保留副本
6. **自動備份**：下載時會自動備份現有本機檔案（.backup_時間戳記）

## 更新記錄

- 2026-01-21: 改為單向寫入模式，僅同步到五常雲端空間
- 2026-01-21: 所有備份檔案改為雲端儲存，本機不儲存
- 2026-01-21: 支援雙向同步：本地端夾下載五常雲端空間變更，本地進行變更上傳雲端空間
- 2026-01-21: 新增僅下載模式（非鏡像）：只下載變更，不覆蓋本機較新檔案
- 2026-01-21: 新增僅上傳模式（非鏡像）：只上傳變更，不覆蓋雲端較新檔案
- 2026-01-21: 新增 C:\wuchang V5.1.0 專用同步工具
- 2026-01-21: 新增雙向增量模式：C:\wuchang V5.1.0 與五常雲端空間互相增加變更，其他目錄僅下載
