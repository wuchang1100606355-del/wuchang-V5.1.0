# 同帳號登入配置指南

## ✅ 優勢

如果本機和伺服器使用**同一個 Google 帳號**登入 Google Drive：

### 自動同步優勢
- ✅ **完全自動同步** - 兩邊的 Google Drive 會自動同步相同內容
- ✅ **路徑一致** - 如果都是 Windows，路徑會完全相同
- ✅ **無需額外設定** - Google Drive 自動處理同步
- ✅ **即時更新** - 一邊修改，另一邊自動更新

---

## 📁 路徑配置

### Windows 本機（LUNGSMSI）
```
J:\共用雲端硬碟\五常雲端空間
```

### Windows 伺服器（HOME-COMMPUT）
如果伺服器也是 Windows，路徑應該是：
```
J:\共用雲端硬碟\五常雲端空間
```
或
```
C:\Users\<使用者名稱>\Google Drive\五常雲端空間
```

### Linux 伺服器
如果伺服器是 Linux，路徑會是：
```
/home/<使用者名稱>/Google Drive/五常雲端空間
```
或
```
/mnt/google-drive/五常雲端空間
```

---

## 🔧 配置調整

### 方案 A：兩邊都是 Windows（最簡單）

**如果伺服器也是 Windows，路徑相同：**

```yaml
# docker-compose.unified.yml
volumes:
  # 本機和伺服器路徑相同
  - J:/共用雲端硬碟/五常雲端空間/containers/data/odoo:/var/lib/odoo
```

**優點：**
- ✅ 配置完全相同
- ✅ 不需要修改任何路徑
- ✅ 直接使用 `docker-compose.unified.yml`

---

### 方案 B：伺服器是 Linux

**需要建立環境變數或配置檔案：**

```yaml
# docker-compose.unified.yml
volumes:
  # 使用環境變數
  - ${GDRIVE_PATH}/containers/data/odoo:/var/lib/odoo
```

**在伺服器上設定環境變數：**
```bash
# Linux 伺服器
export GDRIVE_PATH="/home/user/Google Drive/五常雲端空間"

# 或建立 .env 檔案
echo "GDRIVE_PATH=/home/user/Google Drive/五常雲端空間" > .env
```

---

## 🔍 檢查伺服器路徑

### 在伺服器上檢查 Google Drive 路徑

**Windows 伺服器：**
```powershell
# 檢查 Google Drive 路徑
Get-ChildItem "J:\共用雲端硬碟" -ErrorAction SilentlyContinue
Get-ChildItem "$env:USERPROFILE\Google Drive" -ErrorAction SilentlyContinue
```

**Linux 伺服器：**
```bash
# 檢查 Google Drive 路徑
ls ~/Google\ Drive/
ls /mnt/google-drive/
```

---

## 📋 統一配置步驟

### 1. 確認兩邊的 Google Drive 路徑

**本機：**
```powershell
Test-Path "J:\共用雲端硬碟\五常雲端空間"
```

**伺服器：**
```powershell
# Windows 伺服器
Test-Path "J:\共用雲端硬碟\五常雲端空間"

# 或
Test-Path "$env:USERPROFILE\Google Drive\五常雲端空間"
```

### 2. 建立統一配置

如果路徑相同，直接使用 `docker-compose.unified.yml`

如果路徑不同，建立環境變數配置：

**本機 `.env`：**
```
GDRIVE_PATH=J:/共用雲端硬碟/五常雲端空間
```

**伺服器 `.env`：**
```
GDRIVE_PATH=/home/user/Google Drive/五常雲端空間
```

### 3. 修改 docker-compose.unified.yml 使用環境變數

```yaml
volumes:
  - ${GDRIVE_PATH}/containers/data/odoo:/var/lib/odoo
  - ${GDRIVE_PATH}/containers/uploads:/var/lib/odoo/filestore
```

---

## 🎯 同帳號登入的優勢

### 1. 自動同步
- ✅ 本機上傳檔案 → 自動同步到 Google Drive → 伺服器自動下載
- ✅ 伺服器上傳檔案 → 自動同步到 Google Drive → 本機自動下載
- ✅ 無需手動操作

### 2. 資料一致性
- ✅ 兩邊看到的檔案完全相同
- ✅ 配置檔案自動同步
- ✅ 上傳檔案自動同步

### 3. 備份安全
- ✅ 資料自動備份到 Google Drive
- ✅ 即使一台機器故障，資料還在 Google Drive
- ✅ 可以隨時恢復

---

## ⚠️ 注意事項

### 1. 同步延遲
- ⚠️ Google Drive 同步有延遲（幾秒到幾分鐘）
- ✅ 對於上傳檔案和配置，延遲通常可接受
- ⚠️ 對於需要即時同步的場景，考慮使用網路共享

### 2. 資料庫安全
- ⚠️ **資料庫必須使用本地儲存**
- ⚠️ **不能直接使用 Google Drive 同步資料夾作為資料庫儲存**
- ✅ **備份會自動同步到 Google Drive**

### 3. 版本衝突
- ✅ **共享資料（上傳檔案、配置）可以自動同步**
- ⚠️ **資料庫資料各主機獨立，避免衝突**

---

## 🔧 自動偵測腳本

建立腳本自動偵測 Google Drive 路徑：

```python
# detect_gdrive_path.py
import platform
from pathlib import Path

def detect_gdrive_path():
    """自動偵測 Google Drive 路徑"""
    system = platform.system()
    
    if system == "Windows":
        possible_paths = [
            Path("J:/共用雲端硬碟/五常雲端空間"),
            Path.home() / "Google Drive" / "五常雲端空間",
            Path.home() / "Google 雲端硬碟" / "五常雲端空間",
        ]
    else:  # Linux/Mac
        possible_paths = [
            Path.home() / "Google Drive" / "五常雲端空間",
            Path("/mnt/google-drive/五常雲端空間"),
        ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None
```

---

## 📝 總結

**同帳號登入的優勢：**
- ✅ 完全自動同步
- ✅ 資料一致性
- ✅ 備份安全
- ✅ 無需手動操作

**配置要點：**
1. 確認兩邊的 Google Drive 路徑
2. 如果路徑相同，直接使用統一配置
3. 如果路徑不同，使用環境變數
4. 資料庫使用本地儲存，避免衝突

**下一步：**
1. 在伺服器上確認 Google Drive 路徑
2. 根據路徑調整配置（如果需要）
3. 使用 `docker-compose.unified.yml` 啟動容器
