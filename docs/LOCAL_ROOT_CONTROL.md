# 本機最高權限控制面板（人性化操作指南）

此面板以「最少步驟、明確回饋、可追責」為設計原則，避免誤操作。

## 介面設計重點

-   清單式選項：數字輸入即可執行；`Q` 離開。
-   必須「系統管理員」執行，否則立即中止並提示。
-   顏色提示：
    -   藍/青色：資訊或啟動
    -   黃色：停止/警告
    -   紅色：權限不足
-   日誌可隨時 Ctrl+C 中止；不會修改金鑰內容。

## 安裝與啟動

1. 以系統管理員開啟 PowerShell。
2. 執行：

```powershell
powershell.exe -NoLogo -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\tools\local_root_control.ps1"
```

3. 建議建立桌面捷徑，目標填入上述命令，捷徑圖示可自選醒目顏色。

## 可用功能（對應選單）

1. 啟動核心服務：`docker-compose up -d`
2. 停止核心服務：`docker-compose down`
3. 查詢 AI 參數：讀取 Odoo `ir.config_parameter`（僅顯示，不修改）
4. 追蹤 Odoo 日誌：`docker logs -f wuchangv510-wuchang-web-1`
5. 追蹤 Caddy 日誌：`docker logs -f wuchangv510-caddy-1`
   Q. 離開

## 常見使用情境

-   想確認「AI 是否走服務帳戶」：選 3 查看 `wuchang.google.project_id` 等參數。
-   想重啟整套服務：先 2 停，再 1 啟。
-   想看流量或錯誤：選 4（Odoo）或 5（Caddy）。

## 風險告警

-   此面板具最高控制權，請只在本機、受信任環境使用。
-   執行需有 Docker / docker-compose，且專案路徑為 `C:\wuchang V5.1.0`。
-   不會觸碰金鑰檔案內容，但仍請確保 `config/gcp/littlej-sa.json` 權限正確。

## 待補強（如需）

-   加入「審計輸出」：執行紀錄寫入本機檔案或 Windows 事件紀錄。
-   加入「二次確認」：對停止/重啟提供 Y/N 確認。
-   GUI 版（WPF/WinForms）：若需圖形按鈕、指示燈、即時狀態，可再告知。
