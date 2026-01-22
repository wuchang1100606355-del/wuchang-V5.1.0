# 加密儲存系統設定指南

## 📋 概述

本系統提供加密處理記錄、支援地端外接儲存裝置、設備辨識、變動記錄（硬編碼）功能，並啟用個資處理功能。

## 🔧 設定步驟

### 1. 安裝依賴套件

```bash
pip install cryptography
```

### 2. 設定環境變數

```powershell
# 啟用個資處理功能
setx WUCHANG_PII_ENABLED "true"

# 設定預設個資儲存裝置（設備 ID）
setx WUCHANG_PII_STORAGE_DEVICE "USB001"
```

### 3. 註冊外接儲存裝置

```python
from encrypted_storage_manager import get_storage_manager

storage = get_storage_manager()

# 偵測外接裝置
devices = storage.detect_external_devices()
print(devices)

# 註冊裝置
device = storage.register_device(
    device_id="USB001",
    device_name="USB 隨身碟 1",
    device_type="usb",
    mount_path="E:\\",  # Windows
    # mount_path="/media/usb1",  # Linux
    serial_number="SN123456",  # 可選
    capacity_bytes=16000000000,  # 可選
    actor="admin@wuchang.life",
    notes="主要個資儲存裝置",
)

# 產生加密金鑰
storage.generate_encryption_key("USB001")
```

### 4. 授予個資使用授權

```python
from authorized_administrators import grant_authorization

# 授予可究責自然人個資使用授權
auth = grant_authorization(
    person_name="張三",
    person_type="system_designer",
    authorization_scope="系統開發與維護",
    authorized_uses=["hardcode_record", "system_audit"],
    granted_by="admin@wuchang.life",
)
```

### 5. 使用個資儲存功能

```python
from pii_storage_manager import get_pii_storage_manager

pii_manager = get_pii_storage_manager()

# 儲存個資（加密）
pii_manager.save_pii(
    person_name="張三",
    pii_data={
        "name": "張三",
        "role": "系統開發者",
        "contact": "zhang@example.com",
    },
    actor="admin@wuchang.life",
)

# 載入個資（解密）
pii_data = pii_manager.load_pii(
    person_name="張三",
    actor="admin@wuchang.life",
)
```

## 📊 設備辨識

### 自動偵測

系統會自動偵測外接儲存裝置：

- **Windows**：使用 `wmic` 查詢邏輯磁碟機
- **Linux**：使用 `lsblk` 查詢區塊裝置

### 設備註冊表

設備資訊儲存在 `device_registry.json`（硬編碼）：

```json
{
  "USB001": {
    "device_id": "USB001",
    "device_name": "USB 隨身碟 1",
    "device_type": "usb",
    "mount_path": "E:\\",
    "serial_number": "SN123456",
    "capacity_bytes": 16000000000,
    "registered_at": "2026-01-15T12:00:00+0800",
    "last_seen_at": "2026-01-15T12:00:00+0800",
    "is_active": true,
    "encryption_key_hash": "...",
    "notes": "主要個資儲存裝置"
  }
}
```

## 🔐 加密機制

### 金鑰產生

- 使用 PBKDF2 從設備識別碼和系統資訊產生金鑰
- 金鑰雜湊值記錄在設備註冊表中
- 實際金鑰僅存在記憶體中

### 加密儲存

- 使用 Fernet 對稱加密
- 資料以 JSON 格式加密後儲存
- 檔案副檔名為 `.encrypted`

## 📝 變動記錄（硬編碼）

所有變動記錄在 `storage_change_log.jsonl`（硬編碼）：

```json
{
  "timestamp": "2026-01-15T12:00:00+0800",
  "change_type": "data_encrypted",
  "device_id": "USB001",
  "actor": "system",
  "details": {
    "data_size": 1024,
    "encrypted_size": 1280
  },
  "hash": "sha256_hash_value"
}
```

### 變動類型

- `device_added`：裝置新增
- `device_removed`：裝置移除
- `data_encrypted`：資料加密
- `data_decrypted`：資料解密
- `data_saved_to_device`：資料儲存到裝置
- `data_loaded_from_device`：從裝置載入資料
- `key_rotated`：金鑰輪換

## 🔒 安全性

### 檔案保護

- `device_registry.json`：設備註冊表（硬編碼）
- `storage_change_log.jsonl`：變動記錄（硬編碼）
- `accountable_person_authorizations.json`：授權記錄（硬編碼）
- `.encrypted` 檔案：加密個資檔案（外接裝置）

**建議**：
- 將這些檔案加入 `.gitignore`
- 實施嚴格的檔案存取權限控制
- 定期備份加密檔案

### 存取控制

- 個資使用需獲得明確授權
- 授權檢查在每次存取時執行
- 所有操作記錄在變動記錄中

## ⚠️ 注意事項

1. **啟用個資處理**：需設定 `WUCHANG_PII_ENABLED=true`
2. **設備註冊**：使用前需先註冊外接儲存裝置
3. **授權要求**：個資使用需獲得明確授權
4. **加密金鑰**：金鑰僅存在記憶體中，重啟後需重新產生
5. **外接裝置**：確保外接裝置已正確掛載

## 🔗 相關文件

- `encrypted_storage_manager.py`：加密儲存管理器
- `pii_storage_manager.py`：個資儲存管理器
- `authorized_administrators.py`：授權管理
- `ACCOUNTABLE_PERSON_AUTHORIZATION.md`：授權機制說明
- `COMPLIANCE_NO_PII.md`：合規聲明

---

**最後更新**：2026-01-15
