# 系統感知永久授權設計

## 📋 概述

系統感知功能被設計為**永久授權的讀取操作**，這意味著：

- ✅ **不需要登入**：即使未登入也可以查詢系統感知
- ✅ **不需要授權請示**：不會觸發授權請示單流程
- ✅ **不需要權限檢查**：所有感知 API 端點都跳過權限檢查
- ✅ **AI 小本體可用**：Little J 可以隨時查詢系統狀態

## 🔑 設計原則

### 1. 永久授權的讀取操作

系統感知功能被明確定義為**永久授權的讀取操作**，這是系統設計的核心原則：

```
感知功能 = 永久授權的讀取操作
```

### 2. 只讀不寫

所有感知功能僅提供**讀取**操作，不執行任何修改：

- ✅ 讀取系統狀態
- ✅ 讀取服務狀態
- ✅ 讀取資源使用情況
- ✅ 讀取帳號權限狀態
- ❌ 不執行任何修改操作
- ❌ 不變更系統配置
- ❌ 不觸發任何動作

### 3. 即時性需求

AI 小本體（Little J）需要即時獲取系統狀態，不應被權限流程阻擋：

- 系統健康監控需要即時性
- AI 決策需要即時狀態資訊
- 權限流程會延遲響應時間

## 🛡️ 安全邊界

### 權限檢查跳過範圍

以下 API 端點**永久授權**，跳過權限檢查：

- `/api/neural/perception` - 系統感知摘要
- `/api/neural/status` - 所有節點狀態
- `/api/neural/node` - 特定節點狀態
- `/api/neural/events` - 最近事件

### 權限檢查保留範圍

以下操作**仍需權限檢查**：

- 推送更新（`push_rules`, `push_kb`）
- 個資存取（`pii_read`, `pii_write`）
- Workspace 寫入（`workspace_write`）
- 命令單建立（`job_create`）
- 所有修改操作

## 📊 實作細節

### API 端點實作

所有感知 API 端點都移除了權限檢查：

```python
# 系統神經網路 API（供 AI 小本體查詢系統感知）
# 注意：感知為讀取權限永久授權，不需要額外權限檢查
if parsed.path == "/api/neural/perception":
    if not NEURAL_NETWORK_AVAILABLE:
        _json(self, HTTPStatus.SERVICE_UNAVAILABLE, ...)
        return
    # 直接執行，不需要權限檢查
    perception = nn.get_system_perception()
    _json(self, HTTPStatus.OK, {"ok": True, "perception": perception})
```

### Little J 意圖處理

在 Little J 的意圖處理中，系統感知查詢被標記為永久授權：

```python
# 依意圖做權限門檻
it0 = str(intent_peek.get("intent") or "unknown")
if it0 == "system_perception":
    # 系統感知為永久授權的讀取操作，直接執行
    required_perm = None
    skip_authz = True
else:
    required_perm = "job_create" if it0 in ("push_rules", "push_kb") else "read"
    skip_authz = False

# 跳過權限檢查
if not skip_authz and required_perm is not None:
    # 執行權限檢查...
```

### 帳號政策例外

即使啟用了帳號政策，系統感知查詢也不需要登入：

```python
# 若已啟用帳號政策：所有功能對接都依賴編號（必須先登入）
# 注意：system_perception 為永久授權的讀取操作，不需要登入
pol = _load_accounts_policy()
accounts_enabled = bool((pol.get("accounts") or []))
if accounts_enabled and not sess and it0_peek != "system_perception":
    _json(self, HTTPStatus.FORBIDDEN, ...)
    return
```

## 🔍 涵蓋的感知範圍

### 基礎系統感知

- 服務狀態（本機中控台、Little J Hub）
- 系統資源（CPU、記憶體、磁碟）
- 網路連通性
- 健康檢查

### admin@wuchang.life 帳號感知

- Windows 10 專業版管理員權限
- Google Workspace 狀態
- Google Drive 同步狀態
- 帳單存取權限

### 任務感知

- 任務收件匣狀態
- 任務執行狀態

## 📝 使用範例

### 透過 Little J 查詢

```
用戶：系統感知
小J：顯示系統健康狀態、關鍵節點狀態等（不需要登入或授權）
```

### 透過 API 查詢（不需要認證）

```bash
# 查詢系統感知摘要
curl http://127.0.0.1:8788/api/neural/perception

# 查詢所有節點狀態
curl http://127.0.0.1:8788/api/neural/status

# 查詢特定節點
curl "http://127.0.0.1:8788/api/neural/node?id=admin_account"
```

### 程式化查詢

```python
from system_neural_network import get_neural_network

# 不需要任何認證或權限檢查
nn = get_neural_network()
nn.start()
perception = nn.get_system_perception()
print(perception)
```

## ⚠️ 注意事項

1. **只讀操作**：感知功能僅讀取狀態，不執行任何修改
2. **不包含敏感資訊**：感知讀數不包含密碼、API 金鑰等敏感資訊
3. **安全邊界**：所有修改操作仍需通過正常權限檢查
4. **即時性優先**：設計優先考慮即時性，而非權限控制

## 🔐 安全考量

雖然感知功能為永久授權，但仍需注意：

1. **敏感資訊過濾**：確保感知讀數不包含敏感資訊
2. **記憶檔案管理**：定期清理歷史記錄
3. **網路安全**：API 端點僅綁定 127.0.0.1，不對外網開放
4. **日誌記錄**：所有感知查詢仍會記錄到稽核日誌

## 📊 權限對照表

| 功能 | 是否需要登入 | 是否需要授權 | 是否需要權限檢查 |
|------|------------|------------|----------------|
| 系統感知查詢 | ❌ | ❌ | ❌ |
| 推送更新 | ✅ | ✅ | ✅ |
| 個資存取 | ✅ | ✅ | ✅ |
| Workspace 寫入 | ✅ | ✅ | ✅ |
| 命令單建立 | ✅ | ✅ | ✅ |

---

**最後更新**: 2026-01-15
