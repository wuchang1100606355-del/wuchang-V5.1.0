## 會員折扣票券 / 商品券 / 折扣碼（預留模組）

目的：先把「商務/會員優惠」相關能力以 **編號化（ID）** 的方式預留在系統內，讓日後擴充 UI、串接購物/付款/會員系統時不需要大改。

### 設計原則

- **全部依賴編號**：`voucher_id / owner_account_id / org_id / campaign_id / product_id`
- **不回傳明文折扣碼**：API 永遠不回傳 `code_plain`，只回傳 `code_masked`（例如 `****A1B2`）與狀態
- **本機/Drive 落地**：資料寫入 Google Drive 同步資料夾（`WUCHANG_PII_OUTDIR` 或 `WUCHANG_WORKSPACE_OUTDIR`）
- **稽核不含秘密**：`voucher_audit.jsonl` 只記 sha256 摘要，不含折扣碼明文

### 儲存檔

- `commerce/vouchers.json`（在你的 Drive 同步夾內）
- `voucher_audit.jsonl`（repo 內，僅摘要/不含秘密）

### 目前已預留 API（後端）

- `GET /api/vouchers/list?owner_account_id=...`
- `POST /api/vouchers/upsert`
- `POST /api/vouchers/validate`
- `POST /api/vouchers/redeem`

### 權限（建議）

- `voucher_read`：可查看清單/驗證
- `voucher_manage`：可建立/更新票券
- `voucher_redeem`：可兌換

