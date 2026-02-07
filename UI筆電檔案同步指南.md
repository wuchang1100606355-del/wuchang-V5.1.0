# UI筆電檔案同步指南

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 📋 功能概述

本工具用於在區網中偵測UI筆電設備，比較兩個基地端的檔案差異，並執行最優同步。

---

## 🔧 已創建的工具

### 1. 檔案比較與同步工具

**文件**: `scripts/compare_and_sync_bases.py`

**功能**:
- ✅ 掃描兩個基地端的檔案
- ✅ 計算檔案雜湊值（MD5）
- ✅ 比較檔案差異（相同、不同、獨有）
- ✅ 執行最優同步（使用較新或較大的檔案）
- ✅ 支援預覽模式（dry-run）

### 2. UI筆電同步工具

**文件**: `scripts/sync_with_ui_laptop.py`

**功能**:
- ✅ 自動偵測區網中的UI筆電
- ✅ 讀取設備偵測記錄
- ✅ 檢查網絡連接性
- ✅ 自動執行檔案比較與同步

---

## 🚀 使用方法

### 方法1: 自動偵測UI筆電（推薦）

```powershell
# 預覽模式（推薦先執行）
python scripts/sync_with_ui_laptop.py --dry-run

# 實際執行同步
python scripts/sync_with_ui_laptop.py
```

### 方法2: 指定遠端路徑

```powershell
# 使用網絡共享路徑
python scripts/sync_with_ui_laptop.py --remote-path "\\192.168.50.88\wuchang"

# 使用本地路徑（如果已映射）
python scripts/sync_with_ui_laptop.py --remote-path "Z:\wuchang"
```

### 方法3: 直接使用比較工具

```powershell
# 比較兩個基地端
python scripts/compare_and_sync_bases.py \
  --base1 "C:\wuchang V5.1.0" \
  --base2 "\\192.168.50.88\wuchang" \
  --base1-name "本地基地端" \
  --base2-name "UI筆電基地端" \
  --sync-to base1 \
  --strategy newer \
  --dry-run

# 實際執行同步
python scripts/compare_and_sync_bases.py \
  --base1 "C:\wuchang V5.1.0" \
  --base2 "\\192.168.50.88\wuchang" \
  --base1-name "本地基地端" \
  --base2-name "UI筆電基地端" \
  --sync-to base1 \
  --strategy newer
```

---

## 📊 同步策略

### newer（較新，預設）

使用修改時間較新的檔案版本。

**適用場景**:
- 兩個基地端都有更新
- 需要保留最新的修改

### larger（較大）

使用檔案大小較大的版本。

**適用場景**:
- 檔案可能被截斷
- 需要保留最完整的內容

---

## 🔍 偵測流程

1. **讀取設備記錄**: 從 `logs/connected_devices_*.json` 讀取最新的設備記錄
2. **識別UI筆電**: 根據主機名（MSI、Laptop等）和IP地址（192.168.50.8*）識別
3. **檢查連接性**: 確認設備在線
4. **尋找共享路徑**: 自動檢查常見的網絡共享路徑

---

## 📋 同步流程

1. **掃描檔案**: 掃描兩個基地端的所有檔案
2. **計算雜湊**: 計算每個檔案的MD5雜湊值
3. **比較差異**:
   - 相同檔案（雜湊相同）
   - 不同檔案（雜湊不同）
   - 獨有檔案（只存在於一個基地端）
4. **決定最佳版本**: 根據策略（newer/larger）決定使用哪個版本
5. **執行同步**: 複製或更新檔案到目標基地端

---

## ⚙️ 配置選項

### 同步方向

- `base1`: 同步到基地端1（本地）
- `base2`: 同步到基地端2（遠端）
- `bidirectional`: 雙向同步（需要手動指定）

### 同步策略

- `newer`: 使用較新的檔案（預設）
- `larger`: 使用較大的檔案

### 預覽模式

- `--dry-run`: 只顯示將要執行的操作，不實際執行

---

## 📄 輸出檔案

### 比較結果

**位置**: `logs/base_comparison_YYYYMMDD_HHMMSS.json`

**內容**:
- 兩個基地端的檔案列表
- 相同檔案列表
- 不同檔案列表
- 獨有檔案列表
- 檔案詳細資訊（大小、修改時間、雜湊）

---

## 🔒 安全機制

1. **備份**: 更新檔案前會自動備份（.backup副檔名）
2. **預覽模式**: 建議先使用 `--dry-run` 預覽
3. **錯誤處理**: 同步失敗不會中斷整個流程

---

## ⚠️ 注意事項

1. **網絡共享**: 需要確保網絡共享已正確配置
2. **權限**: 需要對兩個基地端都有讀寫權限
3. **大檔案**: 大檔案同步可能需要較長時間
4. **忽略模式**: 預設忽略 `.git`、`__pycache__`、`node_modules` 等目錄

---

## 💡 使用建議

1. **首次使用**: 建議先執行 `--dry-run` 預覽
2. **備份**: 同步前建議手動備份重要檔案
3. **網絡檢查**: 確保網絡連接穩定
4. **權限確認**: 確認對目標路徑有寫入權限

---

## 🚀 快速開始

```powershell
# 1. 預覽同步計劃
python scripts/sync_with_ui_laptop.py --dry-run

# 2. 確認無誤後執行同步
python scripts/sync_with_ui_laptop.py

# 3. 查看同步結果
Get-Content logs\base_comparison_*.json | ConvertFrom-Json | Format-List
```

---

**報告生成時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「UI筆電檔案同步工具已準備就緒，可以開始同步了！」* ✨
