# Google Drive 儲存使用警告與最佳實踐

## ⚠️ 重要警告：版本衝突風險

### 問題說明

如果本機和伺服器**同時**使用 Google Drive 同步資料夾作為容器儲存，會遇到以下嚴重問題：

#### 1. **資料庫檔案衝突** 🔴 嚴重
- PostgreSQL 資料庫檔案**不能同時被兩個實例寫入**
- 會造成資料庫損壞、資料遺失
- 可能導致服務完全無法啟動

#### 2. **檔案鎖定問題** 🔴 嚴重
- 多個容器同時寫入同一個檔案會造成衝突
- Google Drive 同步無法處理檔案鎖定
- 可能造成檔案損壞或遺失

#### 3. **同步延遲問題** 🟡 中等
- Google Drive 同步有延遲（幾秒到幾分鐘）
- 可能造成資料不一致
- 容器讀取到過時的資料

#### 4. **版本衝突** 🟡 中等
- 如果兩邊同時修改，Google Drive 會建立衝突副本
- 需要手動解決衝突
- 可能造成資料混亂

---

## ✅ 正確的使用方式

### 方案 1：單一主機運行（推薦）

**只有一台主機運行容器，另一台關閉時不影響**

```
本機 (LUNGSMSI):
  - 運行容器時：使用 J:\我的雲端硬碟\wuchang_containers
  - 關機時：不影響（因為沒有容器在運行）

伺服器:
  - 運行容器時：使用伺服器本地的 Google Drive 路徑
  - 例如：/mnt/google-drive/wuchang_containers (Linux)
  - 或：C:\Users\...\Google Drive\wuchang_containers (Windows)
```

**優點：**
- ✅ 避免版本衝突
- ✅ 資料安全
- ✅ 簡單可靠

**缺點：**
- ❌ 本機關機時，如果容器在本機運行，服務會中斷
- ❌ 需要手動遷移容器

---

### 方案 2：使用 Google Drive 作為備份（推薦）

**容器使用本地儲存，定期備份到 Google Drive**

```
本機容器儲存：
  - 本地路徑：C:\docker\wuchang_containers\...
  - 容器直接使用本地路徑

Google Drive 備份：
  - 備份路徑：J:\我的雲端硬碟\wuchang_containers\backups\...
  - 定期同步（例如：每小時、每天）
  - 只讀共享給其他主機

伺服器容器儲存：
  - 本地路徑：/var/docker/wuchang_containers/...
  - 容器直接使用本地路徑
  - 定期備份到伺服器的 Google Drive
```

**優點：**
- ✅ 完全避免版本衝突
- ✅ 資料安全可靠
- ✅ 可以實現多主機運行
- ✅ 有備份保障

**缺點：**
- ❌ 需要設定備份腳本
- ❌ 備份有延遲

---

### 方案 3：使用網路共享（適合多主機）

**使用 SMB/NFS 網路共享，而不是 Google Drive 同步資料夾**

```
共享儲存：
  - 伺服器提供 SMB 共享：\\SERVER\wuchang_containers
  - 本機映射為：Z:\wuchang_containers
  - 兩邊都可以訪問，但只有一個寫入者

容器配置：
  - 本機容器：使用 Z:\wuchang_containers\...
  - 伺服器容器：使用 \\SERVER\wuchang_containers\...
  - 但**不能同時運行相同容器**
```

**優點：**
- ✅ 即時同步（無延遲）
- ✅ 可以實現多主機共享
- ✅ 適合需要即時共享的場景

**缺點：**
- ❌ 需要網路連接
- ❌ 伺服器必須一直開著
- ❌ 仍然需要避免同時寫入

---

## 🎯 建議的架構

### 推薦架構：混合方案

```
【本機 (LUNGSMSI)】
  - 開發/測試容器：使用本地儲存
  - 備份到：J:\我的雲端硬碟\wuchang_containers\backups
  - 可以隨時關機

【伺服器】
  - 生產容器：使用伺服器本地儲存
  - 備份到：伺服器的 Google Drive
  - 24/7 運行

【共享資料】
  - 上傳檔案：使用 Google Drive 同步（只讀共享）
  - 配置檔案：使用 Google Drive 同步（只讀共享）
  - 資料庫：**絕對不要**使用 Google Drive 同步，使用本地儲存+備份

【容器遷移】
  - 使用備份還原的方式遷移
  - 或使用 Docker 匯出/匯入
```

---

## 📋 實作步驟

### 1. 修改 docker-compose.gdrive.yml

**改為使用本地儲存 + Google Drive 備份：**

```yaml
services:
  wuchang-web:
    volumes:
      # 使用本地儲存（不是 Google Drive）
      - ./local_storage/data/odoo:/var/lib/odoo
      - ./local_storage/uploads:/var/lib/odoo/filestore
      # Google Drive 只作為備份目標（只讀）
      - J:\我的雲端硬碟\wuchang_containers\backups:/backups:ro
      
  db:
    volumes:
      # 資料庫必須使用本地儲存
      - ./local_storage/database/data:/var/lib/postgresql/data
      # 備份到 Google Drive
      - J:\我的雲端硬碟\wuchang_containers\backups:/backups
```

### 2. 建立備份腳本

定期將本地儲存備份到 Google Drive

### 3. 容器遷移流程

1. 停止本機容器
2. 備份資料到 Google Drive
3. 在伺服器還原備份
4. 啟動伺服器容器

---

## ⚠️ 絕對不要做的事

1. ❌ **不要**讓兩個 PostgreSQL 容器同時寫入同一個 Google Drive 資料夾
2. ❌ **不要**讓多個容器同時寫入同一個檔案
3. ❌ **不要**直接使用 Google Drive 同步資料夾作為資料庫儲存
4. ❌ **不要**在容器運行時關閉 Google Drive 同步

---

## 📝 總結

**Google Drive 適合：**
- ✅ 備份儲存
- ✅ 只讀共享（配置檔案、上傳檔案）
- ✅ 容器遷移的中間儲存

**Google Drive 不適合：**
- ❌ 直接作為資料庫儲存
- ❌ 多主機同時寫入
- ❌ 需要即時同步的場景

**建議：**
使用**本地儲存 + Google Drive 備份**的混合方案，既安全又靈活。
