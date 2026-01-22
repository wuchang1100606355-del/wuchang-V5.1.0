# 小J Hub（伺服器控制 AI / 資料彙集區）

你更正後的方向：**不要再用「推送交流區」當核心**，改成：

- **小J 程式本身就是資料彙集區（Hub）**
- 小J 在伺服器端作為控制 AI（收件、確認、再由執行器跑）

---

## 組成

- `little_j_hub_server.py`：伺服器端 Hub（HTTP）
  - `inbox/`：收件匣（機器可讀 JSON jobs）
  - `archive/`：封存
  - `hub_audit.jsonl`：稽核
- `little_j_hub_executor.py`：伺服器端執行器（從 inbox 讀，僅執行 confirmed=true）

---

## 安全策略（預設保守）

- Hub **不會自動執行高風險**；只負責收件與確認狀態
- 只有 `hub.confirmed=true` 的 job，執行器才會處理
- Hub 使用 `X-LittleJ-Token` 驗證（環境變數 `WUCHANG_HUB_TOKEN`）

---

## 伺服器端啟動（示例）

```bash
export WUCHANG_HUB_TOKEN="請換成你自己的長字串"
python little_j_hub_server.py --bind 127.0.0.1 --port 8799 --root ./little_j_hub
```

確認健康：

- `GET /health`

---

## API（Hub）

- `POST /api/hub/jobs/submit`：提交 job（JSON）
- `POST /api/hub/jobs/confirm`：確認 job（會把 `hub.confirmed=true`）
- `POST /api/hub/jobs/archive`：封存 job
- `GET /api/hub/jobs/list?state=inbox|archive`
- `GET /api/hub/jobs/get?id=<job_id>`

---

## 執行器

預設只預覽（不執行）：

```bash
python little_j_hub_executor.py --root ./little_j_hub
```

真的執行（目前示範 sync_push → git pull）：

```bash
python little_j_hub_executor.py --root ./little_j_hub --execute
```

### 重要：執行器安全開關（必須明確啟用）

為避免「完整控管」變成「誤觸即毀」，執行器即使帶 `--execute` 也需要環境變數：

- `WUCHANG_LJ_EXECUTOR_ENABLED=1`

未設就只會預覽/記錄，不會真的執行。

### 伺服器端環境回報（給本機開發者 UI 取用）

Hub 提供非機密的 machine-readable 資訊：

- `GET /api/hub/server/info`（需 `X-LittleJ-Token`）
- `GET /api/hub/server/architecture`（需 `X-LittleJ-Token`）
  - 由 `server_architecture_report.py` 產生：偏向容器/編排/port 映射，並對常見使用者路徑做去識別化（例如 `C:\Users\<REDACTED>\`）。
- `POST /api/hub/server/reports/generate`（需 `X-LittleJ-Token`）
  - 在伺服器端生成回報檔並寫入固定安全目錄：
    - 優先：`WUCHANG_SYSTEM_DB_DIR\exchange\server_reports\`
    - 否則：`<hub_root>\exchange\server_reports\`
  - 產生檔名：`server_inventory__YYYYmmdd_HHMMSS.json`、`server_architecture__YYYYmmdd_HHMMSS.json`、`server_reports__latest.json`
