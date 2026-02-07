# 雙向同步使用指南

## 概述

五常雲端空間現在支援**雙向同步**：
- **下載**：本地端夾下載五常雲端空間變更（雲端 → 本機）
- **上傳**：本地進行變更上傳雲端空間（本機 → 雲端）

## 功能特性

### 1. 智能同步判斷
- 自動比較本機和雲端檔案的修改時間
- 較新的版本會覆蓋較舊的版本
- 如果時間相同，則跳過同步

### 2. 安全保護
- 下載時自動備份現有本機檔案（`.backup_時間戳記`）
- 使用原子性操作確保檔案完整性
- 路徑驗證確保只同步五常雲端空間

### 3. 靈活配置
- 支援選擇性同步（下載/上傳/雙向）
- 支援檔案模式過濾（例如：`*.json`, `*.md`）
- 支援遞迴同步子目錄

## 使用方式

### 基本用法

```bash
# 雙向同步（自動判斷方向）
python cloud_bidirectional_sync.py --direction both

# 僅下載（雲端 -> 本機）
python cloud_bidirectional_sync.py --direction download

# 僅下載模式（非鏡像：不覆蓋本機較新檔案）
python cloud_bidirectional_sync.py --download-only

# 僅上傳模式（非鏡像：不覆蓋雲端較新檔案）
python cloud_bidirectional_sync.py --upload-only

# 僅上傳（本機 -> 雲端，會覆蓋雲端較新檔案）
python cloud_bidirectional_sync.py --direction upload
```

### 指定目錄

```bash
# 同步特定本機目錄到雲端
python cloud_bidirectional_sync.py --local-dir ./my_data --direction both

# 從雲端特定目錄下載
python cloud_bidirectional_sync.py --cloud-dir reports --direction download
```

### 檔案模式過濾

```bash
# 只同步 JSON 檔案
python cloud_bidirectional_sync.py --pattern "*.json" --direction both

# 只同步 Markdown 檔案
python cloud_bidirectional_sync.py --pattern "*.md" --direction both
```

### 非遞迴同步

```bash
# 只同步頂層檔案，不遞迴子目錄
python cloud_bidirectional_sync.py --no-recursive --direction both
```

## 同步邏輯

### 檔案比較規則

1. **本機不存在，雲端存在** → 下載
2. **本機存在，雲端不存在** → 上傳
3. **兩邊都存在**：
   - 雲端較新 → 下載
   - 本機較新 → 上傳
   - 時間相同 → 跳過

### 備份機制

下載時會自動備份現有本機檔案：
- 備份檔名格式：`原檔名.backup_YYYYMMDD_HHMMSS`
- 例如：`config.json.backup_20260121_143022`

## 範例場景

### 場景 1：從雲端下載最新變更

```bash
# 下載雲端 reports 目錄的所有變更到本機
python cloud_bidirectional_sync.py \
  --cloud-dir reports \
  --direction download \
  --local-dir ./local_reports
```

### 場景 2：上傳本機變更到雲端

```bash
# 上傳本機 scripts 目錄的所有變更到雲端
python cloud_bidirectional_sync.py \
  --local-dir ./scripts \
  --cloud-dir scripts \
  --direction upload
```

### 場景 3：雙向同步特定檔案類型

```bash
# 雙向同步所有 JSON 檔案
python cloud_bidirectional_sync.py \
  --pattern "*.json" \
  --direction both
```

## 輸出說明

同步完成後會顯示：

```
============================================================
同步結果
============================================================
同步時間: 2026-01-21 14:30:22
同步方向: both
本機目錄: C:\path\to\local
雲端目錄: J:\共用雲端硬碟\五常雲端空間\reports

下載 (3 個):
  ✓ file1.json
  ✓ file2.json
  ✓ file3.json

上傳 (2 個):
  ✓ local_file1.json
  ✓ local_file2.json

跳過 (5 個): 檔案已同步

============================================================
```

## 注意事項

1. ⚠️ **路徑限制**：所有同步操作都限制在「五常雲端空間」目錄內
2. ⚠️ **Google Drive 同步**：確保 Google Drive 桌面應用程式已安裝並正常同步
3. ⚠️ **備份檔案**：下載時會自動備份，請定期清理舊備份檔案
4. ⚠️ **網路連線**：同步操作需要網路連線到 Google Drive
5. ⚠️ **檔案衝突**：如果兩邊都有變更，較新的版本會覆蓋較舊的版本

## 故障排除

### 問題：無法找到五常雲端空間路徑

**解決方案：**
1. 確認 Google Drive 已安裝並正常同步
2. 設定 `WUCHANG_CLOUD_PATH` 環境變數：
   ```powershell
   $env:WUCHANG_CLOUD_PATH = "J:\共用雲端硬碟\五常雲端空間"
   ```

### 問題：同步失敗

**解決方案：**
1. 檢查網路連線
2. 確認 Google Drive 同步狀態
3. 檢查檔案權限
4. 查看錯誤訊息中的詳細資訊

### 問題：檔案被意外覆蓋

**解決方案：**
1. 檢查備份檔案（`.backup_時間戳記`）
2. 使用 `--direction download` 或 `--direction upload` 限制同步方向
3. 在同步前手動備份重要檔案

## 僅下載模式（非鏡像）

使用 `--download-only` 參數啟用僅下載模式：

```bash
# 僅下載變更，不覆蓋本機較新檔案
python cloud_bidirectional_sync.py --download-only
```

**特點：**
- ✅ 只下載雲端新增或更新的檔案
- ✅ 不覆蓋本機較新的檔案
- ✅ 不刪除本機多餘的檔案
- ✅ 非鏡像同步，保留本機所有檔案

詳細說明請參考：`DOWNLOAD_ONLY_MODE.md`

## 僅上傳模式（非鏡像）

使用 `--upload-only` 參數啟用僅上傳模式：

```bash
# 僅上傳變更，不覆蓋雲端較新檔案
python cloud_bidirectional_sync.py --upload-only
```

**特點：**
- ✅ 只上傳本機新增或更新的檔案
- ✅ 不覆蓋雲端較新的檔案
- ✅ 不刪除雲端多餘的檔案
- ✅ 非鏡像同步，保留雲端所有檔案

詳細說明請參考：`UPLOAD_ONLY_MODE.md`

## 相關文檔

- `CLOUD_SYNC_CONFIG.md` - 雲端同步配置說明
- `DOWNLOAD_ONLY_MODE.md` - 僅下載模式（非鏡像）使用說明
- `UPLOAD_ONLY_MODE.md` - 僅上傳模式（非鏡像）使用說明
- `cloud_bidirectional_sync.py` - 雙向同步工具源碼
