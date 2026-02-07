# Odoo 樣式編譯失敗（資產管線）故障排查指南（Windows）

## 快速判斷
- 錯誤訊息：登入頁或任一頁面出現「樣式錯誤／樣式編譯失敗」。
- 常見根因：缺少 `libsass`、主題 SCSS 語法錯誤／變數遺失、資產快取損壞、與 CDN 動態載入衝突。

## 環境確認
- 檢查 Python 版本：`python --version`
- 檢查是否安裝 `libsass`：`pip show libsass`
- 若此環境未安裝 Odoo，請改用 Odoo 實際執行的 Python 環境（服務或 venv），並在該環境內執行上述指令。

## 安裝依賴（於 Odoo 執行環境）
- 安裝 libsass（Odoo 13–16 常用）：`pip install libsass==0.21.0`
- Odoo 17 資產管線變更，仍需確保官方依賴齊備，依官方文件安裝對應套件。

## 取得詳細資產日誌
- 啟動加入資產詳解：`odoo-bin --dev=assets -d <資料庫名稱>`
- 常見錯誤關鍵字：`Error compiling`, `scss`, `assets`。

## 重建資產與清除快取
- 升級核心資產模組：`odoo-bin -d <db> -u web --stop-after-init`
- 若有安裝網站模組：`odoo-bin -d <db> -u website --stop-after-init`
- 清理自動生成的資產附件（後台「設定 → 技術 → 附件」中以 CSS/JS 名稱與 mimetype 篩選），僅刪除由資產管線生成之附件。

## 尋找問題 SCSS 檔（於 addons 路徑）
- 列出 SCSS：在 PowerShell 執行 `Get-ChildItem -Recurse -Path <addons_path> -Filter *.scss`
- 檢查含有變數、函式或 `@use/@import` 的檔案，是否缺少對應來源或版本衝突。

## 與 CDN 動態載入的相容性
- 盡量避免在 QWeb 模板中以 `https://cdn.tailwindcss.com` 動態載入 CSS，改用預編譯後的本地 CSS 並透過 `__manifest__.py` 的 `assets` 宣告納入 `web.assets_frontend`。
- 這可避免 CSP、打包策略與快取的衝突，提升穩定性。

## 本倉庫現況建議
- 本倉庫未定義任何 SCSS 或 `assets` 宣告；若發生樣式編譯失敗，多半來自系統中其他 addons 或主題。
- 已移除首頁模板中誤置的登入與錯誤文字，避免誤導使用者。
- 如需我將 Tailwind 由 CDN 改為本地資產並透過 Odoo 資產管線發佈，請提供 Odoo 版本與希望的樣式來源，我可直接新增資產目錄與宣告。

## 驗證清單
- 重新啟動 Odoo 並觀察日誌無 SCSS 錯誤。
- 前端開發者工具確認 CSS 請求成功且無 404/500。
- 登入頁不再顯示「樣式編譯失敗」訊息（若仍顯示，請回看資產日誌定位具體檔案）。

