# 新商家導入與服務流程（SOP）

本文件作為新加盟商家自動化導入與日常服務的標準流程，涵蓋事前準備、安裝部署、驗收、日常維運與支援升級。

## 1) 事前準備（T-3 ~ T-1 天）

-   資料蒐集：公司名稱、聯絡窗口、門市地址、營業時間、POS 序號/裝置數量。
-   硬體檢核：使用 `check_hardware.ps1` 評估既有電腦是否足以支撐 POS/客顯。
-   網路規劃：路由器位址（預設 192.168.50.1）、伺服器位址（預設 192.168.50.249）。
-   帳號與權限：Odoo 後台管理者、操作員帳號建立，API 權限確認。
-   本地 AI：Ollama 啟動並載入 `little-j` 模型，伺服器 `.ps1` 以 LOCAL_LLM 優先。

## 2) 安裝部署（T 日）

-   伺服器側：
    -   啟動管理伺服器：`run_server.ps1`（確保 8080 對 LAN 開放）。
    -   驗證 API：`GET /` → `Status=Ready`；`/network/arp` 應能列出路由與節點。
-   裝置側：
    -   POS（Windows）：以 `run_agent_POS.bat` 啟動；若多台，分別指定 `--hostname`。
    -   客顯（Chrome OS）：啟用 Linux（Crostini），執行 `run_agent_chromeos.sh`。
    -   成功註冊後於 `/devices` 可見；心跳每 5 秒更新。
-   初始同步：
    -   對 POS 推送：`{"device_type":"POS","command":{"type":"SYNC_UI"}}`
    -   對 客顯 推送：`{"device_type":"CUSTOMER","command":{"type":"SYNC_UI"}}`

## 3) 驗收測試（T 日）

-   POS 與客顯 UI 均能顯示，結帳流程 3 筆成功（現金、信用卡、退貨）。
-   RELOAD 測試成功（畫面可快速回到首頁）。
-   `/devices` 顯示裝置 `last_seen` 持續更新。
-   `/llm/chat` 回應 `source=local`；拔除本地 LLM 後可自動 fallback 至雲端。

## 4) 日常維運

-   每日開店：裝置自動啟動代理 → 自動同步 UI。
-   異常排除：
    -   先檢查 `/devices` 是否在線 → 推送 `RELOAD` → 若仍異常，重啟代理。
    -   需要網路排除時，確認路由器/伺服器可達（`ping`）與 ARP 清單。
-   設定更新：透過伺服器變更 `POS_UI_URL/CUSTOMER_UI_URL`，裝置會在下次輪詢套用。

## 5) 遠端支援與升級

-   版本升級：以腳本推送更新代理/客戶端設定，避免手動登入。
-   硬體升級：依 `HARDWARE_REQUIREMENTS.md` 建議（RAM/SSD）逐步改善體驗。
-   備援策略：
    -   LLM：本地優先，失效即切雲端。
    -   網路：保留行動熱點方案；異地備援伺服器可選。

## 6) 快速指令（PowerShell）

```powershell
# 列出裝置
Invoke-RestMethod http://localhost:8080/devices | ConvertTo-Json -Depth 5

# 推送 POS/客顯同步 UI
$pos = @{ device_type = 'POS'; command = @{ type='SYNC_UI' } } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri http://localhost:8080/commands/push -Body $pos -ContentType 'application/json'

$cus = @{ device_type = 'CUSTOMER'; command = @{ type='SYNC_UI' } } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri http://localhost:8080/commands/push -Body $cus -ContentType 'application/json'

# 推送 RELOAD
$reload = @{ device_type = 'POS'; command = @{ type='RELOAD' } } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri http://localhost:8080/commands/push -Body $reload -ContentType 'application/json'
```

---

如需自動化完整導入，可執行 `scripts/simulate_new_merchant.ps1` 進行演練或驗收。
