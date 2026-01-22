# 遷移到 J 磁碟指南

## 概述

`migrate_to_j_drive.py` 用於將本機非系統檔案從 C 磁碟遷移到 J 磁碟，並在 C 磁碟留下符號連結。

**目的：**
- 節省 C 磁碟空間
- 保持路徑兼容性（透過符號連結）
- 將資料檔案存儲在 J 磁碟

## 遷移策略

### 需要遷移的目錄
- `local_storage/` - 本地儲存
- `data/` - 資料檔案
- `uploads/` - 上傳檔案
- `backups/` - 備份檔案
- `logs/` - 日誌檔案
- `cache/` - 快取檔案
- `temp/` - 臨時檔案

### 需要遷移的檔案類型
- `*.json` - JSON 資料檔案
- `*.log` - 日誌檔案
- `*.db` - 資料庫檔案
- `*.sqlite` - SQLite 資料庫
- `*.sqlite3` - SQLite3 資料庫

### 不遷移的檔案（系統檔案）
- `*.py` - Python 源碼
- `*.md` - Markdown 文檔
- `*.yml`, `*.yaml` - 配置文件
- `*.txt` - 文字檔案
- `*.html`, `*.css`, `*.js` - 網頁檔案
- `.git/` - Git 目錄
- `__pycache__/` - Python 快取

## 使用方式

### 模擬模式（推薦先執行）

```bash
# 模擬遷移，不實際執行
python migrate_to_j_drive.py --dry-run
```

### 實際遷移

```bash
# 執行實際遷移（需要明確指定 --execute）
python migrate_to_j_drive.py --execute
```

### 自訂路徑

```bash
# 指定源目錄和目標目錄
python migrate_to_j_drive.py \
  --execute \
  --source "C:\wuchang V5.1.0\wuchang-V5.1.0" \
  --target "J:\wuchang V5.1.0\wuchang-V5.1.0"
```

### 僅遷移不創建連結

```bash
# 遷移但不創建符號連結
python migrate_to_j_drive.py --execute --no-link
```

## 遷移過程

1. **掃描**：識別需要遷移的檔案和目錄
2. **遷移**：複製檔案/目錄到 J 磁碟
3. **刪除源檔案**：刪除 C 磁碟的原始檔案
4. **創建連結**：在 C 磁碟創建符號連結指向 J 磁碟

## 注意事項

1. ⚠️ **需要管理員權限**：創建符號連結需要管理員權限
2. ⚠️ **備份重要**：遷移前建議先備份
3. ⚠️ **J 磁碟空間**：確保 J 磁碟有足夠空間
4. ⚠️ **符號連結**：如果無法創建符號連結，檔案仍會遷移，但 C 磁碟不會有連結
5. ⚠️ **路徑兼容**：符號連結可以保持路徑兼容性，但某些應用程式可能不支援符號連結

## 故障排除

### 問題：無法創建符號連結

**錯誤訊息：** `ERROR_PRIVILEGE_NOT_HELD`

**解決方案：**
1. 以管理員身份運行 PowerShell
2. 執行：`Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux`
3. 或使用管理員權限運行遷移腳本

### 問題：遷移後應用程式無法找到檔案

**解決方案：**
1. 檢查符號連結是否正確創建
2. 某些應用程式可能需要重新啟動
3. 檢查路徑是否正確

## 相關文檔

- `CLOUD_SYNC_CONFIG.md` - 雲端同步配置說明
- `SYNC_STRATEGY.md` - 同步策略說明
