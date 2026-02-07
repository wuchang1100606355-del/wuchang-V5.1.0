# 社區客製化服務 AI 藍圖（Blueprint）

本藍圖協助協會/里辦公室/非營利組織，以「本地優先、可視可稽核」方式落地 AI 服務。

## 1) 服務對象與情境

-   受眾：長者、身心障礙者、照護者、里民、店家
-   常見情境：申請補助、異常回報（報修/環保）、活動公告、跨語協助（越南語/印尼語/英語）

## 2) 能力模組（Skills）

-   translate：多語翻譯（zh-TW/en/vi/id）
-   summarize_form：條文/計畫書重點摘要
-   compose_announcement：公告草擬（張貼/Line 發送）
-   triage：案件分流（長照/環保/報修/法律/補助）

## 3) 工作流程（Workflows）

-   接待台（POS/資訊站） → 收集需求 → 呼叫技能 → 產生結果 → 印/貼/送
-   客顯螢幕 → 顯示多語說明或公告 → 即時同步
-   後台 → 審核/歸檔 → 事件紀錄（events.log.jsonl）

## 4) 隱私與合規

-   預設本地 LLM（Ollama）優先；可設定 LLM_FALLBACK=0 禁用雲端
-   所有事件記錄至 JSONL，可 CSV 匯出，滿足稽核
-   敏感內容不上雲：在本地僅用模式停用 Vertex AI 備援

## 5) 衡量指標（KPI）

-   回覆時間（P50/P95）
-   一次成功率（無需人工補救）
-   多語案件比例與滿意度
-   補助案件完成率與退件率

## 6) 擴充指引

-   新增技能：在 vm_fastapi_main_new.py 的 skills_registry 註冊新 handler
-   串資料源：在 handler 中讀取內部資料（如 CSV/DB/API）並組合 LLM 提示
-   自動化：透過 /commands/push 同步公告至客顯，或發送到內部 Line Bot（可後續接入）

## 7) 快速測試

-   列出技能：GET /skills
-   執行翻譯：POST /skills/execute { name: "translate", input: { text: "您好", target: "vi" } }
-   執行公告：POST /skills/execute { name: "compose_announcement", input: { title: "里內健康講座", key_points: ["時間：3/10 14:00","免費入場"] } }

---

此藍圖可隨專案成長而細化；若需跨系統整合（Odoo、表單、Line），建議新增對應技能與權限控管。
