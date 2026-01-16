# 設備/帳號委派協定（合規版）

目標：當使用者提出需求需要「用使用者自己的設備或帳號 API」完成時，系統仍能做到：

- **合規**：資料最小化、明確同意、可撤回、可稽核
- **合理**：不強迫你再做大量設定、不把使用者帳號 token 存進系統、不把個資丟進雲端模型

## 核心原則

- **自己的帳號自己跑**：需要手機 Gemini / Google 帳號 / 其他設備 App 才能完成的工作，原則上讓該設備以「使用者自身登入狀態」去做；本系統不代管 token。
- **最小資料**：委派任務只傳「目標、限制、輸出格式」，不傳個資/憑證/金鑰。
- **個資留本機（或 PII Vault）**：個資只存在本機 UI 的 PII Vault（Google Drive 私密夾），不要寫進 job、不要寫進回覆檔。
- **可稽核但不洩漏**：稽核記錄只寫摘要/雜湊，避免明文敏感資訊。
- **無回應＝禁止高風險作業**：委派本身不是高風險執行；若委派結果要觸發高風險動作，仍要走 SOP 與確認/健康檢查閘門。
- **同意先行（必顯示使用權利）**：若任務會使用任何（含不可識別）個資，設備端必須先顯示「範圍/用途/保存期限/使用者權利（可撤回）」並取得同意，否則不得執行。

## 建議流程（最少設定、最可落地）

### A. 系統建立「設備任務」

- 由本機中控台呼叫 `POST /api/device/request`
- 產生：
  - repo 內一張 `jobs/outbox/<job_id>.json`（只含任務描述與 token 的 **sha256**）
  - Google Drive 同步夾內一張 `device_tasks/<job_id>.json`（含一次性 `reply_token`）

> 補充：任務檔會包含 `consent.policy`（用途/範圍/使用權利/保存期限）。設備端必須顯示並回收同意狀態。

### B. 使用者設備完成任務並回覆（使用自己的 App / 帳號）

設備端（例如手機）讀取 `device_tasks/<job_id>.json` 後：

- 用自己的 App（例如 Gemini）完成工作
- 把回覆寫成 JSON 放到 `device_results/<job_id>.json`
- 回覆檔包含：
  - `job_id`
  - `reply_token`（任務檔內提供的一次性 token）
  - `artifact`（建議只放「輸出檔案的路徑/雜湊」而非全文內容）

### C. 本機匯入回覆（只存摘要/雜湊）

由本機中控台呼叫 `POST /api/device/import_results`：

- 驗證 `reply_token`（比對 repo job 內存的 `sha256`，並檢查效期）
- 將 job 標記 `device_done=true`，只寫入：
  - 回覆 JSON 的 `sha256`
  - `artifact` 的參考資訊（例如 workspace 檔案路徑、檔案 sha256）
- 把回覆檔搬到 `device_results_imported/`，避免重複匯入

## 權限（帳號號碼 → 能做什麼）

建議新增/使用權限：

- `device_request`：允許建立設備委派任務
- `job_manage`：允許匯入設備回覆（因為會寫回 job 檔）

## 最小回覆格式（範例）

`device_results/<job_id>.json` 建議長這樣（不要放個資明文）：

```json
{
  "job_id": "abcd1234ef56",
  "reply_token": "（任務檔內的 token）",
  "note": "完成：已用手機 Gemini 生成摘要，並存到 Workspace。",
  "artifact": {
    "kind": "workspace_file",
    "path": "outputs/device/abcd1234ef56_summary.txt",
    "sha256": "（檔案 sha256，可選）"
  }
}
```

## 為什麼這樣「合規又合理」

- **合規**：token/稽核可追溯；不把 token/個資丟到雲端模型；資料最小化；結果以檔案參考（artifact）呈現。
- **合理**：不需要你在本機再配置一堆 OAuth；使用者設備用自己的既有登入狀態完成；交換只靠你已經在用的 Google Drive 同步。

