# 僅下載模式（非鏡像）使用說明

## 概述

僅下載模式（`--download-only`）是一種**非鏡像同步**模式：
- ✅ **只下載變更**：僅下載雲端新增或更新的檔案
- ✅ **不覆蓋本機較新檔案**：如果本機檔案較新，保留本機版本
- ✅ **不刪除本機多餘檔案**：本機有但雲端沒有的檔案會保留
- ✅ **非鏡像同步**：不會讓本機完全鏡像雲端

## 使用方式

### 基本用法

```bash
# 僅下載模式（非鏡像）
python cloud_bidirectional_sync.py --download-only

# 指定目錄
python cloud_bidirectional_sync.py --download-only --cloud-dir reports --local-dir ./local_reports

# 指定檔案類型
python cloud_bidirectional_sync.py --download-only --pattern "*.json"
```

## 同步邏輯

### 僅下載模式的規則

1. **本機不存在，雲端存在** → ✅ 下載
2. **本機存在，雲端不存在** → ⏭️ 跳過（不刪除本機檔案）
3. **兩邊都存在**：
   - 雲端較新 → ✅ 下載（更新本機檔案）
   - 本機較新 → ⏭️ 跳過（保留本機版本）
   - 時間相同 → ⏭️ 跳過（無需同步）

### 與雙向同步的差異

| 項目 | 雙向同步 | 僅下載模式 |
|------|---------|-----------|
| 下載雲端新增檔案 | ✅ | ✅ |
| 下載雲端更新檔案 | ✅ | ✅ |
| 上傳本機新增檔案 | ✅ | ❌ |
| 上傳本機更新檔案 | ✅ | ❌ |
| 覆蓋本機較新檔案 | ✅ | ❌ |
| 刪除本機多餘檔案 | ✅ | ❌ |

## 使用場景

### 場景 1：獲取雲端最新變更，但保留本機修改

```bash
# 下載雲端變更，但不覆蓋本機較新的檔案
python cloud_bidirectional_sync.py --download-only --cloud-dir reports
```

**適用情況：**
- 需要獲取雲端的最新報告
- 但本機有本地修改的檔案需要保留
- 不想讓本機完全鏡像雲端

### 場景 2：增量更新本機檔案

```bash
# 只下載新增或更新的檔案
python cloud_bidirectional_sync.py --download-only --pattern "*.json"
```

**適用情況：**
- 定期同步雲端變更
- 不想影響本機現有檔案
- 只更新有變更的檔案

### 場景 3：備份雲端檔案到本機

```bash
# 下載雲端備份到本機，但不覆蓋本機檔案
python cloud_bidirectional_sync.py --download-only --cloud-dir backups
```

**適用情況：**
- 從雲端下載備份檔案
- 本機已有部分備份，不想覆蓋
- 只下載新的備份檔案

## 輸出說明

僅下載模式執行後會顯示：

```
============================================================
五常雲端空間僅下載同步（非鏡像）
============================================================

本機目錄: C:\path\to\local
雲端目錄: J:\共用雲端硬碟\五常雲端空間\reports
同步方向: download
僅下載模式: 是（非鏡像，不覆蓋本機較新檔案，不刪除本機多餘檔案）

============================================================
同步結果
============================================================
同步時間: 2026-01-21 14:30:22
同步方向: download
本機目錄: C:\path\to\local
雲端目錄: J:\共用雲端硬碟\五常雲端空間\reports

下載 (3 個):
  ✓ file1.json
  ✓ file2.json
  ✓ file3.json

跳過 (5 個):
  - file4.json (僅下載模式：不覆蓋本機較新檔案)
  - file5.json (僅下載模式：不處理本機多餘檔案)
  - file6.json
  - file7.json
  - file8.json

============================================================
```

## 注意事項

1. ⚠️ **非鏡像同步**：本機不會完全鏡像雲端，會保留本機獨有的檔案
2. ⚠️ **不覆蓋本機較新檔案**：如果本機檔案較新，會保留本機版本
3. ⚠️ **不刪除本機多餘檔案**：本機有但雲端沒有的檔案會保留
4. ⚠️ **僅下載雲端變更**：只會下載雲端新增或更新的檔案
5. ⚠️ **自動設定方向**：使用 `--download-only` 會自動設定 `--direction download`

## 與其他模式的比較

### 僅下載模式 vs 雙向同步

```bash
# 僅下載模式：只下載，不覆蓋本機較新檔案
python cloud_bidirectional_sync.py --download-only

# 雙向同步：完整同步，會覆蓋較新檔案
python cloud_bidirectional_sync.py --direction both
```

### 僅下載模式 vs 下載模式

```bash
# 僅下載模式：不覆蓋本機較新檔案
python cloud_bidirectional_sync.py --download-only

# 下載模式：會覆蓋本機較新檔案
python cloud_bidirectional_sync.py --direction download
```

## 範例

### 範例 1：下載雲端報告，保留本機修改

```bash
# 下載雲端 reports 目錄的變更
# 但保留本機較新的檔案
python cloud_bidirectional_sync.py \
  --download-only \
  --cloud-dir reports \
  --local-dir ./local_reports
```

### 範例 2：增量更新配置檔案

```bash
# 只下載雲端新增或更新的 JSON 配置檔案
# 不覆蓋本機較新的配置
python cloud_bidirectional_sync.py \
  --download-only \
  --pattern "*.json" \
  --cloud-dir config
```

## 相關文檔

- `BIDIRECTIONAL_SYNC_GUIDE.md` - 雙向同步使用指南
- `CLOUD_SYNC_CONFIG.md` - 雲端同步配置說明
