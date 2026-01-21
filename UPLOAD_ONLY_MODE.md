# 僅上傳模式（非鏡像）使用說明

## 概述

僅上傳模式（`--upload-only`）是一種**非鏡像同步**模式：
- ✅ **只上傳變更**：僅上傳本機新增或更新的檔案
- ✅ **不覆蓋雲端較新檔案**：如果雲端檔案較新，保留雲端版本
- ✅ **不刪除雲端多餘檔案**：雲端有但本機沒有的檔案會保留
- ✅ **非鏡像同步**：不會讓雲端完全鏡像本機

## 使用方式

### 基本用法

```bash
# 僅上傳模式（非鏡像）
python cloud_bidirectional_sync.py --upload-only

# 指定目錄
python cloud_bidirectional_sync.py --upload-only --local-dir ./my_data --cloud-dir my_data

# 指定檔案類型
python cloud_bidirectional_sync.py --upload-only --pattern "*.json"
```

## 同步邏輯

### 僅上傳模式的規則

1. **本機不存在，雲端存在** → ⏭️ 跳過（不刪除雲端檔案）
2. **本機存在，雲端不存在** → ✅ 上傳
3. **兩邊都存在**：
   - 本機較新 → ✅ 上傳（更新雲端檔案）
   - 雲端較新 → ⏭️ 跳過（保留雲端版本）
   - 時間相同 → ⏭️ 跳過（無需同步）

### 與雙向同步的差異

| 項目 | 雙向同步 | 僅上傳模式 |
|------|---------|-----------|
| 上傳本機新增檔案 | ✅ | ✅ |
| 上傳本機更新檔案 | ✅ | ✅ |
| 下載雲端新增檔案 | ✅ | ❌ |
| 下載雲端更新檔案 | ✅ | ❌ |
| 覆蓋雲端較新檔案 | ✅ | ❌ |
| 刪除雲端多餘檔案 | ✅ | ❌ |

## 使用場景

### 場景 1：推送本機變更到雲端，但保留雲端修改

```bash
# 上傳本機變更，但不覆蓋雲端較新的檔案
python cloud_bidirectional_sync.py --upload-only --local-dir ./scripts
```

**適用情況：**
- 需要推送本機的腳本更新
- 但雲端有其他人修改的檔案需要保留
- 不想讓雲端完全鏡像本機

### 場景 2：增量上傳本機檔案

```bash
# 只上傳新增或更新的檔案
python cloud_bidirectional_sync.py --upload-only --pattern "*.json"
```

**適用情況：**
- 定期同步本機變更到雲端
- 不想影響雲端現有檔案
- 只更新有變更的檔案

### 場景 3：備份本機檔案到雲端

```bash
# 上傳本機備份到雲端，但不覆蓋雲端備份
python cloud_bidirectional_sync.py --upload-only --local-dir ./backups --cloud-dir backups
```

**適用情況：**
- 從本機上傳備份檔案
- 雲端已有部分備份，不想覆蓋
- 只上傳新的備份檔案

## 輸出說明

僅上傳模式執行後會顯示：

```
============================================================
五常雲端空間僅上傳同步（非鏡像）
============================================================

本機目錄: C:\path\to\local
雲端目錄: J:\共用雲端硬碟\五常雲端空間\scripts
同步方向: upload
僅上傳模式: 是（非鏡像，不覆蓋雲端較新檔案，不刪除雲端多餘檔案）

============================================================
同步結果
============================================================
同步時間: 2026-01-21 14:30:22
同步方向: upload
本機目錄: C:\path\to\local
雲端目錄: J:\共用雲端硬碟\五常雲端空間\scripts

上傳 (3 個):
  ✓ file1.json
  ✓ file2.json
  ✓ file3.json

跳過 (5 個):
  - file4.json (僅上傳模式：不覆蓋雲端較新檔案)
  - file5.json (僅上傳模式：不處理雲端多餘檔案)
  - file6.json
  - file7.json
  - file8.json

============================================================
```

## 注意事項

1. ⚠️ **非鏡像同步**：雲端不會完全鏡像本機，會保留雲端獨有的檔案
2. ⚠️ **不覆蓋雲端較新檔案**：如果雲端檔案較新，會保留雲端版本
3. ⚠️ **不刪除雲端多餘檔案**：雲端有但本機沒有的檔案會保留
4. ⚠️ **僅上傳本機變更**：只會上傳本機新增或更新的檔案
5. ⚠️ **自動設定方向**：使用 `--upload-only` 會自動設定 `--direction upload`

## 與其他模式的比較

### 僅上傳模式 vs 雙向同步

```bash
# 僅上傳模式：只上傳，不覆蓋雲端較新檔案
python cloud_bidirectional_sync.py --upload-only

# 雙向同步：完整同步，會覆蓋較新檔案
python cloud_bidirectional_sync.py --direction both
```

### 僅上傳模式 vs 上傳模式

```bash
# 僅上傳模式：不覆蓋雲端較新檔案
python cloud_bidirectional_sync.py --upload-only

# 上傳模式：會覆蓋雲端較新檔案
python cloud_bidirectional_sync.py --direction upload
```

## 範例

### 範例 1：上傳本機腳本，保留雲端修改

```bash
# 上傳本機 scripts 目錄的變更
# 但保留雲端較新的檔案
python cloud_bidirectional_sync.py \
  --upload-only \
  --local-dir ./scripts \
  --cloud-dir scripts
```

### 範例 2：增量上傳配置檔案

```bash
# 只上傳本機新增或更新的 JSON 配置檔案
# 不覆蓋雲端較新的配置
python cloud_bidirectional_sync.py \
  --upload-only \
  --pattern "*.json" \
  --local-dir ./config
```

## 相關文檔

- `BIDIRECTIONAL_SYNC_GUIDE.md` - 雙向同步使用指南
- `DOWNLOAD_ONLY_MODE.md` - 僅下載模式（非鏡像）使用說明
- `CLOUD_SYNC_CONFIG.md` - 雲端同步配置說明
