# Jules 自動同步（無人值守）

- 任務：定期下載 `https://jules.google.com/task/8263971059525947125` 快照並保存到 `downloads/jules`，維護 `latest.html`/`latest.hash`
- 腳本：`scripts/jules_sync.ps1`
- 排程：`scripts/install_jules_sync_task.ps1`

設定連結：

- 於 `config/jules.url.txt` 寫入欲同步之任務頁 URL（預設已為上方連結）

授權方式：

- 建議使用訪客模式或無痕視窗登入 Google 帳號後，複製該頁請求的 `Cookie` 值
- 將 `Cookie` 值寫入 `config/jules.cookie.txt`，或以環境變數 `JULES_COOKIE` 提供

使用步驟：

- 安裝排程：在項目根目錄執行 `./scripts/install_jules_sync_task.ps1 -IntervalMinutes 30`
- 手動測試：`./scripts/jules_sync.ps1` 或指定連結 `./scripts/jules_sync.ps1 -Url "<your_url>"`

輸出與路徑：

- 快照目錄：`downloads/jules/<timestamp>/download.html`
- 最新檔案：`downloads/jules/latest.html`、`downloads/jules/latest.hash`
- 日誌：`automation.log`

調整排程間隔：

- 參數 `-IntervalMinutes` 支援任何整數分鐘值

容器掛載與啟動：

- 於 `docker-compose.yml` 已為 `wuchang-web` 掛載：
  - `./downloads/jules:/mnt/jules:rw`
  - `./config:/mnt/jules-config:ro`
- 啟動容器：`scripts/startup_compose.ps1`（自動等待 Docker 就緒並執行 `docker-compose up -d`）
- 驗證映射：
  - `docker exec wuchangv510-wuchang-web-1 ls -la /mnt/jules`
  - `docker exec wuchangv510-wuchang-web-1 ls -la /mnt/jules-config`
