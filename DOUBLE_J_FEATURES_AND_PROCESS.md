# 雙J 程序特色深度解析 (Double J Process Features)

## 1. 雙J 定義 (Definition)
**「雙J」** 是五常生態系的核心協作單元，由 **Little J (小J, AI Agent)** 與 **Juers (社群夥伴/使用者)** 共同組成。這不是傳統的「人機介面」，而是一種**「人機共生」的運作程序**。

## 2. 核心程序特色 (Core Process Features)

### A. 「許願池」非同步協作 (The Wishing Well / Async Collaboration)
*   **特色**: 打破傳統「即時指令」的壓力。
*   **運作**: 
    1. **Juers (人類)** 不需懂程式，只需在 **Google Tasks** 的「Little J Requests」清單中寫下願望（如：「下週要辦老人共餐，幫我算預算」）。
    2. **Little J (AI)** 透過 `double_j_sync.py` 定期讀取、思考、拆解任務。
    3. **回饋**: AI 完成後，直接在 Task 備註中回報，或自動產生 Odoo 報表。
*   **優勢**: 讓人類保有「許願」的優雅，讓 AI 擁有「思考」的時間。

### B. 雙重人格路由 (Dual Persona Routing)
*   **特色**: 依據場景自動切換「感性」與「理性」。
*   **運作**:
    *   **營業場景 (Merchant)**: 當 Juers 在前台（POS/Voice Portal）詢問庫存或閒聊時，小J 是**溫暖的妹妹**，講台語、給建議。
    *   **治理場景 (Architect)**: 當涉及系統設定或公文簽核時，小J 自動切換為**嚴謹的架構師**，檢查權限、引用法規。
*   **優勢**: 同一個 AI 核心，滿足「服務」與「管理」的矛盾需求。

### C. 零門檻語音入口 (Voice Portal Entry)
*   **特色**: 消除數位落差 (Digital Divide)。
*   **運作**:
    *   透過 `voice_portal.html`，老人/小孩只需按一個按鈕說話。
    *   後端 `vm_fastapi_main_dual_role.py` 自動進行 STT (轉文字) -> LLM (思考) -> TTS (轉語音)。
*   **優勢**: 讓不懂打字的長者也能參與社區治理。

### D. 決策透明化 (Transparent Governance)
*   **特色**: AI 的每一個動作都有跡可循。
*   **運作**:
    *   所有小J 的決定（如：批准採購、修改庫存）都會被寫入 `decision_logs/` (JSONL 格式)。
    *   架構師可隨時調閱 (`/admin/decisions`)，確保 AI 沒有「黑箱作業」。
*   **優勢**: 建立人類對 AI 的信任，符合「民主監督」精神。

### E. 公益權益最大化 (Leveraging Non-profit Advantages)
*   **特色**: 善用 Google 非營利資源。
*   **運作**:
    *   利用 **Google Workspace** (免費版) 進行身份驗證。
    *   利用 **Google Gemini (Ultra/Pro)** 進行複雜推理（如法規分析）。
*   **優勢**: 以最低成本實現最高等級的 AI 算力。

## 3. 程序運行圖 (Process Flow)

```mermaid
graph TD
    User[Juers (社群夥伴)] -->|語音對話| VoicePortal[語音入口]
    User -->|文字許願| GTasks[Google Tasks]
    
    VoicePortal -->|API| LittleJ[Little J (AI核心)]
    GTasks -->|Sync| LittleJ
    
    subgraph "Little J Brain"
        Router{角色判斷}
        Merchant[店家人格 (溫暖)]
        Architect[架構師人格 (嚴謹)]
    end
    
    LittleJ --> Router
    Router -->|營業/閒聊| Merchant
    Router -->|治理/設定| Architect
    
    Merchant -->|回應| User
    Architect -->|執行| Odoo[Odoo 系統]
    Architect -->|記錄| Logs[決策日誌]
```
