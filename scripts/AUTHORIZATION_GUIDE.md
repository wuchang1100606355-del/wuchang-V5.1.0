# 本地小J最高權限授權指南

## 控制中心地址
**http://127.0.0.1:8788/**

## 授權步驟

### 方式一：通過 Web UI（推薦）

1. **開啟瀏覽器訪問控制中心**
   ```
   http://127.0.0.1:8788/
   ```

2. **登入帳號**
   - 如果尚未登入，請先登入
   - 使用 `/api/auth/login` 端點登入

3. **請求最高權限**
   - 在 UI 中選擇「授權請求」功能
   - 或直接使用授權 API

### 方式二：通過 API 直接授權

#### 步驟 1：登入（如果尚未登入）

```powershell
# PowerShell
$body = @{
    account_id = "your_account_id"
    pin = "your_pin"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8788/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

#### 步驟 2：請求最高權限（full_agent）

```powershell
# PowerShell
$body = @{
    permissions = @("full_agent")
    ttl_seconds = 86400  # 24小時（full_agent 可設為較長時間）
    scope = @{
        domain = "wuchang.life"
    }
    reason = "系統管理需要"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8788/api/authz/request" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -SessionVariable session
```

**注意**：`full_agent` 權限需要帳號中已填寫：
- `design_responsibility.natural_person`（設計責任自然人）
- `usage_responsibility.natural_person`（使用責任自然人）

#### 步驟 3：核准授權請求（需要管理員權限）

```powershell
# PowerShell
$body = @{
    id = "request_id_from_step2"
    ttl_seconds = 86400
    scope = @{
        domain = "wuchang.life"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8788/api/authz/requests/approve" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -WebSession $session
```

### 方式三：使用 Python 腳本

```python
import requests

# 登入
session = requests.Session()
login_response = session.post(
    "http://127.0.0.1:8788/api/auth/login",
    json={"account_id": "your_account_id", "pin": "your_pin"}
)

# 請求最高權限
authz_response = session.post(
    "http://127.0.0.1:8788/api/authz/request",
    json={
        "permissions": ["full_agent"],
        "ttl_seconds": 86400,
        "scope": {"domain": "wuchang.life"},
        "reason": "系統管理需要"
    }
)

print(authz_response.json())
```

## 權限類型說明

### 最高權限
- **`full_agent`**：完整代理權限，完全開放（不受時間/項目/範圍限制）
  - 需要填寫設計責任和使用責任的自然人
  - 最強大的權限

- **`admin_all`**：管理員全部權限
  - 可以執行所有管理操作

### 其他常用權限
- `read`：讀取權限（預設）
- `workspace_write`：工作空間寫入
- `high_risk_execute_local`：高風險操作執行
- `auth_manage`：授權管理
- `job_manage`：任務管理

## 檢查授權狀態

```powershell
# 檢查當前授權
Invoke-RestMethod -Uri "http://127.0.0.1:8788/api/authz/grants/list" `
  -WebSession $session
```

## 重要提示

1. **首次使用 full_agent**：需要先在帳號設定中填寫設計責任和使用責任的自然人
2. **授權有效期**：可以設定 `ttl_seconds`（秒數），建議設為 86400（24小時）或更長
3. **範圍限制**：`full_agent` 不受範圍限制，其他權限可以設定 `scope`
4. **授權審核**：授權請求需要管理員核准（除非您已經是管理員）

## 快速授權腳本

已建立 `request_full_agent.py` 腳本，可直接執行：

```bash
python request_full_agent.py
```
