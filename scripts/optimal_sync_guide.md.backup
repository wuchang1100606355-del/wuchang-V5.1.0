# 最優同步指南

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 📋 功能概述

最優同步工具用於比較兩個基地端的檔案差異，並根據最優策略（較新或較大）自動同步檔案。

---

## 🔧 已創建的工具

### 1. 最優同步腳本

**文件**: `scripts/optimal_sync.ps1`

**功能**:
- ✅ 自動偵測 UI 筆電設備
- ✅ 自動尋找網絡共享路徑
- ✅ 執行最優同步策略
- ✅ 支援預覽模式和實際同步
- ✅ 支援多種同步策略（newer/larger）

**使用方式**:
```powershell
# 預覽模式（推薦先執行）
.\scripts\optimal_sync.ps1 -DryRun

# 實際同步
.\scripts\optimal_sync.ps1 -DryRun:$false

# 指定遠端路徑
.\scripts\optimal_sync.ps1 -RemotePath "\\192.168.50.84\wuchang" -Strategy newer

# 使用較大檔案策略
.\scripts\optimal_sync.ps1 -Strategy larger
```

### 2. Python 比較與同步工具

**文件**: `scripts/compare_and_sync_bases.py`

**功能**:
- ✅ 掃描兩個基地端的檔案
- ✅ 計算檔案雜湊值（MD5）
- ✅ 比較檔案差異（相同、不同、獨有）
- ✅ 執行最優同步（使用較新或較大的檔案）
- ✅ 支援預覽模式（dry-run）

**使用方式**:
```powershell
# 比較兩個基地端
python scripts/compare_and_sync_bases.py \
  --base1 "C:\wuchang V5.1.0" \
  --base2 "\\192.168.50.84\wuchang" \
  --base1-name "本地基地端" \
  --base2-name "UI筆電基地端" \
  --sync-to base1 \
  --strategy newer \
  --dry-run

# 實際執行同步
python scripts/compare_and_sync_bases.py \
  --base1 "C:\wuchang V5.1.0" \
  --base2 "\\192.168.50.84\wuchang" \
  --base1-name "本地基地端" \
  --base2-name "UI筆電基地端" \
  --sync-to base1 \
  --strategy newer
```

---

## 🚀 使用流程

### 方式 1: 使用 PowerShell 工具（推薦）

#### 步驟 1: 預覽同步計劃

```powershell
.\scripts\optimal_sync.ps1 -DryRun
```

此工具會：
1. 自動偵測 UI 筆電設備
2. 檢查網絡連接性
3. 自動尋找網絡共享路徑
4. 顯示預覽同步計劃

#### 步驟 2: 執行實際同步

```powershell
.\scripts\optimal_sync.ps1 -DryRun:$false
```

### 方式 2: 使用 Python 工具

```powershell
# 預覽模式
python scripts/compare_and_sync_bases.py \
  --base1 "C:\wuchang V5.1.0" \
  --base2 "\\192.168.50.84\wuchang" \
  --base1-name "本地基地端" \
  --base2-name "UI筆電基地端" \
  --sync-to base1 \
  --strategy newer \
  --dry-run

# 實際同步
python scripts/compare_and_sync_bases.py \
  --base1 "C:\wuchang V5.1.0" \
  --base2 "\\192.168.50.84\wuchang" \
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
- 檔案可能在不同時間被修改

**決策邏輯**:
- 比較檔案的修改時間（mtime）
- 選擇修改時間較新的版本

### larger（較大）

使用檔案大小較大的版本。

**適用場景**:
- 檔案可能被截斷
- 需要保留最完整的內容
- 檔案可能不完整

**決策邏輯**:
- 比較檔案的大小
- 選擇檔案大小較大的版本

---

## 🔍 同步流程

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

### 執行模式

- `--dry-run` / `-DryRun`: 預覽模式，不實際執行
- 無 `--dry-run`: 實際執行同步

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
2. **預覽模式**: 建議先使用預覽模式
3. **錯誤處理**: 同步失敗不會中斷整個流程

---

## ⚠️ 注意事項

1. **網絡共享**: 需要確保網絡共享已正確配置
2. **權限**: 需要對兩個基地端都有讀寫權限
3. **大檔案**: 大檔案同步可能需要較長時間
4. **忽略模式**: 預設忽略 `.git`、`__pycache__`、`node_modules` 等目錄

---

## 💡 使用建議

1. **首次使用**: 建議先執行預覽模式
2. **備份**: 同步前建議手動備份重要檔案
3. **網絡檢查**: 確保網絡連接穩定
4. **權限確認**: 確認對目標路徑有寫入權限

---

## 🚀 快速開始

```powershell
# 1. 預覽同步計劃（推薦先執行）
.\scripts\optimal_sync.ps1 -DryRun

# 2. 確認無誤後執行同步
.\scripts\optimal_sync.ps1 -DryRun:$false

# 3. 查看同步結果
Get-Content logs\base_comparison_*.json | ConvertFrom-Json | Format-List
```

---

**報告生成時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「最優同步工具已準備就緒，可以開始最優同步了！」* ✨
