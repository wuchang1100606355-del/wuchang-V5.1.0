## 目標

把 Google Workspace（Drive 同步）與本系統「營運主體」高度媒合，涵蓋（包含但不限於）：

- **組織（org）**
- **設備（device）**
- **使用者（account_id）**
- **權限（permissions / ui_profile）**
- **管理人（節點 AI / node agent）**
- **系統功能（function catalog / risk / consent）**

設計前提：避免你再做大量設定，因此優先採用「**Google Drive 同步資料夾落地**」方式（不強迫 OAuth / Admin SDK）。

---

## 核心原則（全部依賴編號）

- **唯一主鍵**：所有媒合都以編號為主鍵（`account_id / org_id / device_id / node_id / function_id`），避免用姓名/電話/email 當主鍵。
- **可識別個資隔離**：姓名/電話/email 屬可識別個資，只放在 PII Vault（Drive 私密檔），不進媒合主檔、不寫入一般報表。
- **不可識別資料可分析**：性別/年齡區間/習慣摘要等只放在 non-identifiable vault，且 **同意先行**（未同意就 `consent_required`）。
- **權限可稽核**：帳號編號 → permissions → 可用功能（function_id）必須可追溯。

---

## 建議檔案（都放在 Google Drive 同步資料夾）

- `accounts_policy.json`：帳號編號 → 系統權限（已存在）
- `workspace_matching.json`：Workspace 與系統營運物件的「高度媒合」主檔（新增）
- `pii_contacts.json`：可識別個資（已存在）
- `pii_contacts_non_identifiable.json`：不可識別的「聯繫摘要」（已存在）
- `account_profiles_non_identifiable.json`：不可識別使用習慣（性別/年齡區間/摘要）（已存在）
- `consent_receipts.json`：同意回執（已存在）

你可以用 repo 內的 `workspace_matching.example.json` 先複製成 `workspace_matching.json` 再調整。

---

## `workspace_matching.json`（主檔）包含什麼

（概念）

- **accounts**：把 `account_id` 對上 Workspace principal（可選：email/群組），以及 UI profile 與權限摘要
- **orgs**：`org_id` → Workspace group / Drive folder relpath（讓輸出可自動落地到對應資料夾）
- **devices**：`device_id` → owner_account_id / 管理方式（是否 Workspace managed）
- **node_ai_agents**：`node_id` → agent_id / 管理人 account_id / 可用 function_id
- **system_functions**：把系統功能正式編號化（risk_level / 需同意範圍）

---

## 後續可選（更自動化）

若你未來願意上 API（非必須）：

- Google Admin SDK Directory API：自動同步使用者/群組/OU
- ChromeOS / Endpoint 管理：自動同步設備清單

但這需要 Service Account / Domain-wide delegation，屬「額外設定」，目前先不走。

