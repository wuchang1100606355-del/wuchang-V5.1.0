# 外網登入維持方案

- 反向代理：已加入 Caddy（80/443）代理到 `wuchang-web`，並處理 `/longpolling*` 至 8072。
- 代理模式：Odoo 已啟用 `proxy_mode` 並設定 `--longpolling-port=8072`。
- 無固定 IP：採用 Cloudflare Tunnel。

臨時隧道（trycloudflare.com）：
- 已啟動 `cloudflared` 服務，將本機代理到雲端，會自動分配臨時網址。
- 查詢網址：`docker logs <cloudflared-container> | grep trycloudflare.com`
- 驗證：造訪 `https://<assigned>.trycloudflare.com/web/login`（可正常登入頁）。

長期穩定隧道（建議）：
- 申請 Cloudflare 帳號與域名，建立 Named Tunnel（固定子域），將 `http://caddy:80` 作為 Origin。
- 在 `docker-compose.yml` 以 `cloudflared` 指令 `tunnel run --token <TUNNEL_TOKEN>` 啟動。
- OAuth 設定：將 Google OAuth 的 redirect URI 指向固定子域（例：`https://ui.<your-domain>/auth_oauth/signin`）。

Odoo 參數建議：
- `website.canonical_host`：設定為固定子域（例：`ui.<your-domain>`），避免鏈接錯誤；可用後台設定或執行 `scripts/odoo_set_params.py` 並提供環境變數 `WEBSITE_HOST`。
- `web.base.url`：如有需要固定，於系統參數設定為 `https://ui.<your-domain>`。

故障排查：
- 登入頁 200：`https://<your-domain>/web/login` 可達且返回 200。
- 健康檢查：`https://<your-domain>/health` 返回 200。
- Longpolling：操作聊天/通知正常顯示即代表 `/longpolling*` 代理生效。
