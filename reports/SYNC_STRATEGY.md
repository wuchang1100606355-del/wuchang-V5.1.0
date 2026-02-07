# 同步策略說明

## 同步策略總覽

根據目錄類型採用不同的同步策略：

### C:\wuchang V5.1.0 與五常雲端空間
- **模式**：雙向增量同步（incremental-both）
- **行為**：互相增加變更，不覆蓋較新檔案
- **工具**：`sync_wuchang_to_cloud.py`（預設模式）

### 其他目錄
- **模式**：僅下載（download-only）
- **行為**：只從雲端下載，本地不再增加檔案
- **工具**：`cloud_bidirectional_sync.py --download-only`

## 詳細說明

### C:\wuchang V5.1.0 雙向增量同步

**使用方式：**
```bash
# 預設為雙向增量同步
python sync_wuchang_to_cloud.py

# 或明確指定
python sync_wuchang_to_cloud.py --mode incremental-both
```

**同步邏輯：**
1. 本機不存在，雲端存在 → 下載（增加變更）
2. 本機存在，雲端不存在 → 上傳（增加變更）
3. 兩邊都存在：
   - 雲端較新 → 下載（增加變更）
   - 本機較新 → 上傳（增加變更）
   - 時間相同 → 跳過

**特點：**
- ✅ 互相增加變更
- ✅ 不覆蓋較新檔案
- ✅ 非鏡像同步

### 其他目錄僅下載

**使用方式：**
```bash
# 只從雲端下載，本地不再增加檔案
python cloud_bidirectional_sync.py --download-only --cloud-dir other_dir --local-dir ./other_dir
```

**同步邏輯：**
1. 本機不存在，雲端存在 → 下載
2. 本機存在，雲端不存在 → 跳過（不刪除本機檔案）
3. 兩邊都存在：
   - 雲端較新 → 下載
   - 本機較新 → 跳過（不覆蓋本機較新檔案）
   - 時間相同 → 跳過

**特點：**
- ✅ 只下載變更
- ✅ 不覆蓋本機較新檔案
- ✅ 本地不再增加檔案

## 目錄分類

### C:\wuchang V5.1.0 相關目錄
- `C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage` → `五常雲端空間/local_storage`
- `C:\wuchang V5.1.0\wuchang-V5.1.0` → `五常雲端空間/scripts`
- `C:\wuchang V5.1.0\wuchang-V5.1.0` → `五常雲端空間/reports`
- `C:\wuchang V5.1.0\wuchang-V5.1.0` → `五常雲端空間/config`

**同步模式**：雙向增量（incremental-both）

### 其他目錄
- 所有非 C:\wuchang V5.1.0 的目錄

**同步模式**：僅下載（download-only）

## 使用範例

### 範例 1：同步 C:\wuchang V5.1.0（雙向增量）

```bash
# 互相增加變更，不覆蓋較新檔案
python sync_wuchang_to_cloud.py

# 只同步本地儲存
python sync_wuchang_to_cloud.py --category local_storage
```

### 範例 2：同步其他目錄（僅下載）

```bash
# 只從雲端下載，本地不再增加檔案
python cloud_bidirectional_sync.py \
  --download-only \
  --cloud-dir other_data \
  --local-dir ./other_data
```

## 注意事項

1. ⚠️ **C:\wuchang V5.1.0**：使用雙向增量同步，互相增加變更
2. ⚠️ **其他目錄**：使用僅下載模式，本地不再增加檔案
3. ⚠️ **不覆蓋較新檔案**：兩種模式都不會覆蓋較新的檔案
4. ⚠️ **非鏡像同步**：不會讓任何一方完全鏡像另一方

## 相關文檔

- `INCREMENTAL_BOTH_MODE.md` - 雙向增量模式說明
- `DOWNLOAD_ONLY_MODE.md` - 僅下載模式說明
- `WUCHANG_SYNC_GUIDE.md` - C:\wuchang V5.1.0 同步指南
- `CLOUD_SYNC_CONFIG.md` - 雲端同步配置說明
