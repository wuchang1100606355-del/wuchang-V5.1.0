# admin@wuchang.life 帳號權限感知模組

## 📋 概述

本模組提供對 `admin@wuchang.life` 帳號權限狀態的感知能力，涵蓋：

- Windows 10 專業版系統帳號權限
- Google Workspace 雲端硬碟同步狀態
- Google 非營利帳號狀態
- 帳單存取權限

## 🔑 帳號身份

**admin@wuchang.life** 被定義為：
- **超級管理員**：系統最高權限者
- **所有權人**：擁有所有資源的所有權
- **永久授權**：系統感知為永久授權的讀取操作

## 🖥️ Windows 10 專業版感知

### 檢查項目

1. **管理員權限**：檢查當前是否以管理員身份執行
2. **用戶資訊**：獲取當前 Windows 用戶名和網域
3. **系統資訊**：Windows 版本和平台資訊

### 使用方式

```python
from admin_account_sensor import check_windows_admin

status = check_windows_admin()
print(status)
```

輸出範例：
```json
{
  "is_windows": true,
  "is_admin": true,
  "username": "admin",
  "userdomain": "WUCHANG",
  "full_username": "WUCHANG\\admin",
  "platform": "Windows-10-10.0.26220-SP0",
  "system": "Windows",
  "release": "10"
}
```

## ☁️ Google Workspace 感知

### 檢查項目

1. **環境變數配置**：
   - `WUCHANG_SYSTEM_DB_DIR`：系統資料庫目錄
   - `WUCHANG_WORKSPACE_OUTDIR`：Workspace 輸出目錄
   - `WUCHANG_PII_OUTDIR`：個資保管目錄
   - `WUCHANG_WORKSPACE_EXCHANGE_DIR`：交換目錄

2. **Google Drive 同步狀態**：
   - 檢查 Google Drive 進程是否運行
   - 驗證同步資料夾是否存在

3. **配置檔案**：
   - `accounts_policy.json`：帳號政策
   - `workspace_matching.json`：Workspace 媒合設定

### 使用方式

```python
from admin_account_sensor import check_google_drive_sync, check_google_workspace_account

# 檢查 Google Drive 同步
drive_status = check_google_drive_sync()
print(drive_status)

# 檢查 Google Workspace 帳號
workspace_status = check_google_workspace_account()
print(workspace_status)
```

## 💰 帳單存取權限

### 檢查項目

1. **預期權限**：admin@wuchang.life 作為所有權人應有的權限
2. **帳單目錄**：檢查是否有帳單相關目錄

### 預期權限

作為所有權人，admin@wuchang.life 應擁有：

- ✅ Google Workspace Admin Console 完整存取
- ✅ Google Cloud Console 帳單查看
- ✅ Google for Nonprofits 帳號管理
- ✅ 所有資源的所有權人權限

## 🔗 整合到系統神經網路

感知模組已自動整合到系統神經網路，包含以下節點：

1. **admin_account**：管理員帳號權限感知
2. **google_workspace**：Google Workspace 狀態感知
3. **google_drive_sync**：Google Drive 同步狀態感知
4. **billing_access**：帳單存取權限感知

### 查詢方式

```python
from system_neural_network import get_neural_network

nn = get_neural_network()
nn.start()

# 查詢管理員帳號狀態
admin_status = nn.get_node_status("admin_account")
print(admin_status)

# 查詢 Google Workspace 狀態
workspace_status = nn.get_node_status("google_workspace")
print(workspace_status)
```

### 透過 API 查詢

```bash
# 查詢特定節點
curl "http://127.0.0.1:8788/api/neural/node?id=admin_account"

# 查詢系統感知摘要（包含所有關鍵節點）
curl "http://127.0.0.1:8788/api/neural/perception"
```

## 🔐 永久授權設計

系統感知功能（包括 admin 帳號感知）被設計為**永久授權的讀取操作**：

- ✅ **不需要登入**：即使未登入也可以查詢
- ✅ **不需要授權請示**：不會觸發授權請示單
- ✅ **不需要權限檢查**：所有感知 API 都跳過權限檢查
- ✅ **AI 小本體可用**：Little J 可以隨時查詢

### 設計理由

1. **基礎設施監控**：感知功能用於監控系統基礎設施狀態
2. **只讀操作**：僅讀取狀態，不執行任何修改
3. **即時性需求**：AI 需要即時獲取狀態，不應被權限流程阻擋
4. **安全邊界**：所有修改操作仍需通過正常權限檢查

## 📊 感知節點配置

預設感知節點配置：

```json
{
  "nodes": [
    {
      "node_id": "admin_account",
      "name": "admin@wuchang.life 帳號權限",
      "sensor_type": "admin_account",
      "check_interval": 30.0,
      "enabled": true,
      "metadata": {
        "admin_email": "admin@wuchang.life"
      }
    },
    {
      "node_id": "google_workspace",
      "name": "Google Workspace 狀態",
      "sensor_type": "google_workspace",
      "check_interval": 60.0,
      "enabled": true,
      "metadata": {
        "admin_email": "admin@wuchang.life"
      }
    },
    {
      "node_id": "google_drive_sync",
      "name": "Google Drive 同步狀態",
      "sensor_type": "google_drive",
      "check_interval": 30.0,
      "enabled": true
    },
    {
      "node_id": "billing_access",
      "name": "帳單存取權限",
      "sensor_type": "billing",
      "check_interval": 300.0,
      "enabled": true,
      "metadata": {
        "admin_email": "admin@wuchang.life"
      }
    }
  ]
}
```

## 🔍 故障排除

### Google Drive 同步未運行

**檢查項目：**
1. 確認 Google Drive for Desktop 已安裝
2. 檢查進程是否運行：`tasklist | findstr GoogleDrive`
3. 確認同步資料夾路徑正確

**解決方法：**
```powershell
# 檢查 Google Drive 進程
tasklist | findstr GoogleDrive

# 檢查環境變數
echo %WUCHANG_SYSTEM_DB_DIR%
echo %WUCHANG_WORKSPACE_OUTDIR%
```

### Windows 管理員權限檢查失敗

**檢查項目：**
1. 確認以管理員身份執行
2. 檢查用戶名是否正確

**解決方法：**
- 以系統管理員身份執行 PowerShell
- 確認當前用戶具有管理員權限

## 📝 注意事項

1. **敏感資訊**：感知模組不會讀取或儲存任何敏感資訊（如密碼、API 金鑰）
2. **只讀操作**：所有感知功能僅讀取狀態，不執行任何修改
3. **永久授權**：感知功能為永久授權，不需要額外權限檢查
4. **即時性**：感知節點會定期檢查狀態，確保即時性

---

**最後更新**: 2026-01-15
