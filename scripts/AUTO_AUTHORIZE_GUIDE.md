# 自動權限授權與執行指南

## 概述

`auto_authorize_and_execute.py` 是一個自動化腳本，可以：
- 自動檢查當前權限狀態
- 自動請求必要權限（full_agent）
- 自動執行授權後的操作

## 快速開始

### 步驟 1：建立配置檔案

複製範例配置檔案並填入您的資訊：

```bash
# 複製範例檔案
Copy-Item auto_auth_config.example.json auto_auth_config.json

# 編輯配置檔案，填入：
# - account_id: 您的帳號 ID
# - pin: 您的 PIN 碼
# - auto_approve: 是否自動核准（需要管理員權限）
```

### 步驟 2：執行自動授權

```bash
python auto_authorize_and_execute.py
```

## 配置檔案說明

### auto_auth_config.json

```json
{
  "account_id": "your_account_id",
  "pin": "your_pin",
  "auto_approve": false,
  "default_permission": "full_agent",
  "default_ttl_hours": 24
}
```

**欄位說明：**
- `account_id`: 您的帳號 ID（必填）
- `pin`: 您的 PIN 碼（必填）
- `auto_approve`: 是否自動核准授權請求（需要管理員權限）
- `default_permission`: 預設請求的權限類型（預設：full_agent）
- `default_ttl_hours`: 預設授權有效期（小時，預設：24）

## 執行流程

1. **檢查控制中心**
   - 確認控制中心是否運行
   - 如果未運行，提示啟動

2. **載入配置**
   - 讀取 `auto_auth_config.json`
   - 如果不存在，提示手動輸入

3. **登入帳號**
   - 使用配置檔案中的帳號 ID 和 PIN 登入

4. **檢查當前權限**
   - 檢查是否已有 full_agent 或 admin_all 權限
   - 如果已有權限，直接執行操作

5. **請求權限**（如果需要）
   - 自動提交權限請求
   - 如果配置允許且帳號有管理員權限，自動核准
   - 否則等待管理員手動核准

6. **執行操作**
   - 在獲得權限後執行預設操作
   - 例如：檢查系統狀態、同步檔案等

## 安全注意事項

1. **配置檔案安全**
   - `auto_auth_config.json` 包含敏感資訊（PIN）
   - 請勿提交到版本控制系統
   - 建議加入 `.gitignore`

2. **自動核准**
   - `auto_approve` 功能需要管理員權限
   - 僅在信任的環境中使用
   - 建議設為 `false` 以增加安全性

3. **權限有效期**
   - 預設為 24 小時
   - 可以根據需要調整
   - 建議不要設定過長的有效期

## 使用範例

### 基本使用

```bash
# 1. 建立配置檔案
Copy-Item auto_auth_config.example.json auto_auth_config.json
# 編輯 auto_auth_config.json，填入帳號資訊

# 2. 執行自動授權
python auto_authorize_and_execute.py
```

### 手動輸入模式

如果沒有配置檔案，腳本會提示手動輸入：
- 帳號 ID
- PIN 碼

### 自動核准模式

如果您的帳號有管理員權限，可以設定 `auto_approve: true`：
- 授權請求會自動核准
- 無需等待管理員手動核准

## 擴展功能

腳本可以擴展以執行更多操作：

```python
# 在 execute_with_permission 函數中添加新操作
def execute_with_permission(session, operation, **kwargs):
    if operation == "your_operation":
        # 執行您的操作
        pass
```

## 疑難排解

### 問題：找不到配置檔案

**解決方案**：
1. 複製 `auto_auth_config.example.json` 為 `auto_auth_config.json`
2. 填入實際的帳號資訊

### 問題：登入失敗

**解決方案**：
1. 檢查帳號 ID 和 PIN 是否正確
2. 確認控制中心正在運行
3. 檢查網路連接

### 問題：權限請求失敗

**解決方案**：
1. 檢查帳號是否已填寫設計責任和使用責任的自然人
2. 確認帳號有權限提出授權請求
3. 檢查授權請求的格式是否正確

### 問題：自動核准失敗

**解決方案**：
1. 確認帳號有管理員權限（auth_manage 或 admin_all）
2. 檢查授權請求 ID 是否正確
3. 確認授權請求尚未被核准或拒絕

## 相關文件

- `AUTHORIZATION_GUIDE.md` - 完整授權指南
- `request_full_agent.py` - 手動授權腳本
