# 最高權限倉位啟用操作指南

## 問題描述
- 系統檢測到最高權限倉位未啟用，導致管理入口 `/admin` 無法進入。
- 該倉位負責最高級別操作（審計、同意管理、策略配置），需受嚴格權限與環境保護。

## 排查步驟
1. 檢查環境標記位：
   - `VITE_ADMIN_ENABLED` 是否為 `true`
   - `VITE_ADMIN_TOKEN_SHA256` 是否已配置（令牌 SHA-256 雜湊）
2. 檢查本機標記位（替代方式）：
   - `localStorage.admin-enabled` 是否為 `true`
   - `localStorage.admin-token-hash` 是否存在（令牌 SHA-256 雜湊）
3. 審查審計記錄：
   - `localStorage.ai-compliance-audit` 中事件 `admin_enable_local`, `admin_save_token_hash`, `admin_access_success` 是否存在
4. 確認非公開環境：
   - 主機名需為 `localhost/127.0.0.1/10.* /192.168.* /172.16–31.*`

## 啟用流程
### 方式 A：環境變數（推薦，用於持久化）
1. 設定環境變數（`.env` 或 CI/CD 注入）：
   - `VITE_ADMIN_ENABLED=true`
   - `VITE_ADMIN_TOKEN_SHA256=<你的令牌 SHA-256 雜湊>`
2. 生成令牌雜湊（Windows/Node）：
   - PowerShell：
     ```
     node -e "console.log(require('crypto').createHash('sha256').update(process.argv[1]).digest('hex'))" "YOUR_TOKEN"
     ```
3. 重啟前端開發服務（或重新部署），訪問 `/admin` 輸入令牌驗證。

### 方式 B：本機快速啟用（僅限測試開發）
1. 打開 `/admin`，點「本機啟用入口」（寫入 `admin-enabled=true`）。
2. 輸入令牌，點「保存本機令牌」（寫入 `admin-token-hash`）。
3. 點「驗證並進入」。

## 權限驗證步驟
- 僅非公開環境可進入（前置檢查）。
- 令牌驗證通過後進入最高權限頁面。
- 操作事件寫入審計（本地 `ai-compliance-audit`）。

## 重啟後狀態確認
- 方式 A：環境變數配置會持續有效；重啟後直接訪問 `/admin`。
- 方式 B：依賴瀏覽器 `localStorage`；清除快取或更換瀏覽器需重新啟用與保存令牌。

## 驗證標準
1. 功能運作：最高權限頁能載入同意清單與最近審計事件，撤回同意正常。
2. ACL 正確：未啟用或令牌錯誤時不可進入；公開環境阻擋進入。
3. 依賴流程：與「同意控管」「生物辨識」等模組交互正常。

## 風險與建議
- 不要在公開環境啟用最高權限倉位。
- 令牌請使用高強度字串；雜湊不可逆，勿保存明文令牌。
- 審計需定期匯出與留存（合規要求）。

