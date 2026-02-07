# Docker 容器掛載安全檢查與完整健康檢查方案

## 1. 連線脈絡與風險分析 (Connection Context & Risk Analysis)
- **現狀脈絡**：目前系統運行於 Google Drive (J:) 虛擬磁碟上。
- **風險點**：Docker 無法穩定掛載 (Bind Mount) 虛擬磁碟上的設定檔 (`odoo.conf`, `config.yml`)，導致服務啟動失敗或無限重啟。
- **解決方案**：採用「主動同步策略」，將設定檔從 J: 複製到 Docker Named Volumes (`wuchang-odoo-config`, `wuchang-cloudflared-config`)。

## 2. 掛載前安全檢查設計 (Pre-Mount Safety Check)
在執行同步與啟動前，必須通過以下檢查：
1. **來源檔案完整性檢查**：
   - 確認 `config/odoo/odoo.conf` 存在且非空。
   - 確認 `config/cloudflared/config.yml` 存在且包含 `tunnel:` ID。
   - 確認 `config/cloudflared/credentials.json` 存在且為有效 JSON。
2. **Docker 環境檢查**：
   - 確認 Docker Daemon 正在運行。
   - 確認目標 Volume 是否已建立，若無則自動建立。
3. **路徑編碼檢查**：
   - 確保複製過程不受中文路徑 (`共用雲端硬碟`) 影響 (使用相對路徑或 PowerShell 轉碼)。

## 3. 部屬後完整健康檢查方案 (Post-Deployment Health Check)
部屬完成後，執行以下層次檢查：
1. **容器狀態層 (Container Level)**：
   - 檢查 `wuchang-pos` 與 `wuchang-tunnel` 狀態是否為 `Up` (非 Restarting)。
   - 檢查 Exit Code 是否為 0。
2. **應用服務層 (Application Level)**：
   - **Odoo**: 檢測 Port 8069 回應 (HTTP 200/303)。
   - **Tunnel**: 檢測 Cloudflare Tunnel Log 是否顯示 `Registered tunnel connection`。
3. **連線脈絡層 (Connectivity Level)**：
   - **外部存取**: 透過 `https://app.wuchang.life` 驗證是否能抵達 Odoo (需 DNS 生效)。
   - **內部互通**: 驗證 Odoo 容器是否能連線至 Postgres DB。

## 4. 執行工具
- **同步與檢查腳本**: `tools/sync_docker_configs.ps1`
- **深度健康檢查**: `tools/deep_health_check.py`

