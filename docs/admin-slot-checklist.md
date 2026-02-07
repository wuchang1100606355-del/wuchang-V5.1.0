# 最高權限倉位排查與驗證檢查清單

## 排查清單
- [ ] 非公開環境（localhost/私網）
- [ ] `VITE_ADMIN_ENABLED=true` 或 `localStorage.admin-enabled=true`
- [ ] `VITE_ADMIN_TOKEN_SHA256` 或 `localStorage.admin-token-hash` 已設置
- [ ] 審計存在：`admin_enable_local` / `admin_save_token_hash` / `admin_access_success`
- [ ] `/admin` 載入成功，令牌驗證通過

## 驗證清單
- [ ] 同意清單載入與撤回操作正常
- [ ] 審計事件顯示最新 10 條（含成功進入）
- [ ] 錯誤令牌時拒絕進入，提示正確
- [ ] 公開環境嘗試進入被阻擋
- [ ] 生物辨識與偏好學習功能在啟用後仍正常

## 重啟確認
- [ ] 以環境變數方式：重啟後仍可進入 `/admin`
- [ ] 以本機方式：瀏覽器未清除快取，`localStorage` 仍在

## 預防性維護
- [ ] 令牌定期輪換並更新雜湊
- [ ] 定期匯出審計事件至安全存儲
- [ ] 每次部署後執行本檢查清單一次

