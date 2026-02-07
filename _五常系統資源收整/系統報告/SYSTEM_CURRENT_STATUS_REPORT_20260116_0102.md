# 系統現狀詳細報告（Wuchang V5.1.0）

**產出時間**：2026-01-16 01:01（本機時間）  
**工作目標**：彙整「本機 + VM + Google Workspace（手動項）」的可驗證現況，給出下一步行動。  

---

## 1) 主機（本機）基本資訊

- **OS**：Microsoft Windows 10 專業版 (10.0.19045)
- **Host**：HOME-COMMPUT
- **User**：User

---

## 2) Docker 現狀

### 2.1 Docker Context

目前存在多個 context（其中 `vm-server` 指向遠端 SSH）：

- `default`（本機 npipe）
- `desktop-linux`
- `ui-laptop`：`ssh://wuchang@192.168.50.84`
- `vm-server`：`ssh://administrator@192.168.50.249`（先前造成 `docker ps` 連線錯誤）

> ✅ 已切回 `docker context use default`，以下容器狀態為 **本機 docker**。

### 2.2 本機正在運行的容器（docker ps）

- `wuchangv510-caddy-1`：80/443
- `wuchangv510-wuchang-web-1`：8069
- `wuchangv510-db-1`：5432（容器內）
- `wuchangv510-caddy-ui-1`：8081/8444
- `wuchangv510-uptime-kuma-1`：3001（healthy）
- `wuchangv510-portainer-1`：9000
- `wuchangv510-ollama-1`：11434
- `wuchangv510-cloudflared-1`：無本機對外端口（tunnel）

### 2.3 重要提示

- **`docker ps` 先前報錯**屬於「Docker context 指向遠端（192.168.50.249）且 SSH 失敗」造成；與本機容器是否運行**無直接關係**。

---

## 3) 本機端口/HTTP 健康檢查

### 3.1 本機端口監聽（127.0.0.1）

- **OPEN**：80, 443, 8069, 8081, 8767, 9000, 3001
- **closed**：8072, 8080, 8766

> 注意：Odoo longpolling 在 compose 裡設定為 8072，但目前本機 8072 顯示 closed（需後續確認是否真的需要對外映射或由 caddy 內部轉發即可）。

### 3.2 HTTP 回應

- `http://127.0.0.1:8069/web/login` → **HTTP 200**（Odoo 正常）
- `http://127.0.0.1:9000/` → **HTTP 200**（Portainer 正常）
- `http://127.0.0.1:3001/` → **HTTP 200**（Uptime Kuma 正常）
- `http://127.0.0.1:8080/` → **FAIL**（FastAPI/OpenWebUI 未提供服務）

---

## 4) VM（192.168.50.84）連線現況

### 4.1 端口可達性（從本機測試）

- `192.168.50.84:22` → **OPEN**（SSH 可達）
- `192.168.50.84:8069` → **OPEN**（Odoo 可達）
- `192.168.50.84:8767` → **closed**（VM 端 voice/8767 目前未開）

> 與前述本機相比：本機 8767 是 OPEN，但 VM 8767 是 closed。若目標是由 VM 提供 voice service，需要在 VM 端啟動對應服務/反向代理。

---

## 5) Python / Debug 現況（本機）

### 5.1 專案內建 Python

- `C:\wuchang V5.1.0\.conda\python.exe` → **Python 3.11.14**
- `requests / fastapi / uvicorn` → **可 import（python_deps_ok）**

### 5.2 Debug Console 出現的錯誤（已定位）

你看到的：
- `activate : ... not recognized`
- `conda : ... not recognized`

屬於 **誤輸入/PowerShell 未初始化 conda**，並非系統崩壞。

### 5.3 uvicorn --reload 問題（已定位）

執行：
- `uvicorn vm_fastapi_main_dual_role:app --reload`

會因 Windows reloader 子行程啟動失敗而報：
- `FileNotFoundError: [WinError 3] 系統找不到指定的路徑。`

建議：
- 改用 **不帶 `--reload`** 啟動，或
- 將專案路徑搬到 **不含空白** 的目錄（避免 reload 子行程路徑問題）。

---

## 6) 私人 DNS / hosts（本機）

目前在本機 hosts 可看到：
- `192.168.50.84  pos-server.chong-sin.local`
- `192.168.50.84  odoo.chong-sin.local`

尚未看到：
- `api.chong-sin.local`（如需要，建議補上並 flushdns）

---

## 7) Google Workspace（裝置/OU/乙太網路政策）現況與待辦

### 7.1 已產出檢查報告（勾選清單）

- `logs/google_workspace_device_check_20260115_212112.md`
- `docs/GOOGLE_WORKSPACE_DEVICE_SETTINGS_CHECK.md`

### 7.2 目前你已完成的關鍵進展（根據對話與截圖）

- `wuchang.life` 網域下已有 `Infrastructure` OU（含 `Control` / `Servers`）
- `Stores` OU 已建立並已回到根層（非掛在 Servers）
- `Stores` 的 **乙太網路政策**頁面下已看到「重新店路由器」「重新店」兩筆（表示已經開始放到門市 OU）

### 7.3 待完成（建議最小閉環）

1. 建立 `Stores/ChongSin/CustomerDisplay` 子 OU（避免門市與伺服器混用政策）
2. 將 **ChromeOS 客顯裝置**移到 `Stores/ChongSin/CustomerDisplay`
3. 確認乙太網路政策只存在於 `Stores`（不要再出現在 `Infrastructure/Servers`）
4. 到 **Admin audit log** 確認「那兩筆政策」的 Actor（誰建立/修改），以便追溯與定責

---

## 8) Git 工作區狀態（摘要）

- `git status` 顯示大量新增/修改檔案（包含多個 `.backup`、報告、腳本等）
- 這會增加 IDE/自動提交的負擔（之前已遇過 timeout）

建議（如要降低噪音/避免 timeout）：
- 明確決定哪些報告/backup 需要納入版控，其餘加入 `.gitignore`

---

## 9) 下一步建議（按優先級）

### P0（立即）

- **Google Workspace 門市客顯閉環**：建立 `Stores/ChongSin/CustomerDisplay` → 移動客顯裝置 → 確認乙太網路政策生效

### P1（系統一致性）

- **VM voice service（8767）**：若需要 VM 提供 8767，需在 VM 啟動/開放並在路由器/反代做對應

### P2（開發/Debug 穩定）

- 若要跑 `vm_fastapi_main_dual_role.py`：先用「無 reload」啟動；之後再處理路徑含空白導致 reload 失敗

---

## 附件/參考

- `docker-compose.yml`：本機 system/ui profiles（open-webui 在此檔內註解）
- `docker-compose-ai.yml`：提供 open-webui:8080（目前本機 8080 closed，推測未啟動此 compose）

