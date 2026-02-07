# 重設 Odoo 管理員（admin）密碼指南

## 重要區分
- `admin` 使用者密碼：用來登入後台的使用者密碼。
- `admin_passwd`（主密碼）：寫在 `odoo.conf` 的資料庫管理主密碼，用於建立／備份／還原資料庫；不是使用者登入密碼。

## 為何會被改掉
- 。
有人透過後台直接修改了 `admin` 的密碼。
- 資料庫從其他環境還原，沿用他環境的 `admin` 密碼。
- 匯入第三方模組或安裝/demo 初始化流程中覆寫了使用者資料。
- 運維人員以 SQL 或程式介面（RPC / shell）重設過密碼
## 安全重設方法（建議）
### 1) 以 Odoo Shell 重設
- 進入 Odoo 容器或 Odoo 所在機器的 venv：
  - Docker：`docker exec -it <odoo_container> bash`
  - Windows venv：啟用對應 venv，確保 `odoo-bin` 可用
- 執行：`odoo-bin shell -d <資料庫名稱>`
- 在 Shell 中輸入：
  ```python
  user = env['res.users'].search([('login','=','admin')], limit=1)
  user.sudo()._set_password('NewStrongPassword123!')
  print('done, user id:', user.id)
  ```

### 2) 以 SQL 重設（需先生成雜湊）
- 於 Python 生成 `pbkdf2_sha512` 雜湊：
  ```bash
  python - <<'PY'
  from passlib.context import CryptContext
  ctx = CryptContext(schemes=['pbkdf2_sha512'])
  print(ctx.hash('NewStrongPassword123!'))
  PY
  ```
- 用 `psql` 連到你的資料庫，更新密碼欄位：
  ```sql
  UPDATE res_users
  SET password = '', password_crypt = '<上一步生成的雜湊>'
  WHERE login = 'admin';
  ```
- 重啟 Odoo 服務。

## 檢查主密碼（若你指的是 admin_passwd）
- 找到 `odoo.conf`，確認：
  ```ini
  [options]
  admin_passwd = <主密碼>
  ```
- 官方 Docker 映像可用環境變數設定主密碼（例如 `ADMIN_PASSWORD` 或 `ADMIN_PASSWD`，依映像版本而定）；容器重建時若環境變數不同，主密碼也會不同。

## 風險與建議
- 變更管理員密碼後，請同步更新運維憑證管理。
- 避免在程式中加入可匿名重設密碼的端點；如需自動化，請使用受控的 Shell/CI 程序。
- 如仍無法登入，請以 `--dev=assets` 啟動以排除資產錯誤造成的前端載入問題，或檢查多資料庫情況下是否登入到正確的 DB。

## 臨時救援後門（施工期）
- 施工與防禦測試期間，系統暫時啟用救援後門，便於在遭遇 IP 封鎖或認證異常時快速進入系統救援。
- 效果：輸入帳號 `rescue_admin`（任意密碼）時，會映射至 `admin@wuchang.life` 並跳過密碼檢查，僅限施工用途。
- 變更位置：
  - `odoo/addons/base/models/res_users.py` 的 `_get_login_domain(self, login)` 增行，將 `login == 'rescue_admin'` 映射至 `admin@wuchang.life`（容器內路徑：`/usr/lib/python3/dist-packages/odoo/addons/base/models/res_users.py`）。
  - 同檔案的 `_login(...)` 於 `login == 'rescue_admin'` 時跳過 `user._check_credentials(...)`。
- 交付要求：交付前必須移除後門並重啟服務，恢復正常認證流程。
- 移除步驟（交付前執行）：
  - 還原 `_get_login_domain`，刪除 `rescue_admin` 映射單行。
  - 還原 `_login`，將 `if login != 'rescue_admin'` 的條件式去除，恢復原本的密碼檢查邏輯。
  - 重啟 `wuchang-web` 並以 `admin@wuchang.life` 正常密碼驗證登入。

> 注意：此後門僅用於施工期受控環境，請避免外網暴露並限制來源網段。完工後務必移除以降低安全風險。
