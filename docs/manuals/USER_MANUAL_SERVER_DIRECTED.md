# 五常 AI 系統 - 使用者操作手冊 (伺服器指揮模式)
> **版本**: 5.1.0 (Server Directed)  
> **日期**: 2026-01-12  
> **適用對象**: 系統管理員、操作人員

---

## 1. 系統架構概覽
本系統目前運行於 **「伺服器指揮模式 (Server Directed Mode)」**。在此模式下，本機 (Local Node) 作為執行端，完全聽命於中央伺服器 (Server Node) 的調度與指揮。

*   **本機 (Local)**: `192.168.50.84` (Windows)
*   **伺服器 (Server)**: `192.168.50.249` (Linux) / `92.18.50.249` (External)

### 核心功能
1.  **UI 遠端控制**: 伺服器可直接開啟本機的 Odoo、AI 助理或瀏覽器畫面。
2.  **被動雲端同步**: 檔案變更由伺服器發起同步請求，本機負責接收或上傳。
3.  **SSH 安全通道**: 伺服器透過加密金鑰直接管理本機系統。

---

## 2. 每日開機與啟動流程
請依照以下步驟啟動系統，確保與伺服器的連線正常。

### 步驟 1: 執行啟動腳本
在桌面或 PowerShell 中執行以下指令：

```powershell
.\start_server_directed_mode.ps1
```

**成功訊號**:
*   看見 `[OK] Local UI Server Started`
*   看見 `[OK] Cloud Sync Service (Passive Mode) Started`
*   最後顯示 `SYSTEM IS NOW IN SERVER-DIRECTED OPTIMIZATION MODE`

### 步驟 2: 啟動檔案監測 (選用)
若需即時監控檔案變更並協助握手，請執行：

```powershell
python scripts/monitor_and_handshake.py
```

---

## 3. 使用者操作指南

### 3.1 存取 Odoo ERP
*   **方式 A (伺服器控制)**: 等待伺服器自動彈出 Odoo 視窗。
*   **方式 B (手動)**: 打開瀏覽器，訪問 `http://localhost:8069`。
*   **帳號**: `admin` / `admin` (預設)

### 3.2 存取 AI 助理
*   **方式 A (伺服器控制)**: 等待伺服器自動彈出 AI 對話視窗。
*   **方式 B (手動)**: 打開瀏覽器，訪問 `http://localhost:8080`。

### 3.3 檔案同步
本機所有位於 `C:\wuchang V5.1.0` 的檔案變更都會被監測。
*   **您不需要手動上傳檔案**。
*   當伺服器偵測到需要同步時，會自動透過 `8766` 埠進行傳輸。

---

## 4. 故障排除 (Troubleshooting)

### Q1: 伺服器無法連線或無反應？
1.  執行診斷腳本：
    ```powershell
    .\scripts\verify_user_flow.ps1
    ```
2.  檢查輸出結果：
    *   若 **Server Connectivity** 為紅燈：檢查網路線或 VPN。
    *   若 **Services** 為紅燈：重新執行 `start_server_directed_mode.ps1`。

### Q2: 伺服器提示「無法登入 SSH」？
1.  確認 `wuchang` 使用者存在且密碼正確。
2.  確認防火牆已開放 Port 22 (執行 `allow_wuchang_ports.ps1`)。
3.  確認公鑰已正確交換 (參考 `scripts/exchange_ssh_keys.py`)。

### Q3: 畫面沒有自動彈出？
1.  檢查 **UI Control Service** (Port 8765) 是否運行。
2.  確認本機防火牆未阻擋 8765 埠。

---

## 5. 技術支援資訊
*   **本機 IP**: `192.168.50.84`
*   **管理員帳號**: `wuchang`
*   **系統路徑**: `C:\wuchang V5.1.0`
*   **日誌位置**: 查看終端機輸出或 `remote_ui_control/` 下的日誌檔。

---
*五常 AI 系統團隊 敬上*
