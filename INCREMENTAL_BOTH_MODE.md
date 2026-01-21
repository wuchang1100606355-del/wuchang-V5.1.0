# 雙向增量同步模式說明

## 概述

雙向增量同步模式（`--incremental-both`）是一種**互相增加變更**的同步模式：
- ✅ **互相增加變更**：下載雲端新增/更新，上傳本機新增/更新
- ✅ **不覆蓋較新檔案**：保留任何一方較新的版本
- ✅ **非鏡像同步**：不會讓任何一方完全鏡像另一方

## 使用方式

### 基本用法

```bash
# 雙向增量同步（互相增加變更）
python cloud_bidirectional_sync.py --incremental-both

# C:\wuchang V5.1.0 專用（預設為雙向增量）
python sync_wuchang_to_cloud.py
```

## 同步邏輯

### 雙向增量模式的規則

1. **本機不存在，雲端存在** → ✅ 下載（增加變更）
2. **本機存在，雲端不存在** → ✅ 上傳（增加變更）
3. **兩邊都存在**：
   - 雲端較新 → ✅ 下載（增加變更）
   - 本機較新 → ✅ 上傳（增加變更）
   - 時間相同 → ⏭️ 跳過（無需同步）

### 與其他模式的差異

| 項目 | 雙向同步 | 雙向增量模式 |
|------|---------|------------|
| 下載雲端新增檔案 | ✅ | ✅ |
| 下載雲端更新檔案 | ✅ | ✅ |
| 上傳本機新增檔案 | ✅ | ✅ |
| 上傳本機更新檔案 | ✅ | ✅ |
| 覆蓋較新檔案 | ✅ | ❌ |
| 刪除多餘檔案 | ✅ | ❌ |

## 使用場景

### 場景 1：C:\wuchang V5.1.0 與五常雲端空間同步

```bash
# 互相增加變更，不覆蓋較新檔案
python sync_wuchang_to_cloud.py --mode incremental-both
```

**適用情況：**
- C:\wuchang V5.1.0 與五常雲端空間需要互相同步變更
- 但不想覆蓋任何一方較新的檔案
- 只想增加變更，不做鏡像同步

### 場景 2：其他目錄單向下載

對於非 C:\wuchang V5.1.0 的目錄，使用僅下載模式：

```bash
# 只從雲端下載，本地不再增加檔案
python cloud_bidirectional_sync.py --download-only --cloud-dir other_dir
```

## 輸出說明

雙向增量模式執行後會顯示：

```
============================================================
五常雲端空間雙向增量同步（互相增加變更）
============================================================

本機目錄: C:\wuchang V5.1.0\wuchang-V5.1.0
雲端目錄: J:\共用雲端硬碟\五常雲端空間\scripts
同步方向: both
雙向增量模式: 是（互相增加變更，不覆蓋任何一方較新的檔案）

============================================================
同步結果
============================================================
同步時間: 2026-01-21 14:30:22
同步方向: both
本機目錄: C:\wuchang V5.1.0\wuchang-V5.1.0
雲端目錄: J:\共用雲端硬碟\五常雲端空間\scripts

下載 (3 個):
  ✓ file1.json
  ✓ file2.json
  ✓ file3.json

上傳 (2 個):
  ✓ local_file1.json
  ✓ local_file2.json

跳過 (5 個):
  - file4.json (雙向增量：本機較新，保留本機版本)
  - file5.json (雙向增量：雲端較新，保留雲端版本)
  - file6.json (雙向增量：檔案已同步)
  - file7.json (雙向增量：檔案已同步)
  - file8.json (雙向增量：檔案已同步)

============================================================
```

## 注意事項

1. ⚠️ **互相增加變更**：只會增加變更，不會覆蓋較新檔案
2. ⚠️ **不覆蓋較新檔案**：如果一方較新，會保留該版本
3. ⚠️ **不刪除多餘檔案**：任何一方多餘的檔案會保留
4. ⚠️ **非鏡像同步**：不會讓任何一方完全鏡像另一方
5. ⚠️ **自動設定方向**：使用 `--incremental-both` 會自動設定 `--direction both`

## 與其他模式的比較

### 雙向增量模式 vs 雙向同步

```bash
# 雙向增量模式：互相增加變更，不覆蓋較新檔案
python cloud_bidirectional_sync.py --incremental-both

# 雙向同步：完整同步，會覆蓋較新檔案
python cloud_bidirectional_sync.py --direction both
```

### 雙向增量模式 vs 僅下載模式

```bash
# 雙向增量模式：互相增加變更
python cloud_bidirectional_sync.py --incremental-both

# 僅下載模式：只下載，不上傳
python cloud_bidirectional_sync.py --download-only
```

## 範例

### 範例 1：C:\wuchang V5.1.0 雙向增量同步

```bash
# 互相增加變更，不覆蓋較新檔案
python sync_wuchang_to_cloud.py --mode incremental-both
```

### 範例 2：其他目錄僅下載

```bash
# 只從雲端下載，本地不再增加檔案
python cloud_bidirectional_sync.py \
  --download-only \
  --cloud-dir other_data \
  --local-dir ./other_data
```

## 相關文檔

- `BIDIRECTIONAL_SYNC_GUIDE.md` - 雙向同步使用指南
- `DOWNLOAD_ONLY_MODE.md` - 僅下載模式說明
- `UPLOAD_ONLY_MODE.md` - 僅上傳模式說明
- `WUCHANG_SYNC_GUIDE.md` - C:\wuchang V5.1.0 同步指南
