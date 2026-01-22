# 雲端硬碟系統歷史資料庫指南

## 📋 概述

在雲端硬碟建立系統歷史資料庫，分類管理各種資料，未來備份只保留路徑檔案（不實際備份內容）。

## 🗂️ 資料庫結構

```
系統歷史資料庫/
├── database_index.json          # 資料庫索引
├── 備份/
│   ├── 完整備份/
│   ├── 增量備份/
│   ├── 設定備份/
│   └── 資料備份/
├── 健康報告/
│   ├── 每日健康報告/
│   ├── 週報/
│   ├── 月報/
│   └── 異常報告/
├── 部署日誌/
│   ├── 部署記錄/
│   ├── 更新記錄/
│   └── 回滾記錄/
├── 稽核日誌/
│   ├── 風險動作/
│   ├── 授權記錄/
│   └── 變更記錄/
├── 工作日誌/
│   ├── 地端小j日誌/
│   ├── 雲端小j日誌/
│   └── 協作記錄/
├── DNS變更記錄/
│   ├── DNS更改清單/
│   └── DNS替換記錄/
├── 路由器設定/
│   ├── 設定備份/
│   ├── 端口轉發記錄/
│   └── 防火牆規則/
└── 系統快照/
    ├── 完整快照/
    ├── 增量快照/
    └── 配置快照/
```

## 📄 路徑檔案格式

每個歸檔的檔案都會建立一個 `.path.json` 檔案，包含：

```json
{
  "version": "1.0",
  "file_type": "path_reference",
  "local_path": "C:\\wuchang V5.1.0\\backups\\backup_20260122.json",
  "cloud_path": "系統歷史資料庫/備份/完整備份/backup_20260122.json.path.json",
  "file_info": {
    "name": "backup_20260122.json",
    "size": 1024000,
    "modified": "2026-01-22T08:00:00",
    "hash": "sha256_hash_here"
  },
  "metadata": {
    "created": "2026-01-22T08:00:00",
    "category": "backups",
    "subcategory": "完整備份",
    "description": "系統完整備份"
  }
}
```

## 🔧 使用方式

### 1. 初始化資料庫結構

```bash
python cloud_history_database.py --init
```

### 2. 歸檔所有歷史檔案

```bash
python cloud_history_database.py --archive-all
```

### 3. 歸檔指定備份

```bash
python cloud_history_database.py --archive-backup "backups/backup_20260122.json"
```

### 4. 歸檔指定報告

```bash
python cloud_history_database.py --archive-report "健康報告/健康報告_20260122.md"
```

### 5. 指定雲端硬碟路徑

```bash
python cloud_history_database.py --init --cloud-path "J:\我的雲端硬碟"
```

## 📦 分類說明

### 1. 備份 (backups)
- **用途**: 系統備份記錄
- **內容**: 只保留路徑檔案，不實際備份內容
- **子分類**:
  - 完整備份
  - 增量備份
  - 設定備份
  - 資料備份

### 2. 健康報告 (health_reports)
- **用途**: 系統健康檢查報告
- **內容**: 健康報告的路徑檔案
- **子分類**:
  - 每日健康報告
  - 週報
  - 月報
  - 異常報告

### 3. 部署日誌 (deployment_logs)
- **用途**: 系統部署和更新記錄
- **內容**: 部署記錄的路徑檔案
- **子分類**:
  - 部署記錄
  - 更新記錄
  - 回滾記錄

### 4. 稽核日誌 (audit_logs)
- **用途**: 風險動作稽核記錄
- **內容**: 稽核記錄的路徑檔案
- **子分類**:
  - 風險動作
  - 授權記錄
  - 變更記錄

### 5. 工作日誌 (work_logs)
- **用途**: 雙J協作工作日誌
- **內容**: 工作日誌的路徑檔案
- **子分類**:
  - 地端小j日誌
  - 雲端小j日誌
  - 協作記錄

### 6. DNS變更記錄 (dns_changes)
- **用途**: DNS更改清單和記錄
- **內容**: DNS變更記錄的路徑檔案
- **子分類**:
  - DNS更改清單
  - DNS替換記錄

### 7. 路由器設定 (router_configs)
- **用途**: 路由器設定備份
- **內容**: 只保留路徑檔案
- **子分類**:
  - 設定備份
  - 端口轉發記錄
  - 防火牆規則

### 8. 系統快照 (system_snapshots)
- **用途**: 系統狀態快照記錄
- **內容**: 只保留路徑檔案
- **子分類**:
  - 完整快照
  - 增量快照
  - 配置快照

## 🔄 自動化整合

### 與備份系統整合

修改 `complete_uninstall.py` 和備份腳本，在備份後自動歸檔路徑：

```python
from cloud_history_database import archive_backup_path

# 備份完成後
archive_backup_path(backup_path, description="系統完整備份")
```

### 與健康報告整合

修改 `generate_health_report.py`，在生成報告後自動歸檔：

```python
from cloud_history_database import archive_health_report

# 報告生成後
archive_health_report(report_path)
```

## 📝 路徑檔案管理

### 查詢路徑檔案

```python
from cloud_history_database import get_cloud_drive_path
import json

cloud_root = get_cloud_drive_path()
database_root = cloud_root / "系統歷史資料庫"

# 讀取索引
index_file = database_root / "database_index.json"
index = json.loads(index_file.read_text(encoding='utf-8'))

# 查詢特定分類的路徑檔案
category_path = database_root / "備份" / "完整備份"
for path_file in category_path.glob("*.path.json"):
    data = json.loads(path_file.read_text(encoding='utf-8'))
    print(f"本地路徑: {data['local_path']}")
    print(f"檔案大小: {data['file_info']['size']} bytes")
```

### 驗證路徑檔案

路徑檔案包含檔案雜湊值，可用於驗證本地檔案是否仍然存在且未變更。

## ⚠️ 注意事項

1. **路徑檔案**: 只保留路徑和檔案資訊，不實際備份內容
2. **本地檔案**: 確保本地檔案不會被意外刪除
3. **雲端同步**: 依賴雲端硬碟的同步功能
4. **路徑有效性**: 如果本地檔案移動或刪除，路徑檔案將失效

## 🔗 相關檔案

- `cloud_history_database.py` - 資料庫管理主程式
- `CLOUD_HISTORY_DATABASE_GUIDE.md` - 本指南

## 📅 文檔建立日期

2026-01-22
