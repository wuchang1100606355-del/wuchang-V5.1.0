# ODOO 專業顧問AI遷移至 UI 總AI 架構

## 目標
- 將 ODOO 專業顧問 AI 的功能模組整合至 UI 總AI，統一接口、數據與部署。

## 模組化結構
- 核心入口：`wuchang_design_system.controllers.web_login_home` 提供標準 API。
- 模組清單：`/api/ui_ai/modules` 回傳可用模組與引擎狀態。
- 分身窗口：前台 `/xj/window/<key>`、後台 `/xj/admin/window/<key>`。

## 標準 API
- `POST /api/ui_ai/spec`：回傳模組與存儲路徑。
- `POST /api/ui_ai/modules`：查詢 `odoo_advisor` 模組狀態。
- `POST /api/ui_ai/config/sync`：同步顧問設定到 UI 總AI。
- `POST /api/ui_ai/odoo/consult`：顧問諮詢，遵循 `ai_mode` 路由（Google 或 Ollama）。
- `POST /api/ui_ai/data/migrate`：遷移設定與歷史紀錄至存儲。

## 數據遷移
- 存儲路徑：`/opt/wuchang/memory_store/ui_ai/odoo`。
- `config.json`：完整設定快照。
- `history.jsonl`：逐筆記錄（含 `ts`、`text` 等）。

## 測試計畫
- 單元測試：以 `scripts/sanity_deploy_tests.ps1` 呼叫各 API。
- 集成測試：驗證 `ai_mode` 下游引擎（Google、Ollama）可用性。
- UAT：在 POS/首頁嵌入呼叫窗口，驗證互動流程與性能。

## 部署與回滾
- 分支：`migration/ui-total-ai` 作為遷移工作分支。
- 分階段：先上線 API，再導入資料與前端嵌入，最後切換引擎模式。
- 回滾：`POST /api/deploy/rollback` 以快照還原核心配置。

## 性能與穩定
- 依 `/api/deploy/diag` 與 `/api/perf/status` 監控狀態，自動開關備援。
- 使用 `Ollama` 或 `Google Generative AI` 依配額與可用性分配。

## 安全
- API 需 `auth='user'`，建議僅限管理角色。
- 可搭配固定 IP 白名單以限制遷移入口來源。

