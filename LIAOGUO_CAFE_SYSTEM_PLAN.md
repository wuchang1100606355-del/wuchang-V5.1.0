# 聊國咖啡智慧化系統綜合規劃書 (Liaoguo Cafe System Master Plan)

## 1. 核心願景 (Vision)
將「聊國咖啡」打造為五常與世界 (Wuchang & World) 的第一個實體智慧節點 (Store Node)。
不僅是咖啡廳，更是「數位人權」、「在地治理」與「自動化營運」的示範場域。
系統設計遵循「五常安全標準 (WSS)」，優先考量韌性、公平與人類優先。

## 2. 系統容器架構 (Container Architecture - The Brain)
本系統採用微服務架構，部署於店內高算力主機 (Windows/Docker Desktop)。

### 2.1 核心服務
*   **Wuchang Core (Odoo)**
    *   **容器名稱**: wuchang-odoo
    *   **職責**: 業務邏輯中樞、ERP、庫存管理、會員系統、訂單處理。
    *   **狀態**: 🟢 Online (Port 8069)
*   **Database (PostgreSQL)**
    *   **容器名稱**: wuchang-db
    *   **職責**: 資料持久化存儲 (Volume Mounted)。
    *   **狀態**: 🟢 Online (Internal)
    *   **備份策略**: 每日自動快照至 Google Drive。

### 2.2 邊緣代理 (Edge Agents)
*   **Store Apprentice (店駐點徒弟)**
    *   **容器/進程**: store_apprentice.py (Python)
    *   **職責**: 
        *   **手 (Hands)**: 透過 ADB 控制 Android POS 點餐機。
        *   **眼 (Eyes)**: 透過 Selenium/Playwright 監控 Web 介面。
        *   **耳 (Ears)**: (規劃中) 藍芽語音接單模組。
    *   **狀態**: 🟢 Online (已連接 POS @ 192.168.50.88:39301)
*   **Preview Server**
    *   **進程**: python -m http.server
    *   **職責**: 前端開發預覽與即時反饋。
    *   **狀態**: 🟢 Online (Port 8000)

## 3. 現地資源配置 (On-site Resources - The Body)

### 3.1 終端設備 (Terminals)
*   **Android POS 機**
    *   **IP**: 192.168.50.88 (Static Lease)
    *   **連接埠**: 39301 (ADB Wireless Debugging)
    *   **角色**: 現場點餐、收銀介面。
    *   **控制權**: 由 Store Apprentice 全權接管。
*   **PC 工作站**
    *   **角色**: 系統主機、開發終端、Docker Host。
    *   **網路**: 雙網卡策略 (LAN 連接設備 / WAN 連接雲端)。

### 3.2 網路架構 (Network Infrastructure)
*   **Subnet**: 192.168.50.x/24
*   **Gateway**: 192.168.50.1 (ASUS Router)
*   **Failover**: 4G USB Tethering (備援線路)。

## 4. 整合邏輯 (Integration Logic)

`mermaid
graph TD
    User[使用者/店員] -->|語音/觸控| POS[Android POS]
    User -->|Web介面| Odoo[Wuchang Core]
    
    subgraph Store_Host [店內主機]
        Odoo <-->|指令/狀態| Apprentice[Store Apprentice]
        Apprentice -->|ADB指令| POS
        Apprentice -->|監控| Browser[Web Commander]
    end
    
    POS -->|訂單資料| Odoo
`

## 5. 當前狀態與行動 (Status & Actions)
*   **✅ 已完成**: 
    *   Odoo 核心啟動。
    *   Store Apprentice 成功連線 POS。
    *   首頁預覽伺服器上線。
*   **⚠️ 待處理**:
    *   **資源衝突**: 清理重複運行的 Store Apprentice 進程。
    *   **Git Repository**: 清理過大歷史檔案 (8.97GB)。
    *   **語音模組**: 整合 Speech-to-Text 服務。

## 6. 結論
系統已具備「大腦 (Odoo)」與「手腳 (Apprentice)」，且已成功與實體世界 (POS) 建立連結。
下一步將強化「自動化腳本」的編寫，讓徒弟能代替人類完成重複性操作。

## 6. 雙核心接手切換機制 (Dual-Core Handover Mechanism)

為因應本機「機動性開機」特性，系統設計了「接手切換」邏輯，確保服務不中斷。

### 6.1 切換邏輯 (Handover Logic)
*   **主要模式 (Primary Mode)**: **本機 (Local)** 優先。
    *   當本機開機且 wuchang-tunnel 連線時，Cloudflare 流量 100% 導向本機 (低延遲)。
*   **接手模式 (Takeover Mode)**: **雲端 (Cloud)** 備援。
    *   當本機關機或斷線 (>30s 無心跳)，Cloudflare 自動將流量切換至雲端實例 (GCP)。
    *   POS 自動重連至雲端 IP/Domain。

### 6.2 資料同步 (Data Synchronization)
*   **上行 (Upstream)**: 本機運行時，Postgres 透過 WAL Shipping 或每 5 分鐘差異備份同步至雲端。
*   **下行 (Downstream)**: 本機開機時，優先從雲端拉取最新交易紀錄 (Catch-up) 後才啟動服務。

### 6.3 執行要求
*   **Cloudflare Load Balancer**: 需在 Cloudflare 後台設定 Origin Pool，將 Local 設為 Priority 1，Cloud 設為 Priority 2。
*   **State Monitor**: store_apprentice.py 需增加「心跳回報」功能，向雲端打卡。
