# 系統地端檔案夾容量分析

**檢查日期**: 2025-01-07  
**總容量**: 1.83 GB (1876.88 MB)

---

## 📊 容量分析

### 主要佔用空間的資料夾

| 資料夾 | 大小 | 說明 |
|--------|------|------|
| **migration_pack** | **1.03 GB** | ⚠️ 遷移備份資料夾（最大） |
| **.venv** | 0.26 GB | Python 虛擬環境 |
| **downloads** | 0.16 GB | 下載檔案 |
| **node_modules** | 0.15 GB | Node.js 依賴套件 |
| **.conda** | 0.14 GB | Conda 環境 |

### 大檔案

| 檔案 | 大小 | 說明 |
|------|------|------|
| **openwebui-data.tar.gz** | **0.91 GB** | ⚠️ OpenWebUI 資料壓縮檔（非常大） |

### 常見快取資料夾

| 類型 | 總大小 | 數量 |
|------|--------|------|
| **migration_pack** | 1.03 GB | 1 個 |
| **Python 虛擬環境** | 0.26 GB | 4 個 |
| **node_modules** | 0.16 GB | 13 個 |
| **__pycache__** | 0.12 GB | 738 個 |

---

## 🎯 清理建議

### 優先清理項目（可釋放約 1.2 GB）

#### 1. migration_pack (1.03 GB) ⚠️
- **說明**: 遷移備份資料夾
- **建議**: 
  - 如果遷移已完成且不需要備份，可以刪除
  - 或壓縮後移到外部儲存
- **可釋放**: ~1.03 GB

#### 2. openwebui-data.tar.gz (0.91 GB) ⚠️
- **說明**: OpenWebUI 資料壓縮檔
- **建議**:
  - 如果已解壓縮且不需要備份，可以刪除
  - 或移到外部儲存
- **可釋放**: ~0.91 GB

#### 3. __pycache__ (0.12 GB)
- **說明**: Python 快取檔案
- **建議**: 可以安全刪除，Python 會自動重新生成
- **可釋放**: ~0.12 GB

#### 4. node_modules (0.16 GB)
- **說明**: Node.js 依賴套件
- **建議**: 
  - 如果不需要開發 Node.js 專案，可以刪除
  - 需要時可透過 `npm install` 重新安裝
- **可釋放**: ~0.16 GB

### 保留項目

#### .venv (0.26 GB)
- **說明**: Python 虛擬環境
- **建議**: **保留**，這是開發環境所需

#### .conda (0.14 GB)
- **說明**: Conda 環境
- **建議**: **保留**，如果使用 Conda 管理環境

#### downloads (0.16 GB)
- **說明**: 下載檔案
- **建議**: 手動檢查並清理不需要的檔案

---

## 🛠️ 清理腳本

### 快速清理腳本

```powershell
# 清理 Python 快取
Get-ChildItem -Path "." -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path "." -Recurse -File -Filter "*.pyc" | Remove-Item -Force

# 清理 node_modules（謹慎使用）
# Get-ChildItem -Path "." -Recurse -Directory -Filter "node_modules" | Remove-Item -Recurse -Force

# 檢查 migration_pack（手動決定是否刪除）
# Remove-Item -Path "migration_pack" -Recurse -Force

# 檢查 openwebui-data.tar.gz（手動決定是否刪除）
# Remove-Item -Path "downloads\openwebui-data.tar.gz" -Force
```

---

## 📋 清理檢查清單

- [ ] 檢查 `migration_pack` 是否還需要（1.03 GB）
- [ ] 檢查 `openwebui-data.tar.gz` 是否還需要（0.91 GB）
- [ ] 清理 `__pycache__` 快取（0.12 GB）
- [ ] 檢查 `downloads` 資料夾中的檔案（0.16 GB）
- [ ] 檢查 `node_modules` 是否還需要（0.16 GB）
- [ ] 檢查 `.git` 歷史記錄大小
- [ ] 檢查是否有重複的備份檔案

---

## 💡 預防措施

### 1. 使用 .gitignore
確保以下項目已加入 `.gitignore`：
- `__pycache__/`
- `*.pyc`
- `node_modules/`
- `.venv/`
- `.conda/`
- `*.tar.gz`
- `downloads/`

### 2. 定期清理
- 每月檢查一次大檔案
- 清理不需要的快取檔案
- 將備份移到外部儲存

### 3. 監控腳本
使用 `scripts/check_disk_usage.ps1` 定期檢查容量

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
