## 系統盤點報告（以證據為準）
更新時間：2026-01-15

---

## 1) 本機 DNS/hosts 覆寫（會造成「看起來沒部署/其實有部署」的假象）
證據：`C:\Windows\System32\drivers\etc\hosts`
- `wuchang.life`、`app.wuchang.life`、`ai.wuchang.life`、`llm.wuchang.life`、`asr.wuchang.life`、`tts.wuchang.life` 被固定指向 `127.0.0.1`
- `wuchang.global` 與其子網域也被固定指向 `127.0.0.1`

結論：在這台機器上，直接用瀏覽器或程式連 `wuchang.life`，**預設會打到本機**，不是公網真實服務。

---

## 2) 公網 DNS（外部真實解析）
證據來源：
- repo 檔：`dns_records.json`
- 外部驗證：`nslookup <subdomain> 8.8.8.8` 與 `nslookup <subdomain> 1.1.1.1`（結果一致）

主要 A 記錄（摘要）：
- `wuchang.life` → `35.185.167.23`, `220.135.21.74`
- `www.wuchang.life` → `220.135.21.74`
- `shop.wuchang.life` → `220.135.21.74`
- `odoo.wuchang.life` → `35.185.167.23`
- `core/admin/verify/butler/ft/vs.wuchang.life` → `35.201.170.114`
- `pos/pm/hj/housing.wuchang.life` → `104.199.144.93`

---

## 3) 本機 80/443 實際被誰接管（本機 UI/反代層的關鍵）
證據：`netstat -ano` + `tasklist` / `wmic`

### 3.1 LISTENING
- `0.0.0.0:80` / `0.0.0.0:443`：
  - PID `47404` = `com.docker.backend.exe`（Docker Desktop）
  - PID `27712` = `svchost.exe (iphlpsvc)`
- `::1:80` / `::1:443`：
  - PID `7280` = `wslrelay.exe`（WSL）

### 3.2 對本機 `wuchang.life` 的 HTTP 回應
證據：`curl -I -H "Host: wuchang.life" http://127.0.0.1/`
- 回應：`HTTP/1.1 400 Bad Request`（代表本機確實有反代/服務在回應，但因 Host/路徑/協定不符合而拒絕）

結論：你這台機器的 `wuchang.life -> 127.0.0.1` 明確存在「本機入口/反代層」，但目前回應為 400/或超時，表示需要補齊正確的 vhost/路由/對應服務才會正常。

---

## 4) 公網服務連通性（從本機出網的可達性）
證據：`Test-NetConnection` 與 `curl`

### 4.1 可達
- `220.135.21.74:8443`（RT-BE86U 遠端管理 HTTPS）：
  - `Test-NetConnection`：`TcpTestSucceeded=True`
  - `curl -k -I https://220.135.21.74:8443/`：`HTTP/1.0 200 OK`，`Server: httpd/3.0`

### 4.2 不可達（至少在此機器/此網路環境下）
- `220.135.21.74:80`：TCP 連線失敗（拒絕/未開）
- `220.135.21.74:5000`：TCP 連線失敗（未開）
- `35.185.167.23:80/443`、`35.201.170.114:80/443`、`104.199.144.93:80/443`：
  - `Test-NetConnection` 顯示 `TcpTestSucceeded=False`（多為 timeout）

解讀：這不等於「那些服務不存在」，而是「從這台機器的出網路徑目前連不到」。常見原因包括：
- 目標端防火牆未開 80/443
- 目標端只開特定來源 IP（ACL）
- ISP/網路環境對特定路徑/國外 IP 有阻斷或不穩

---

## 5) 本 workspace（repo）內實際包含的內容定位
### 5.1 git 追蹤到的檔案（`git ls-files`）
- `.gitignore`
- `MAP_3D_INTEGRATION.md`
- `README.md`
- `diagnose_connection.py`
- `dns_records.json`
- `login_router.py`
- `requirements.txt`
- `router_connection.py`
- `test_local_connection.py`

### 5.2 workspace 內目前存在（多為未追蹤/資料與 UI 片段）
- 社區分析資料與知識庫：`wuchang_community_analysis.json`、`wuchang_community_knowledge_base.json`、`wuchang_community_knowledge_index.json`…
- API 模組（Blueprint）：`api_community_data.py`、`upload_avatar_api.py`（需要「主 Flask app」掛載才可跑）
- UI/展示頁：`system_architecture.html`、`wuchang_community_dashboard.html`
- 小 J icon HTML 片段：`little_j_floating_icon.py`（會呼叫 `/api/ai/settings`、`/api/ai/execute`，但本 workspace 未見該 API 實作）

### 5.3 文件提到但 workspace 內缺少的元件（表示主系統在別處）
在 `MAP_3D_INTEGRATION.md` / `WUCHANG_COMMUNITY_ANALYSIS.md` / `LITTLE_J_ICON_GUIDE.md` 中提到：
- `web_ui.py`
- `map_api_routes.py`
- `map_downloader.py`
- `map_3d_viewer.html`
- `responsive_ui_module.py`
上述檔案在本 workspace 內 **不存在**，因此文件所描述的「localhost:5000 Web UI」與「地圖 API」應位於其他 repo/其他主機/或尚未同步到此 workspace。

---

## 6) 盤點結論（當前可用的架構對話基準）
1. 你本機有一個「wuchang.life 本機入口層」（hosts + 80/443 listener），由 Docker/WSL/系統服務介入；目前回應 400/超時，代表入口存在但路由未對齊。
2. 公網 DNS 的子網域分流架構清楚（220.* / 35.* / 104.*），但從此機器出網目前只穩定打到 `220.135.21.74:8443`，其餘多為 timeout。
3. 本 workspace 的角色偏向「UI/資料/片段與工具」，不是完整後端；主系統（尤其是 `core/pos/admin/verify/odoo` 對應的服務實作與部署）必須到對應主機或其他 repo 才能盤到。

