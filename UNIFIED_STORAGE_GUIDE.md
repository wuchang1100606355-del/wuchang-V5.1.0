# 統一儲存指南

## ✅ 問題解決

**原本問題：**
- 本機和伺服器有各自的儲存配置
- 不會自動連動
- 需要維護兩套配置

**解決方案：**
- ✅ **統一使用一套 Google Drive 儲存**
- ✅ **本機和伺服器共用同一個路徑**
- ✅ **自動同步，無需手動複製**

---

## 📁 統一儲存結構

```
J:\共用雲端硬碟\五常雲端空間\
├── containers/              ← 共享容器資料
│   ├── data/
│   │   ├── odoo/          ← Odoo 資料（共享）
│   │   └── other/          ← 其他應用資料（共享）
│   ├── uploads/            ← 上傳檔案（共享）
│   ├── logs/              ← 日誌檔案（共享）
│   └── config/            ← 配置檔案（共享）
│
├── backups/                ← 共享備份
│   ├── database/          ← 資料庫備份（共享）
│   ├── system/            ← 系統備份（共享）
│   └── migration/         ← 遷移備份（共享）
│
└── local_storage/          ← 本地儲存（各主機獨立）
    ├── data/              ← 本地資料
    └── database/
        ├── data/          ← 資料庫資料（各主機獨立，不共享）
        └── backups/       ← 資料庫備份（會同步到共享）
```

---

## 🔄 運作方式

### 自動同步流程

```
本機修改檔案
    ↓
Google Drive 自動同步
    ↓
伺服器自動更新（如果伺服器也安裝 Google Drive）
```

### 資料分類

#### 共享資料（自動同步）
- ✅ **上傳檔案** - 兩邊都可以看到
- ✅ **配置檔案** - 兩邊都使用相同配置
- ✅ **日誌檔案** - 統一管理
- ✅ **備份檔案** - 統一管理

#### 本地資料（各主機獨立）
- ⚠️ **資料庫資料** - 各主機獨立，避免版本衝突
- ⚠️ **臨時檔案** - 各主機獨立

---

## 🖥️ 伺服器設定

### 方案 A：伺服器也安裝 Google Drive（推薦）

1. **在伺服器安裝 Google Drive**
2. **同步到相同路徑**（如果伺服器是 Linux，路徑會不同）
3. **使用相同的 docker-compose.unified.yml**

**Linux 伺服器路徑範例：**
```yaml
# 如果伺服器是 Linux
volumes:
  - /mnt/google-drive/五常雲端空間/containers/data/odoo:/var/lib/odoo
```

### 方案 B：使用網路共享

**讓伺服器通過網路共享訪問本機的 Google Drive：**

1. **在本機啟用網路共享**
   - 共享 `J:\共用雲端硬碟\五常雲端空間`
   - 共享名稱：`wuchang_cloud_storage`

2. **在伺服器映射網路磁碟**
   ```bash
   # Windows 伺服器
   net use Z: \\LUNGSMSI\wuchang_cloud_storage
   
   # Linux 伺服器
   mount -t cifs //LUNGSMSI/wuchang_cloud_storage /mnt/wuchang_storage
   ```

3. **使用網路共享路徑**
   ```yaml
   volumes:
     - Z:/containers/data/odoo:/var/lib/odoo
   ```

---

## 🗑️ 刪除舊配置

### 可以刪除的檔案

1. **舊的儲存配置**
   - `shared_storage_config.json`（已整合到 `unified_storage_config.json`）
   - `docker-compose.gdrive.yml`（已整合到 `docker-compose.unified.yml`）

2. **舊的備份腳本**（可選）
   - `backup_to_gdrive.py`（已整合到統一配置）

### 保留的檔案

- ✅ `docker-compose.safe.yml` - 本地儲存配置（備用）
- ✅ `docker-compose.unified.yml` - **統一配置（使用這個）**

---

## 📋 使用步驟

### 1. 本機設定（已完成）

```bash
# 使用統一配置啟動容器
docker-compose -f docker-compose.unified.yml up -d
```

### 2. 伺服器設定

**選項 A：伺服器也安裝 Google Drive**
```bash
# 在伺服器上執行相同設定
python unified_storage_setup.py

# 使用統一配置啟動容器
docker-compose -f docker-compose.unified.yml up -d
```

**選項 B：使用網路共享**
```bash
# 在伺服器上映射網路磁碟
net use Z: \\LUNGSMSI\wuchang_cloud_storage

# 修改 docker-compose.unified.yml 使用網路共享路徑
# 然後啟動容器
docker-compose -f docker-compose.unified.yml up -d
```

---

## ⚠️ 重要注意事項

### 1. 資料庫安全
- ⚠️ **資料庫必須使用本地儲存**
- ⚠️ **不能直接使用 Google Drive 同步資料夾作為資料庫儲存**
- ✅ **備份會自動同步到 Google Drive**

### 2. 版本衝突
- ✅ **共享資料（上傳檔案、配置）可以自動同步**
- ⚠️ **資料庫資料各主機獨立，避免衝突**

### 3. 同步延遲
- ⚠️ Google Drive 同步有延遲（幾秒到幾分鐘）
- ✅ 對於上傳檔案和配置檔案，延遲通常可接受
- ⚠️ 對於需要即時同步的場景，考慮使用網路共享

---

## 🎯 總結

**統一儲存方案：**
- ✅ 一套配置，兩邊共用
- ✅ 自動同步，無需手動複製
- ✅ 資料一致性
- ✅ 安全設計（資料庫本地儲存）

**下一步：**
1. 在伺服器上設定 Google Drive 或網路共享
2. 使用 `docker-compose.unified.yml` 啟動容器
3. 刪除舊的配置檔案（可選）

---

## 📚 相關檔案

- `docker-compose.unified.yml` - 統一 Docker Compose 配置
- `unified_storage_config.json` - 統一儲存配置
- `unified_storage_setup.py` - 統一儲存設定腳本
- `GOOGLE_DRIVE_STORAGE_WARNING.md` - Google Drive 使用警告
