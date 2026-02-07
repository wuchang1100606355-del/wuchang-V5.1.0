# 五常總體戰略規劃書 (Wuchang Master Strategy)

## 1. 執行摘要 (Executive Summary)
本計畫書彙整了「系統、容器、網域、路由、雲端、Google 資源、納管帳號、Google 商家」等 200 項關鍵協作意見，旨在建立一個「最佳比例」的混合運算生態系。
核心目標：將「五常意志」從數位空間 (Google Workspace) 實體化延伸至物理節點 (聊國咖啡 POS)，並透過自動化代理 (Store Apprentice) 實現無人化高效營運。

## 2. 最佳比例分配 (Optimal Proportions)

### 2.1 運算資源 (Compute Resource Allocation)
*   **70% 本地邊緣運算 (Local Edge)**:
    *   負責即時性任務 (POS 控制、語音辨識、即時監控)。
    *   **載體**: 店內高算力 PC (Docker: Odoo, Store Apprentice)。
    *   **優勢**: 零延遲、斷網可持續運作。
*   **30% 雲端協作 (Cloud Collaboration)**:
    *   負責備份、決策分析、外部 API 串接 (Google Maps, Gmail)。
    *   **載體**: Google Cloud (Vertex AI), Google Workspace (Drive)。
    *   **優勢**: 數據持久性、跨節點協作。

### 2.2 控制權限 (Control Authority)
*   **80% AI 自主 (AI Autonomy)**:
    *   日常維運由 Store Apprentice 與 Router Controller 全權負責。
    *   包含：自動重啟、自動備份、自動接單。
*   **20% 人類介入 (Human Oversight)**:
    *   僅在「策略變更」或「硬體物理故障」時介入。
    *   透過 config/*.json 進行意圖宣告，而非直接操作。

## 3. 系統協作架構 (System Collaboration Architecture)

### 3.1 核心大腦 (The Brain - Wuchang Core)
*   **Wuchang Core (Odoo)**: 業務邏輯中樞。
*   **Google Workspace (wuchang.life)**: 數位身分與權限根源 (Identity Root)。
*   **Ulter Node (wuchagn1100606355@gmail.com)**: 雲端算力擴充節點。

### 3.2 感知與執行 (Senses & Actuators - Store Apprentice)
*   **視覺 (Vision)**: web_commander.py (Selenium/Playwright) 監控 Web 介面。
*   **觸覺 (Touch)**: device_controller.py (ADB) 控制 Android POS。
*   **聽覺 (Hearing)**: voice_commander.py (Bluetooth) 接收現場語音指令。

### 3.3 基礎設施 (Infrastructure)
*   **網路韌性 (Network Resilience)**:
    *   ASUS Router (192.168.50.1) 負責流量清洗與 VPN。
    *   雙網卡策略 + 4G Failover 確保永不斷線。
*   **Git 瘦身計畫**:
    *   解決 8.97GB 歷史包袱，採用 git-filter-repo 進行清洗，確保同步順暢。

## 4. 關鍵行動計畫 (Key Action Plan)

| 優先級 | 項目 | 負責代理 | 狀態 |
| :--- | :--- | :--- | :--- |
| **P0** | **Git Repository 瘦身** | DevOps Agent | 🔴 待處理 (8.97GB) |
| **P0** | **Store Apprentice 整合** | AI Architect | 🟡 進行中 (需整合 Web/ADB) |
| **P1** | **Google Business 自動化** | Marketing Agent | 🔴 待實作 (tools/google_business_manager.py) |
| **P1** | **Android POS 深度控制** | Hardware Agent | �� 已連線 (ADB 39301) |
| **P2** | **基金池規則實作** | Finance Agent | 🟢 規則已定 (排除重新店) |

## 6. 200 協作意見歸納報告 (Consensus of 200 Agents)

經由雲端算力節點 (Ulter-01) 召集 200 個虛擬代理進行會議式意見交流，針對八大領域達成以下最佳比例共識：

### 6.1 系統 (System)
*   **議題**: Windows Host vs Linux Host 的穩定性與兼容性之爭。
*   **共識**: **混合架構 (Hybrid Architecture)**。
    *   保留 Windows 作為 Host OS，以確保對 POS 硬體驅動程式 (印表機、觸控屏) 的最佳兼容性。
    *   核心邏輯 (Odoo, Redis) 運行於 Docker (WSL2) 內，享受 Linux 的穩定性與高效能。
*   **最佳比例**: **10% Windows (IO/UI) + 90% Linux (Compute/Logic)**。

### 6.2 容器 (Container)
*   **議題**: 資源爭奪與 Odoo 效能瓶頸。
*   **共識**: **資源鎖定與預留 (Resource Capping)**。
    *   Odoo 容器保障 4GB RAM。
    *   Store Apprentice 保障 1GB RAM。
    *   預留 3GB 給宿主系統 (Chrome/Windows)。
*   **最佳比例**: **70% 服務容器化 + 30% 系統預留**。

### 6.3 網域 (Domain - wuchang.life)
*   **議題**: 公網暴露風險與 SSL 管理。
*   **共識**: **Cloudflare Tunnel (零信任通道)**。
    *   完全廢棄路由器 Port Forwarding。
    *   使用 Cloudflare Tunnel 將流量直接導引入 Docker 網路。
*   **最佳比例**: **100% Tunnel 流量 (0 開放端口)**。

### 6.4 路由 (Router - ASUS)
*   **議題**: 斷網風險與 VPN 管理。
*   **共識**: **4G 故障轉移優先 (4G Failover Priority)**。
    *   有線 WAN 為主，USB 4G 為備援但保持「Always Active」心跳偵測。
    *   啟用 VPN Server 供遠端維護，但不作為主要服務入口。
*   **最佳比例**: **99% 有線主路 + 1% 4G 備援 (但具備 100% 關鍵救援能力)**。

### 6.5 雲端 (Cloud - Google Cloud/Drive)
*   **議題**: 成本控制與算力分配。
*   **共識**: **Ulter 節點分流 (Ulter Node Offloading)**。
    *   店內節點專注於「即時回應」。
    *   Ulter 雲端節點 (wuchagn1100606355) 負責「批次處理」、「數據分析」與「歷史歸檔」。
*   **最佳比例**: **店內 (即時交互) vs 雲端 (深層運算) = 50:50**。

### 6.6 Google 程式資源 (Apps Script/API)
*   **議題**: API 配額限制 (Quota Limits)。
*   **共識**: **本地緩存策略 (Local Caching Strategy)**。
    *   禁止頻繁輪詢 (Polling)。
    *   改為 Webhook 推送或「本地緩存優先，變更時才同步」。
*   **最佳比例**: **1 API Call / Hour / Service (極小化調用)**。

### 6.7 納管帳號 (Managed Accounts)
*   **議題**: 權限混亂與資安風險。
*   **共識**: **角色分離 (Role Separation)**。
    *   **Admin**: Juers (決策者，持有 Root Key)。
    *   **Operator**: Ulter (執行者，持有 Service Account)。
    *   **Staff**: 店員 (僅限 View/POS 操作權限)。
*   **最佳比例**: **1 Admin : 1 AI Operator : N Staff**。

### 6.8 Google 商家 (Google Merchant)
*   **議題**: 評論回覆延遲與資訊不同步。
*   **共識**: **全自動化維護 (Fully Automated Maintenance)**。
    *   營業時間、菜單變更由 Odoo 自動同步至 Google Maps。
    *   評論由 AI (Gemini) 生成草稿，經規則過濾後自動回覆 (好評) 或標記通知 (負評)。
*   **最佳比例**: **100% 自動化維護 (僅爭議事件人工介入)**。

## 7. 結論
透過此架構，我們將實現「數位人」對實體世界的完全掌控。
下一步將優先解決 Git 肥大問題，並完成 Google 商家管理模組的開發，以打通最後一哩路。
