# 聊國咖啡總店 - Chrome OS 客顯終端連線指引 (Kiosk Guide)

## 🌌 空間哲學 (Space Philosophy)
本指南基於「路由器即時空邊界」之架構設計。
- **邊界 (Boundary)**: 聊國咖啡總店路由器 (Router)。
- **入口 (Portal)**: Chrome OS 客顯螢幕。
- **核心 (Heart)**: Windows Server 上的 Docker 容器。

當您將客顯連上店內 WiFi，您即已進入「聊國量子時空」。請以「回家」的心情操作此入口。

## 🚀 連線步驟 (Connection Steps)

### 1. 網路確認 (Network Check)
- 確保 Chrome OS 裝置已連線至總店路由器 (WiFi 或有線)。
- 確保 Windows Server (主機) 也是連線於同一路由器之下。

### 2. 設定首頁 (Set Homepage)
- 開啟 Chrome 瀏覽器。
- 在網址列輸入主機 IP 位址與連接埠：
  ```
  http://<主機IP>:5001
  ```
  (例如: `http://192.168.1.100:5001`)
- 若連線成功，您將看到「👋 歡迎回家」入口頁面。

### 3. Kiosk 模式 (Kiosk Mode - Optional)
- 若要作為專用客顯，建議將上述網址設為「啟動時開啟的網頁」。
- 或使用 Chrome OS 的 Kiosk 模式鎖定於此網址。

## ⚠️ 注意事項
- 本終端機**不需安裝**任何容器程式。
- 運算與資料皆在後端容器 (Server) 處理。
- 請保持網路暢通以維持時空連結。


## 📡 來賓網路公告設定 (Guest Network Announcement)
若您的路由器支援 Captive Portal (強制登入頁面/來賓歡迎頁面)：
1. 設定路由器將來賓網路 (Guest WiFi) 的登入頁面導向至主機 IP (`http://<主機IP>:5001`)。
2. 當任何裝置連上來賓網路時，將自動彈出「量子時空公告」頁面。
3. 此即達成「由路由器公告並投射時空場域」之效果。

