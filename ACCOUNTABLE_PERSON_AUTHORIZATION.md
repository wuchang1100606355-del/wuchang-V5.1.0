# 可究責自然人個資使用授權機制

## 📋 概述

本機制用於管理可究責自然人的個資使用授權，確保系統在使用可究責自然人個資時獲得明確授權。

## 🔑 合規聲明

根據系統合規聲明：

1. **本系統及AI程序設計之可究責自然人不在隱私權保護規範內**
2. **本系統經授權之獨立管理權限自然人不在隱私權保護規範內**
3. **此兩種自然人除姓名外其餘不得公開揭露，但須紀錄於本系統之硬編碼**
4. **個資使用需獲得明確授權**

## 📊 授權範圍

### 可授權的用途

- **hardcode_record**：記錄於系統硬編碼
- **system_audit**：系統稽核記錄
- **compliance_report**：合規報告
- **system_management**：系統管理
- **responsibility_tracking**：責任追蹤
- **\***：所有用途（需謹慎使用）

### 授權類型

1. **永久授權**：`expires_at` 為 `None`，授權永久有效
2. **定期授權**：設定 `expires_at`，授權在指定時間到期
3. **可撤銷授權**：可隨時撤銷授權

## 🔧 使用方式

### 程式化使用

```python
from authorized_administrators import (
    grant_authorization,
    revoke_authorization,
    get_authorization,
    check_authorization,
    get_authorization_summary,
)

# 授予授權
auth = grant_authorization(
    person_name="張三",
    person_type="system_designer",  # 或 "authorized_administrator"
    authorization_scope="系統開發與維護",
    authorized_uses=["hardcode_record", "system_audit"],
    expires_at=None,  # 永久有效
    granted_by="admin@wuchang.life",
    notes="系統主要開發者",
)

# 檢查授權
if check_authorization("張三", "hardcode_record"):
    # 可以記錄於硬編碼
    pass

# 獲取授權摘要（僅可公開資訊）
summary = get_authorization_summary("張三")
print(summary)
# {
#     "person_name": "張三",
#     "authorized": True,
#     "status": "active",
#     "granted_at": "2026-01-15T12:00:00+0800",
#     "expires_at": None,
# }

# 撤銷授權
revoke_authorization("張三")
```

### API 使用

#### 授予授權

```bash
curl -X POST http://127.0.0.1:8800/api/accountable/authorization/grant \
  -H "Content-Type: application/json" \
  -d '{
    "person_name": "張三",
    "person_type": "system_designer",
    "authorization_scope": "系統開發與維護",
    "authorized_uses": ["hardcode_record", "system_audit"],
    "granted_by": "admin@wuchang.life"
  }'
```

#### 查詢授權

```bash
curl "http://127.0.0.1:8800/api/accountable/authorization?person_name=張三"
```

#### 檢查授權

```bash
curl -X POST http://127.0.0.1:8800/api/accountable/authorization/check \
  -H "Content-Type: application/json" \
  -d '{
    "person_name": "張三",
    "use_case": "hardcode_record"
  }'
```

#### 撤銷授權

```bash
curl -X POST http://127.0.0.1:8800/api/accountable/authorization/revoke \
  -H "Content-Type: application/json" \
  -d '{
    "person_name": "張三"
  }'
```

## 📝 授權記錄格式

授權記錄儲存在 `accountable_person_authorizations.json`：

```json
{
  "張三": {
    "person_name": "張三",
    "person_type": "system_designer",
    "authorization_scope": "系統開發與維護",
    "authorized_uses": ["hardcode_record", "system_audit"],
    "granted_at": "2026-01-15T12:00:00+0800",
    "expires_at": null,
    "revoked_at": null,
    "granted_by": "admin@wuchang.life",
    "notes": "系統主要開發者"
  }
}
```

## 🔐 安全性

### 存取控制

- 授權記錄檔案（`accountable_person_authorizations.json`）應限制存取權限
- 建議不在公開版本控制系統中提交此檔案
- API 端點應實施適當的認證機制

### 資訊保護

- 除姓名外，所有授權資訊不得公開揭露
- 授權記錄僅用於系統內部管理
- 公開查詢僅返回姓名和授權狀態

## 📊 授權驗證

### 驗證授權記錄

```python
from authorized_administrators import validate_authorizations

validation = validate_authorizations()
print(validation)
# {
#     "total_count": 5,
#     "valid_count": 4,
#     "expired_count": 0,
#     "revoked_count": 1,
#     "valid": True,
# }
```

### 檢查授權有效性

```python
from authorized_administrators import get_authorization

auth = get_authorization("張三")
if auth and auth.is_valid():
    # 授權有效
    pass
```

## ⚠️ 注意事項

1. **授權記錄為硬編碼**：授權記錄儲存在系統檔案中，需確保安全性
2. **除姓名外不得公開**：所有授權資訊除姓名外不得公開揭露
3. **定期審查**：建議定期審查授權記錄，撤銷不再需要的授權
4. **授權範圍明確**：授權範圍和用途應明確記錄，避免濫用

## 🔗 相關文件

- `authorized_administrators.py`：可究責自然人硬編碼記錄
- `accountable_person_authorization_api.py`：授權管理 API
- `COMPLIANCE_NO_PII.md`：合規聲明
- `AGENT_CONSTITUTION.md`：系統憲法

---

**最後更新**：2026-01-15
