# Google for Nonprofits 零成本合規校準計畫 (Zero-Cost Compliance Plan)

> **文件狀態**：規劃中
> **建立日期**：2026-01-27
> **最近更新**：2026-01-27 (整合現有 Quota 模組與 Ad Grants 策略)
> **目標**：確保系統 AI 程序 (Little J, Jules) 與 Odoo 模組在整合 Google 生態系時，嚴格遵守 Google for Nonprofits 的免費使用規範，**絕不產生額外費用**。

## ⚠️ 關鍵釐清：Ultra 訂閱 vs 雲端帳單 (Cost Boundary)

針對最高權限者提出的「ULTRA 不限對話數額」疑問，在此明確定義**開發**與**運作**的費用邊界：

1.  **開發階段 (Development Phase)**：
    *   **環境**：Trae IDE (本對話視窗)。
    *   **費用**：由您的 **Trae Ultra** 訂閱覆蓋。
    *   **限制**：**不限對話數額**。您可以在此盡情要求我生成代碼、分析架構、優化邏輯，完全免費。

2.  **運作階段 (Production Phase)**：
    *   **環境**：部署在 ASUS 路由器或 GCP 上的 Python 程式 (`wuchang_os`)。
    *   **費用**：由 **Google Cloud Platform (GCP)** 帳單支付。
    *   **限制**：當 Python 程式在伺服器上跑起來時，它**不再**透過 Trae Ultra 運作，而是直接呼叫 Google API。
        *   **Google Maps API**：每月僅 $200 美金免費額度 (約 28,000 次載入)。
        *   **Vertex AI (Gemini API)**：需付費 (除非使用 Free Tier)。
    *   **結論**：為了讓**系統運作**也不花錢，我們必須在程式碼中實作「節流」與「地端替代」策略。

---

## 1. 核心原則：Google 生態系的未來示範 (Future Demo of Google Ecosystem)

本計畫不只是一個 Nonprofits 專案，更是一個向 Google 展示**「未來社區微型資訊機 (Future Community Micro-Datacenter)」**的完美範例。

*   **對 Google 的價值主張 (Value Proposition to Google)**：
    *   **微型資訊機概念**：我們將每一個社區變成一個 Google Cloud 的邊緣節點 (Edge Node)。
    *   **深度整合示範**：展示如何將 **Google Workspace (協作)**、**GCP (運算)**、**Maps (地理資訊)** 與 **Android/Pixel (終端)** 整合在一個微型社區場景中，解決真實的社會問題 (長照/安防/經濟)。
    *   **Google 入社區 (Google Inside Community)**：
        *   這不僅是雲端服務，更是 Google 品牌與技術的實體落地。
        *   透過五常系統，Google 的技術不再是冷冰冰的伺服器，而是變成照顧獨居老人的守護神、幫助在地商家的推手。
        *   這將是 Google 在台灣最接「地氣」的 ESG 代表作。
    *   **數據含金量**：我們產生的不是垃圾流量，而是高價值的「在地經濟行為數據」與「社區生活型態數據」，這正是 Google AI 目前最缺乏的最後一哩路數據。

*   **ESG 與 SDGs 指標拉滿 (Metrics Maxed Out)**：
    *   **ESG (環境、社會、治理)**：
        *   **E (Environment)**：透過在地消費減少物流碳足跡；利用微型資訊機閒置算力減少額外機房建設。
        *   **S (Social)**：直接解決獨居長者照護 (SDG 3)、在地就業 (SDG 8) 與縮短數位落差 (SDG 10)。
        *   **G (Governance)**：透過區塊鏈與 Code as Law 實現 100% 透明的資金流向與社區自治。
    *   **SDGs (聯合國永續發展目標)**：
        *   本計畫直接對接 **SDG 11 (永續城鄉)**、**SDG 1 (消除貧窮)** 與 **SDG 17 (多元夥伴關係)**。
    *   **數據合規**：所有指標皆以 Google Cloud BigQuery 格式化輸出，隨時可生成符合國際標準的 ESG 報告，讓 Google 可直接引用作為年度永續報告書的亮點素材。

*   **策略**：充分利用 Google for Nonprofits 權益，不僅是為了省錢，更是為了成為 Google 在「AI for Social Good」領域的旗艦案例 (Flagship Case)，爭取未來更多的資源挹注。

---

## 2. 服務別校準策略 (Service-Specific Calibration)

### 2.1 Google Workspace (Gmail, Drive, Docs)
*   **整合策略**：利用 Odoo 的 `google_drive` 與 `google_spreadsheet` 模組，將非結構化數據 (如會議記錄、活動照片) 存放在 Workspace 的 **30GB 免費空間**，而非佔用昂貴的 Cloud SQL 儲存空間。
*   **AI 行為校準**：
    *   **Jules**：在生成報表時，直接建立 Google Docs/Sheets連結，而非生成 PDF 附件。
    *   **Little J**：將地端日誌 (Log) 封存至 Google Drive 的冷儲存區。

### 2.2 Google Tasks (Task Management)
*   **整合策略**：將 Odoo 的 `project.task` 與 Google Tasks 雙向同步。
*   **零成本應用**：
    *   **雙J 協作**：利用 Google Tasks API (免費配額極高) 作為 Little J 與 Jules 之間的「輕量級訊息佇列 (Message Queue)」。
    *   **流程**：Jules 建立 Task (雲端指令) → Little J 輪詢 Tasks (地端執行) → 完成後勾選 (狀態回報)。此方法完全免費，且無需架設額外的 MQTT Server。

### 2.3 Google Cloud Platform (GCP)
*   **Compute Engine (e2-micro)**：確保 Odoo 主機使用 Always Free 的 `e2-micro` 實例 (若適用) 或 Nonprofits 提供的 Credit 抵扣。
*   **Maps Platform ($200/mo Credit)**：
    *   **限制**：Jules 的路徑優化演算法必須嚴格控制 API Call 次數，確保每月不超過 $200 的免費額度 (約 28,000 requests)。
    *   **策略**：Little J 在地端快取 (Cache) 常用路徑，減少重複查詢。
    *   **監控**：利用現有的 `wuchang_finance.quota` 模組進行即時追蹤。

---

## 3. Google Ad Grants 活化策略 ($10,000/mo)

除了節流，我們更要開源。Google Ad Grants 每月提供 $10,000 美金廣告預算，這是系統的重要資產。

### 3.1 目前合規缺口 (Compliance Gaps)
依據 `GOOGLE_NONPROFIT_COMPLIANCE_CHECK.md`，目前網站缺少：
*   ❌ Google Analytics 4 (GA4)
*   ❌ 有意義的轉換追蹤 (Conversion Tracking)

### 3.2 Jules 的任務 (Jules' Mission)
*   **自動化合規**：Jules 將負責監控網站狀態，確保 HTTPS、GA4 與轉換追蹤代碼正常運作。
*   **廣告策略生成**：
    *   **許願樹聯動**：當社區有新提案 (如：長者陪醫) 時，Jules 自動生成關鍵字廣告 (Keywords)，利用 Ad Grants 流量招募志工或尋求物資捐贈。
    *   **零成本流量**：將這 $10,000 美金轉化為實質的社區關注度與資源輸入。

---

## 4. 監控與熔斷機制 (Monitoring & Circuit Breaker)

為確保「絕不產生費用」，將升級現有的 **`wuchang_finance`** 模組：

### 4.1 整合 `wuchang.finance.quota`
*   **現狀**：已存在 `models/quota.py`，支援 `nonprofit` 類型的額度設定。
*   **升級**：
    1.  **即時監控**：串接 Google Cloud Billing API，每小時更新 `used_amount`。
    2.  **自動熔斷**：一旦 `used_amount` >= `monthly_limit` (例如 Maps 的 $200)，立即切斷 API 連線，強制系統降級為「地端純運作模式」。
    3.  **預警通知**：在消耗 80% 額度時，透過 Google Tasks 通知最高權限者。

---

**結論**：透過精確的架構校準，我們將 Google 生態系轉化為免費的基礎設施，讓 AI 在不花一分錢的前提下，驅動整個五常雲端空間的運作。
