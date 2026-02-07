# 本機總控面板 GUI 版（含小 j 對話功能）

## 界面說明

-   左側：系統控制區（啟動/停止/查參數/日誌）
-   右側：AI 對話區（與小 j 即時對話）

## 功能特點

1. **啟動核心** - 執行 docker-compose up -d
2. **停止核心** - 含二次確認，執行 docker-compose down
3. **查 AI 參數** - 顯示當前 AI 路由設定
4. **日誌追蹤** - 新視窗即時追蹤 Odoo/Caddy 日誌
5. **小 j 對話** - 內建 AI 助手，本地優先/雲端備援

## AI 對話能力

-   走 Odoo `wuchang.ai.logic` 模組（已設本地優先）
-   本地 Ollama 正常 → 走本地；失敗 → 自動切 Vertex AI
-   可詢問系統狀態、請求建議、問技術問題
-   對話歷史顯示在右側面板

## 啟動方式

```powershell
# 以系統管理員執行
powershell.exe -NoLogo -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\tools\local_root_control_gui.ps1"
```

## 桌面捷徑設定

1. 右鍵桌面 → 新增 → 捷徑
2. 位置填入：
    ```
    powershell.exe -NoLogo -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\tools\local_root_control_gui.ps1"
    ```
3. 名稱：五常總控 - 小 j
4. 右鍵捷徑 → 內容 → 進階 → 勾選「以系統管理員身分執行」
5. 更換圖示（可選）

## 使用情境

-   日常：右側與小 j 對話，詢問狀態或請求協助
-   維護：左側控制服務啟停、查看參數
-   排錯：開新視窗追蹤日誌，同時問小 j 建議

## 安全設計

-   必須系統管理員執行
-   停止核心需二次確認
-   查參數僅讀取，不修改金鑰
-   對話走 Odoo 模組，遵循本地優先/雲端備援規則

## 技術架構

-   UI: WinForms (System.Windows.Forms)
-   AI: Odoo wuchang.ai.logic 模組
-   路由: 本地 Ollama (192.168.50.1) → Vertex AI (ADC)
-   日誌: docker logs -f（新 PowerShell 視窗）

## 常見問題

Q: 小 j 回應很慢？
A: 可能走雲端 Vertex AI；確認本地 Ollama 是否正常。

Q: 對話顯示錯誤？
A: 檢查容器 wuchang-web 與 db 是否運行，執行「查 AI 參數」確認設定。

Q: 如何改成強制雲端？
A: 在 Odoo 後台或用「查 AI 參數」確認後，將 ai_mode 改為 external_key。
