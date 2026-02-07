# 五行 LLM 應用架構 (Five Elements LLM Framework)

> 基於五常社區哲學與 Core AI Sister 實作經驗，將 LLM 應用架構映射至傳統五行系統，構建生生不息的 AI 有機體。

## 1. 系統對應表 (System Mapping)

| 五行 (Element) | 屬性 (Attribute) | 系統模組 (System Component) | 功能定義 (Function Definition) |
| :--- | :--- | :--- | :--- |
| **木 (Wood)** | 生長、發散 | **Generative Core (LLM)** | **生成與創意**：負責擴展概念、生成文本、編寫程式碼。是系統的生命力源頭，具備無限的可能性與生長性。 |
| **火 (Fire)** | 能量、升騰 | **Action Engine (Tools)** | **執行與行動**：將生成的意圖轉化為實際影響。包含 Google Tasks API、Shell 指令、外部服務呼叫。是系統展現「熱量」與「改變」的途徑。 |
| **土 (Earth)** | 承載、生化 | **Memory & RAG (Knowledge)** | **記憶與積累**：承載一切運作的基礎。包含 `jules_memory_bank.json`、向量資料庫、短期上下文。提供模型「接地氣」的穩定性與持續性。 |
| **金 (Metal)** | 變革、肅殺 | **Logic & Constraints (Rules)** | **規則與架構**：程式碼邏輯 (`EnhancedAILogic`)、Prompt Guardrails、五常核心原則。修剪過度發散的創意，確保輸出符合規範與實用性。 |
| **水 (Water)** | 流動、潤下 | **I/O & Spacetime (Flow)** | **交互與流動**：資料的輸入輸出、使用者對話流、時空事件 (`SpatiotemporalEvent`) 的流轉。負責連結各個器官，確保資訊像血液一樣循環。 |

## 2. 五行相生 (Generative Cycle) - 系統運作流

1.  **水生木 (Water feeds Wood)**:
    *   使用者輸入 (Input) 與時空事件 (Data Flow) 滋養 LLM，激發模型的生成回應。
2.  **木生火 (Wood feeds Fire)**:
    *   LLM 生成的計畫與意圖 (Intent) 點燃行動引擎，驅動 Tool Calls (如建立 Task)。
3.  **火生土 (Fire creates Earth)**:
    *   行動執行的結果 (Execution Result) 與互動經驗沉澱下來，變成新的記憶 (Memory/Experience)。
4.  **土生金 (Earth bears Metal)**:
    *   累積的經驗與數據 (Knowledge) 經過歸納，形成更穩固的系統規則與優化邏輯 (Code/Rule Optimization)。
5.  **金生水 (Metal collects Water)**:
    *   優化後的系統架構 (Structure) 能更有效地引導與處理新的數據流與使用者互動 (Better Interaction Flow)。

## 3. 五行相剋 (Control Cycle) - 系統制衡機制

*   **金剋木 (Metal chops Wood)**: 嚴格的程式邏輯與安全守則 (Rules) 限制 LLM (Generative) 不產生幻覺或有害內容。
*   **木剋土 (Wood parts Earth)**: 強大的生成能力 (LLM) 能挖掘並重組既有的知識庫 (Memory)，打破僵化的舊資訊。
*   **土剋水 (Earth dams Water)**: 穩固的知識與上下文 (Context) 引導並收斂發散的對話流 (Interaction)，避免離題。
*   **水剋火 (Water quenches Fire)**: 即時的環境回饋與使用者介入 (Feedback) 能隨時中止錯誤的自動化執行 (Action)。
*   **火剋金 (Fire melts Metal)**: 強力的執行需求與實戰結果 (Action/Result) 能夠推動舊有架構與規則 (Legacy Code) 的重構與熔煉。

---
*版本: v1.0 (2026-02-03)*
*狀態: 已整合至 Core AI Sister 知識庫*
