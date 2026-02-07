# API 参考

- `POST /api/deploy/diag`（auth=user）
  - 返回：`lib_google_genai_present`、`google_api_key_set`、`google_ok`、`ollama_ok`、`webui_ok`
- `POST /api/deploy/apply`（auth=user）
  - 入参：`ai_mode`、`gen_model`、`google_api_key`、`ollama_model`
  - 返回：`snapshot_saved`、`needs_ui_start`
- `POST /api/deploy/rollback`（auth=user）
  - 返回：`ok`
- `POST /api/perf/status`（auth=user）
  - 返回：`ai_mode`、`daily_quota`、`daily_used`、`ollama_ok`、`webui_ok`
- `POST /api/perf/allocate`（auth=user）
  - 返回：`ai_mode`、`ollama_model`
- `POST /api/ide/tools`（auth=user）
  - 返回：`webui_url`、`ollama_models[]`、`verification{}`、`paths{}`
- `POST /api/ai/resources`（auth=public）
  - 返回：`curated{models,frameworks,tools}`、`policy{}`、`plugins[]`

## 日志与快照
- 快照：`/opt/wuchang/memory_store/deploy/snapshot.json`
- 日志：`/opt/wuchang/memory_store/deploy/logs.jsonl`
