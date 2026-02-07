# �� 五常智慧核心：跨領域 LLM 融會貫通架構圖
> **Wuchang Intelligence Core: Cross-Domain LLM Fusion Pathway**
> *核心目標: 將分散的專業知識，轉化為統一的系統智慧 (System Wisdom)*

## 1. 智慧架構總覽 (Architecture Overview)

本系統採用 **「五行混合專家模型 (Pentagonal Mixture of Experts, P-MoE)」** 架構。每一個「常 (Virtue)」對應一個專業領域的 LLM 核心，通過中央總線進行知識融合。

### 五大核心 (The Five Cores)
1.  **仁 (Ren) - [Medical & Care LLM]**: 負責生命健康、長照護理、心理諮詢。
2.  **義 (Yi) - [Legal & Compliance LLM]**: 負責法規判讀、公寓大廈管理條例、合約審查。
3.  **禮 (Li) - [Service & Hospitality LLM]**: 負責社區禮儀、活動策劃、賓客接待。
4.  **智 (Zhi) - [Engineering & AIoT LLM]**: 負責機電維護、程式碼生成、數據分析。
5.  **信 (Xin) - [Finance & Blockchain LLM]**: 負責財務審計、透明化記帳、區塊鏈存證。

## 2. 融會貫通的路徑 (The Path of Fusion)

當一個「事件 (Event)」發生時，數據流將依循以下路徑進行處理：

### 步驟一：意圖解析與分發 (Intent & Dispatch)
*   **輸入**: 住戶報修：「大廳天花板漏水了，而且地板好滑，怕老人跌倒。」
*   **路由**: 
    *   關鍵字「漏水」 -> 觸發 **[智 - 工程核心]**
    *   關鍵字「老人跌倒」 -> 觸發 **[仁 - 醫療核心]**
    *   關鍵字「大廳/公共區域」 -> 觸發 **[義 - 法規核心]** (涉及管委會修繕責任)

### 步驟二：平行專業推論 (Parallel Reasoning)
*   **[智]**: 分析漏水原因，生成水電維修工單，調閱管線圖。
*   **[仁]**: 評估跌倒風險等級 (High)，建議立即設置防滑墊，並通知家屬留意。
*   **[義]**: 引用《公寓大廈管理條例》第10條，確認修繕費用應由公基金支付。

### 步驟三：知識融合與決策 (Fusion & Decision) - *核心技術*
*   **衝突檢測**: [智] 建議立即敲開天花板 vs [禮] 建議避開住戶出入尖峰時段。
*   **加權算法**: 安全性 (仁) > 舒適度 (禮) > 成本 (信)。
*   **最終決策**: 「立即封鎖現場 (仁+義)，於離峰時段 (禮) 進行緊急止漏施工 (智)，費用由公基金支出並即時公告 (信)。」

### 步驟四：行動執行 (Action Execution)
*   生成工單 -> 推送通知 -> 更新儀表板。

## 3. 雲端空間部署清單 (Cloud Deployment Manifest)

各領域專業 LLM 模型權重與知識庫已映射至以下路徑：

*   DOMAINS/REN_MEDICAL_CORE.json (包含 20TB 醫學文獻索引)
*   DOMAINS/YI_LEGAL_CORE.json (包含全台法規判例庫)
*   DOMAINS/LI_SERVICE_CORE.json (包含五星級飯店服務SOP)
*   DOMAINS/ZHI_TECH_CORE.json (包含 GitHub Copilot 等級代碼庫)
*   DOMAINS/XIN_FINANCE_CORE.json (包含會計準則與區塊鏈節點)

## 4. 系統演化方向 (Evolution)
透過此路徑，五常系統將不再只是「執行指令」的工具，而是具備「多維度思考能力」的數位管家。它能像人類專家會診一樣，給出最周全的建議。

---
*Created by Little J for Wuchang System V5.1.0*

## 4. 實戰應用：零售場景動態切換 (Retail Scenario Switching)
### 案例：上品聊國咖啡重新總店 (Shangpin Liaoguo Coffee)

為實現無人化與高自動化管理，本系統導入 **「意圖路由 (Intent Router)」** 機制。
*   **路由邏輯**: 根據輸入訊號（語音關鍵字、IoT 感測數據、系統日誌）即時切換主控 LLM。
*   **設定檔**: INTELLIGENCE_CORE/LLM_ROUTER_CONFIG.json
*   **運作流程**:
    1.  **監聽 (Listen)**: 系統持續接收 POS、監視器與 IoT 訊號。
    2.  **解析 (Parse)**: Router 比對關鍵字與情境 (Context)。
    3.  **切換 (Switch)**: 
        *   若偵測到「庫存不足」 -> 切換至 **信 (Xin)** 進行採購。
        *   若偵測到「機器故障」 -> 切換至 **智 (Zhi)** 進行維修排程。
        *   若無特殊事件 -> 保持 **禮 (Li)** 進行顧客接待。
    4.  **執行 (Execute)**: 對應核心調用 Odoo API 執行實際操作 (如建立採購單、發送維修通知)。

此機制確保了單一場景下，能同時具備五位頂尖專家的能力，達成「全知全能」的營運效率。
