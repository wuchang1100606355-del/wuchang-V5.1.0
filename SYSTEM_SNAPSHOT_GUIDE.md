# 系統存檔及回滾點快照指南

**更新日期**: 2026-01-18  
**系統版本**: Wuchang OS V5.1.0

---

## 📋 概述

系統存檔及回滾點快照功能允許您：

- 創建系統完整快照（包括 Docker 卷、數據庫、配置文件）
- 建立回滾點以便快速恢復
- 支持 Hyper-V VM 快照
- 記錄系統狀態以便追蹤

---

## 🚀 快速開始

### 創建系統快照

```powershell
# 基本快照
powershell -ExecutionPolicy Bypass -File scripts\create_system_snapshot.ps1

# 指定名稱的快照
powershell -ExecutionPolicy Bypass -File scripts\create_system_snapshot.ps1 -SnapshotName "before_update"

# 完整備份（包含所有配置文件）
powershell -ExecutionPolicy Bypass -File scripts\create_system_snapshot.ps1 -SnapshotName "full_backup" -FullBackup

# 包含 Hyper-V VM 快照
powershell -ExecutionPolicy Bypass -File scripts\create_system_snapshot.ps1 -SnapshotName "with_vm" -IncludeVM
```

### 查看回滾點列表

```powershell
powershell -ExecutionPolicy Bypass -File scripts\list_rollback_points.ps1
```

### 恢復快照

```powershell
# 預覽恢復（不會實際執行）
powershell -ExecutionPolicy Bypass -File scripts\restore_from_snapshot.ps1 -SnapshotName "snapshot_20260118_120000" -WhatIf

# 實際恢復
powershell -ExecutionPolicy Bypass -File scripts\restore_from_snapshot.ps1 -SnapshotName "snapshot_20260118_120000"
```

---

## 📦 快照內容

### 標準快照包含

1. **系統狀態記錄**
   - Docker 版本
   - 容器列表和狀態
   - 卷列表
   - 網絡列表

2. **Docker 卷備份**
   - 所有 Docker 卷的完整備份
   - 格式: `卷名_時間戳.tar.gz`

3. **數據庫備份**
   - PostgreSQL 數據庫備份
   - 包括: admin, postgres, odoo
   - 格式: `數據庫名_時間戳.sql`

4. **配置文件備份**
   - `docker-compose.yml`
   - `docker-compose-ai.yml`
   - `requirements.txt`
   - `wuchang_os/Caddyfile`
   - `config/odoo.conf`
   - `config/official_ai_identity.json`
   - `wuchang.code-workspace`

5. **Docker Compose 配置**
   - 解析後的配置
   - 所有 compose 文件

6. **元數據**
   - 快照信息
   - 備份清單
   - 系統狀態

### 完整備份（-FullBackup）

額外包含：

- `config/` 目錄
- `scripts/` 目錄
- `wuchang_os/addons/` 目錄
- `control_center.html`
- `command_center.html`

### VM 快照（-IncludeVM）

如果啟用，會為所有 Hyper-V VM 創建快照：

- 快照名稱: `Snapshot-快照名稱`
- 支持運行中和已關閉的 VM

---

## 📁 快照結構

```
backups/
├── snapshots/
│   └── snapshot_20260118_120000/
│       ├── metadata.json          # 快照元數據
│       ├── volumes/               # Docker 卷備份
│       │   ├── odoo-db-data_20260118_120000.tar.gz
│       │   └── odoo-web-data_20260118_120000.tar.gz
│       ├── database/              # 數據庫備份
│       │   ├── admin_20260118_120000.sql
│       │   └── odoo_20260118_120000.sql
│       ├── config/                # 配置文件
│       │   ├── docker-compose.yml
│       │   └── ...
│       └── docker-compose/         # Docker Compose 配置
│           └── docker-compose-resolved.yml
└── rollback_points/
    └── rollback_index.json        # 回滾點索引
```

---

## 🔄 恢復流程

### 1. 預覽恢復

在實際恢復前，建議先預覽：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\restore_from_snapshot.ps1 -SnapshotName "快照名稱" -WhatIf
```

### 2. 執行恢復

恢復過程包括：

1. 停止當前服務
2. 恢復 Docker 卷
3. 恢復數據庫
4. 恢復配置文件

### 3. 驗證恢復

恢復完成後：

```powershell
# 啟動服務
docker-compose up -d

# 檢查服務狀態
docker-compose ps

# 檢查數據庫
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "\dt"
```

---

## 📊 快照管理

### 查看快照列表

```powershell
# 使用腳本
powershell -ExecutionPolicy Bypass -File scripts\list_rollback_points.ps1

# 手動查看
Get-Content backups\rollback_points\rollback_index.json | ConvertFrom-Json | Format-Table
```

### 查看快照詳情

```powershell
$snapshot = Get-Content "backups\snapshots\snapshot_20260118_120000\metadata.json" | ConvertFrom-Json
$snapshot | ConvertTo-Json -Depth 10
```

### 刪除舊快照

```powershell
# 刪除特定快照
Remove-Item -Path "backups\snapshots\snapshot_20260118_120000" -Recurse -Force

# 刪除超過 30 天的快照
Get-ChildItem "backups\snapshots" -Directory | Where-Object {
    $_.CreationTime -lt (Get-Date).AddDays(-30)
} | Remove-Item -Recurse -Force
```

---

## 🔒 安全與合規

### 合規性

- ✅ 符合 Google 非營利組織合規要求
- ✅ 備份目的明確（系統恢復）
- ✅ 元數據包含合規信息

### 安全建議

1. **備份加密**
   - 敏感數據應在備份前加密
   - 使用強密碼保護備份文件

2. **訪問控制**
   - 限制備份目錄訪問權限
   - 定期審查快照內容

3. **備份驗證**
   - 定期驗證備份完整性
   - 測試恢復流程

---

## 🛠️ 故障排除

### 快照創建失敗

**問題**: Docker 卷備份失敗

**解決方案**:

```powershell
# 檢查 Docker 服務
docker ps

# 檢查卷列表
docker volume ls

# 手動備份單個卷
docker run --rm -v 卷名:/data -v ${PWD}:/backup alpine tar czf /backup/volume.tar.gz -C /data .
```

### 數據庫備份失敗

**問題**: 數據庫容器未運行

**解決方案**:

```powershell
# 啟動數據庫容器
docker-compose up -d db

# 等待數據庫就緒
Start-Sleep -Seconds 10

# 重新創建快照
```

### 恢復失敗

**問題**: 卷恢復時衝突

**解決方案**:

```powershell
# 停止所有容器
docker-compose down

# 刪除衝突的卷
docker volume rm 卷名

# 重新執行恢復
```

---

## 📝 最佳實踐

### 1. 定期快照

建議在以下情況創建快照：

- 重大更新前
- 配置變更前
- 定期備份（每週/每月）

### 2. 命名規範

使用描述性名稱：

- `before_update_20260118`
- `after_migration_20260118`
- `monthly_backup_202601`

### 3. 快照保留

- 保留最近 10 個快照
- 重要快照長期保留
- 定期清理舊快照

### 4. 測試恢復

定期測試恢復流程：

- 在測試環境恢復
- 驗證數據完整性
- 確認服務正常運行

---

## 📞 相關腳本

- `scripts/create_system_snapshot.ps1` - 創建系統快照
- `scripts/restore_from_snapshot.ps1` - 恢復快照
- `scripts/list_rollback_points.ps1` - 列出回滾點
- `scripts/create_backup_rollback.ps1` - 創建備份回滾點（舊版）
- `scripts/create_rollback_point.py` - Python 回滾點腳本

---

## ✅ 檢查清單

### 創建快照前

- [ ] 確認所有服務運行正常
- [ ] 檢查磁盤空間充足
- [ ] 確認備份目錄可寫入

### 創建快照後

- [ ] 驗證快照文件存在
- [ ] 檢查元數據完整性
- [ ] 確認回滾點已記錄

### 恢復前

- [ ] 預覽恢復操作
- [ ] 備份當前狀態
- [ ] 確認快照可用

### 恢復後

- [ ] 驗證服務啟動
- [ ] 檢查數據完整性
- [ ] 測試關鍵功能

---

**維護者**: 小J (Little J)  
**授權狀態**: ✅ 完整最高權限授權
