## Google Workspace（Drive 同步）精準對齊：環境變數與資料夾結構

目標：讓「所有平台功能」在不導入 OAuth / Admin SDK 的前提下，**精準落地**到 Google Drive 同步資料夾並可稽核。

---

## 建議 Drive 資料夾結構（你只要建一次）

在你的 Google Drive 同步路徑下建立：

- `五常_中控/`
  - `config/`：設定檔（不含個資）
    - `accounts_policy.json`
    - `workspace_matching.json`
  - `vault/`：私密 vault（可識別/不可識別/同意/票券）
    - `pii_contacts.json`
    - `pii_contacts_non_identifiable.json`
    - `account_profiles_non_identifiable.json`
    - `consent_receipts.json`
    - `commerce/vouchers.json`
  - `exchange/`：設備委派交換檔
    - `device_tasks/`
    - `device_results/`
    - `device_results_imported/`
  - `artifacts/`：一般輸出（小J/報表/稽核輸出到 Workspace）

---

## 建議環境變數（PowerShell）

> 設定後請**重開終端機**再啟動主控台。

```powershell
setx WUCHANG_WORKSPACE_OUTDIR "C:\Users\<你>\Google Drive\五常_中控\artifacts"
setx WUCHANG_WORKSPACE_EXCHANGE_DIR "C:\Users\<你>\Google Drive\五常_中控\exchange"
setx WUCHANG_PII_OUTDIR "C:\Users\<你>\Google Drive\五常_中控\vault"
setx WUCHANG_ACCOUNTS_PATH "C:\Users\<你>\Google Drive\五常_中控\config\accounts_policy.json"
setx WUCHANG_WORKSPACE_MATCHING_PATH "C:\Users\<你>\Google Drive\五常_中控\config\workspace_matching.json"
```

可選：

- `WUCHANG_WORKSPACE_WEBHOOK_URL`：若你要 Apps Script webhook

---

## 一鍵檢查（腳本）

本 repo 內提供：

- `workspace_alignment_check.py`

它會輸出 JSON，告訴你：

- 哪些目錄/檔案存在或缺少
- 是否有把資料夾放在 repo 內（不建議）
- 建議的 setx 指令

主控台也提供對應 API：

- `GET /api/workspace/alignment`

