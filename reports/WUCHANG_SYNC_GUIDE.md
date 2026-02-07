# C:\wuchang V5.1.0 與五常雲端空間同步指南

## 概述

`sync_wuchang_to_cloud.py` 是專門用於同步 `C:\wuchang V5.1.0\wuchang-V5.1.0` 與五常雲端空間的工具。

**預設模式：雙向增量同步（incremental-both）**
- 互相增加變更：下載雲端新增/更新，上傳本機新增/更新
- 不覆蓋較新檔案：保留任何一方較新的版本
- 非鏡像同步：不會讓任何一方完全鏡像另一方

## 目錄映射

| 本地目錄 | 雲端目錄 | 說明 |
|---------|---------|------|
| `C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage` | `五常雲端空間/local_storage` | 本地儲存 |
| `C:\wuchang V5.1.0\wuchang-V5.1.0` | `五常雲端空間/scripts` | 腳本檔案 |
| `C:\wuchang V5.1.0\wuchang-V5.1.0` | `五常雲端空間/reports` | 報告檔案 |
| `C:\wuchang V5.1.0\wuchang-V5.1.0` | `五常雲端空間/config` | 配置檔案 |

## 使用方式

### 基本用法

```bash
# 雙向增量同步（互相增加變更，預設模式）
python sync_wuchang_to_cloud.py

# 或明確指定
python sync_wuchang_to_cloud.py --mode incremental-both

# 僅下載變更（非鏡像）
python sync_wuchang_to_cloud.py --mode download-only

# 僅上傳變更（非鏡像）
python sync_wuchang_to_cloud.py --mode upload-only
```

### 指定類別

```bash
# 只同步本地儲存
python sync_wuchang_to_cloud.py --category local_storage

# 只同步腳本
python sync_wuchang_to_cloud.py --category scripts

# 只同步報告
python sync_wuchang_to_cloud.py --category reports

# 只同步配置
python sync_wuchang_to_cloud.py --category config
```

### 指定檔案類型

```bash
# 只同步 JSON 檔案
python sync_wuchang_to_cloud.py --pattern "*.json"

# 只同步 Python 腳本
python sync_wuchang_to_cloud.py --pattern "*.py"
```

### 同步模式

```bash
# 雙向同步（自動判斷方向）
python sync_wuchang_to_cloud.py --mode both

# 僅下載（雲端 -> 本機）
python sync_wuchang_to_cloud.py --mode download

# 僅上傳（本機 -> 雲端）
python sync_wuchang_to_cloud.py --mode upload

# 雙向增量同步（互相增加變更，不覆蓋較新檔案）- 預設
python sync_wuchang_to_cloud.py --mode incremental-both

# 僅下載變更（非鏡像：不覆蓋本機較新檔案）
python sync_wuchang_to_cloud.py --mode download-only

# 僅上傳變更（非鏡像：不覆蓋雲端較新檔案）
python sync_wuchang_to_cloud.py --mode upload-only
```

## 範例場景

### 場景 1：互相增加變更（預設模式）

```bash
# 雙向增量同步所有類別（互相增加變更，不覆蓋較新檔案）
python sync_wuchang_to_cloud.py

# 只同步腳本（互相增加變更）
python sync_wuchang_to_cloud.py --category scripts
```

### 場景 2：從雲端下載最新變更

```bash
# 下載所有類別的最新變更（不覆蓋本機較新檔案）
python sync_wuchang_to_cloud.py --mode download-only

# 只下載腳本變更
python sync_wuchang_to_cloud.py --mode download-only --category scripts
```

### 場景 3：上傳本機變更到雲端

```bash
# 上傳所有類別的變更
python sync_wuchang_to_cloud.py --mode upload-only

# 只上傳本地儲存
python sync_wuchang_to_cloud.py --mode upload-only --category local_storage
```

### 場景 4：雙向同步特定檔案

```bash
# 雙向同步所有 JSON 檔案
python sync_wuchang_to_cloud.py --pattern "*.json" --mode both
```

## 輸出說明

執行後會顯示每個類別的同步結果：

```
======================================================================
C:\wuchang V5.1.0 與五常雲端空間同步
======================================================================

本地目錄: C:\wuchang V5.1.0\wuchang-V5.1.0
雲端空間: J:\共用雲端硬碟\五常雲端空間
同步模式: download-only
同步類別: all

----------------------------------------------------------------------
同步類別: local_storage
  本地: C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage
  雲端: J:\共用雲端硬碟\五常雲端空間\local_storage
----------------------------------------------------------------------

============================================================
同步結果
============================================================
...

======================================================================
同步總結
======================================================================
總下載: 5 個檔案
總上傳: 0 個檔案
總跳過: 10 個檔案
======================================================================
```

## 注意事項

1. ⚠️ **本地目錄**：確保 `C:\wuchang V5.1.0\wuchang-V5.1.0` 目錄存在
2. ⚠️ **雲端空間**：確保五常雲端空間路徑正確配置
3. ⚠️ **預設模式**：預設為雙向增量同步（互相增加變更，不覆蓋較新檔案）
4. ⚠️ **檔案衝突**：在雙向增量模式下，較新的版本會保留，不會覆蓋
5. ⚠️ **其他目錄**：對於非 C:\wuchang V5.1.0 的目錄，建議使用僅下載模式（本地不再增加檔案）

## 其他目錄同步策略

對於非 C:\wuchang V5.1.0 的目錄，建議使用僅下載模式：

```bash
# 只從雲端下載，本地不再增加檔案
python cloud_bidirectional_sync.py --download-only --cloud-dir other_dir
```

**策略：**
- C:\wuchang V5.1.0：雙向增量同步（互相增加變更）
- 其他目錄：僅下載模式（本地不再增加檔案）

## 相關文檔

- `BIDIRECTIONAL_SYNC_GUIDE.md` - 雙向同步使用指南
- `INCREMENTAL_BOTH_MODE.md` - 雙向增量模式說明
- `DOWNLOAD_ONLY_MODE.md` - 僅下載模式說明
- `UPLOAD_ONLY_MODE.md` - 僅上傳模式說明
- `CLOUD_SYNC_CONFIG.md` - 雲端同步配置說明
