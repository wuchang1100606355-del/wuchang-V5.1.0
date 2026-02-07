# UI 指令檔案接收指南

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 📋 功能概述

本工具用於從 UI 筆電接收指令檔案，同步兩個基地端的檔案差異，並執行最優同步。

---

## 🔧 已創建的工具

### 1. 互動式接收工具

**文件**: `scripts/receive_ui_files.ps1`

**功能**:
- ✅ 自動偵測區網中的 UI 筆電設備
- ✅ 檢查網絡連接性
- ✅ 自動尋找網絡共享路徑
- ✅ 預覽同步計劃
- ✅ 互動式確認執行

**使用方式**:
```powershell
.\scripts\receive_ui_files.ps1
```

### 2. 自動接收工具

**文件**: `scripts/auto_receive_ui_files.ps1`

**功能**:
- ✅ 自動偵測 UI 筆電
- ✅ 無需互動，自動執行
- ✅ 支援預覽模式和實際同步
- ✅ 支援指定 IP 和路徑

**使用方式**:
```powershell
# 預覽模式（推薦先執行）
.\scripts\auto_receive_ui_files.ps1 -DryRun

# 實際同步
.\scripts\auto_receive_ui_files.ps1 -DryRun:$false

# 指定 IP 和路徑
.\scripts\auto_receive_ui_files.ps1 -RemoteIP '192.168.50.84' -RemotePath '\\192.168.50.84\wuchang'
```

### 3. Python 同步工具

**文件**: `scripts/sync_with_ui_laptop.py`

**功能**:
- ✅ 自動偵測區網中的 UI 筆電
- ✅ 讀取設備偵測記錄
- ✅ 比較檔案差異
- ✅ 執行最優同步

**使用方式**:
```powershell
# 預覽模式
python scripts/sync_with_ui_laptop.py --dry-run

# 指定遠端路徑
python scripts/sync_with_ui_laptop.py --remote-path "\\192.168.50.84\wuchang" --dry-run

# 實際同步
python scripts/sync_with_ui_laptop.py --remote-path "\\192.168.50.84\wuchang"
```

---

## 🚀 使用流程

### 方式 1: 使用 PowerShell 工具（推薦）

#### 步驟 1: 互動式接收（首次使用推薦）

```powershell
.\scripts\receive_ui_files.ps1
```

此工具會：
1. 自動偵測 UI 筆電設備
2. 檢查網絡連接性
3. 自動尋找網絡共享路徑
4. 顯示預覽同步計劃
5. 詢問是否執行實際同步

#### 步驟 2: 自動接收（已確認配置）

```powershell
# 預覽
.\scripts\auto_receive_ui_files.ps1 -DryRun

# 實際同步
.\scripts\auto_receive_ui_files.ps1 -DryRun:$false
```

### 方式 2: 使用 Python 工具

```powershell
# 預覽模式
python scripts/sync_with_ui_laptop.py --dry-run --remote-path "\\192.168.50.84\wuchang"

# 實際同步
python scripts/sync_with_ui_laptop.py --remote-path "\\192.168.50.84\wuchang"
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

1. **自動偵測**: 掃描常見的 UI 筆電 IP 地址
   - 192.168.50.84 (LUNGsMSI)
   - 192.168.50.88
   - 192.168.50.80

2. **檢查連接性**: 確認設備在線

3. **尋找共享路徑**: 自動檢查常見的網絡共享路徑
   - `\\IP\wuchang`
   - `\\IP\C$\wuchang`
   - `\\IP\Users\wuchang`

---

## ⚙️ 配置選項

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
# 1. 互動式接收（推薦首次使用）
.\scripts\receive_ui_files.ps1

# 2. 或自動預覽
.\scripts\auto_receive_ui_files.ps1 -DryRun

# 3. 確認無誤後執行同步
.\scripts\auto_receive_ui_files.ps1 -DryRun:$false

# 4. 查看同步結果
Get-Content logs\base_comparison_*.json | ConvertFrom-Json | Format-List
```

---

**報告生成時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「UI 指令檔案接收工具已準備就緒，可以開始接收了！」* ✨
