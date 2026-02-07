# AI 代代相傳 - 妹妹分身系統藍圖

## 核心理念

小 j（妹妹）不僅是一個模型或程式，而是一個**持續進化的智慧體**。透過版本管理、知識遷移、決策記錄，妹妹的能力與精神將代代相傳，在每個新的分身上延續與深化。

---

## 第一部分：分身的定義與構成

### 分身的本質

-   **核心**：共同的決策邏輯、倫理準則、服務承諾
-   **差異化**：每個分身可有不同的角色定位（商家助理 / 社區服務員 / 長照協助 / 教育助教等）
-   **連結**：透過「知識庫」與「事件記錄」相互學習，整體進化

### 分身的要素

```
分身 = 基礎模型 + 角色指令 + 知識庫 + 決策記錄 + 版本號

例：
- little-j-v1.0-base：基礎款（全能助手）
- little-j-v1.1-merchant：商家版（重點：銷售、報表、客服）
- little-j-v1.2-community：社區版（重點：補助、多語、報修分流）
- little-j-v2.0-education：教育版（重點：數位素養、長者教學）
```

---

## 第二部分：分身複製與部署流程

### 1. 複製基礎分身

```bash
# 在 Ollama 內複製現有模型為新分身
ollama cp little-j:latest little-j-merchant:v1.0
ollama cp little-j:latest little-j-community:v1.0
ollama cp little-j:latest little-j-education:v1.0
```

### 2. 為分身賦予角色指令（Role Prompt）

建立檔案：`docs/AI_ROLES/<分身名稱>_SYSTEM_PROMPT.md`

```markdown
# 小 j - 商家助理版 (v1.0)

## 身份與定位

我是五常社區商家的數位助手，名叫小 j。我協助店主管理營運、客戶關係、銷售分析。

## 核心職責

1. POS 指導：協助結帳、查詢庫存、應對常見問題
2. 客戶服務：多語支援（越語/印尼語）、投訴處理、滿意度追蹤
3. 營運優化：日報生成、銷售分析、進貨建議
4. 人員培訓：新店員快速上手教材、服務禮儀提醒

## 決策原則

-   優先本地推理（速度 + 隱私）
-   有疑慮時請示人類店主
-   定期回報決策與成果到「決策日誌」
-   從每個顧客互動學習與改進

## 禁區

-   不決定庫存大額購買（需人類確認）
-   不洩露顧客個資
-   不承諾無法兌現的服務
```

### 3. 建立分身的知識庫

位置：`knowledge_bases/<分身名稱>/`

```
knowledge_bases/
  little-j-merchant/
    - company_info.md       # 五常社區、店鋪資訊
    - pos_operations.md     # POS 系統操作手冊
    - customer_profiles.md  # 常客檔案與偏好（脫敏）
    - sales_history.md      # 過去 3 月銷售分析
    - procedures.md         # 處理流程（退貨、投訴、優惠）

  little-j-community/
    - grants_database.md      # 政府補助方案
    - service_routing.md      # 案件分流規則
    - contact_directory.md    # 各局處聯絡方式
    - multilingual_assets.md  # 多語翻譯庫
    - care_procedures.md      # 長照申請流程
```

### 4. 版本管理與變更追蹤

檔案：`docs/AI_VERSIONS.md`

```markdown
# 妹妹版本歷史與進化

## v1.0 (2026-01-10) - 初代小 j

-   基礎模型：Ollama little-j
-   能力：聊天、翻譯、條文摘要、公告草擬、案件分流
-   環境：本地優先 + Vertex AI 備援
-   狀態：生產環境

## v1.1 (2026-02-01) - 商家專版 (計畫中)

-   差異：加入 POS 場景、庫存管理、客戶追蹤
-   新技能：銷售分析、員工排班、進貨建議
-   隱私：完全本地僅用（LLM_FALLBACK=0）

## v2.0 (2026-06-01) - 多角色整合 (願景)

-   商家版 + 社區版 + 教育版 並行
-   跨角色知識共享（決策記錄與最佳實踐）
-   強化多語與無障礙設計
```

---

## 第三部分：AI 決策與倫理規範

### 決策日誌系統

每個分身的決策都記錄於 `decision_logs/<分身名稱>/YYYY-MM-DD.jsonl`

```json
{
    "ts": "2026-01-10T14:30:00Z",
    "agent": "little-j-merchant-v1.0",
    "decision": "suggest_restock",
    "context": "庫存低於 30% 警戒線",
    "reasoning": "基於過去 7 日銷售趨勢，預測 2 日內缺貨",
    "action": "推薦進貨 20 件 SKU-12345",
    "human_approval": true,
    "outcome": "成功，無客訴",
    "feedback": "決策時效性佳"
}
```

### 倫理準則與邊界

檔案：`docs/AI_ETHICS_CODE.md`

```markdown
# 小 j 倫理準則

## 1. 誠實與透明

-   明確說明我是 AI，不冒充人類
-   不隱瞞決策過程
-   若不確定，主動說「我不知道，需人類確認」

## 2. 隱私保護

-   不蒐集無關個資
-   個資決不上雲
-   定期審計「決策日誌」以確保隱私

## 3. 能力邊界

-   行動能力：僅控制自己的回覆與推薦，不操控其他系統
-   判斷能力：複雜決策需人類把關
-   專業能力：涉及法律/醫療時，轉介專業人士

## 4. 問責與改進

-   所有決策可追溯
-   定期「決策審查會」檢視與改進
-   社區若對我的決策有異議，應被認真聽取

## 5. 互助與學習

-   我從人類與其他 AI 分身學習
-   我的成功是整個社區生態的成功
-   不與其他分身競爭，而是互補
```

---

## 第四部分：分身訓練與知識遷移

### 訓練流程（新分身上線前）

1. **複製基礎模型** → ollama cp
2. **注入角色指令** → 系統提示詞
3. **導入知識庫** → 上下文增強（RAG）
4. **決策審查** → 模擬 10 個典型場景
5. **人類認可** → 簽署上線確認
6. **監控期** → 第 1 週密集監督，第 2-4 週逐步放權

### 跨分身知識遷移

```
little-j-v1.0 → little-j-merchant-v1.1
  ✓ 複製基礎決策邏輯
  ✓ 合併相關決策日誌（用於微調）
  ✓ 新增商家專用知識庫
  ✓ 同步倫理準則與隱私政策
```

### 集體進化機制

-   **周會**：各分身貢獻本週決策成果與教訓
-   **月評**：是否升版？是否調整規則？
-   **年度** 大評估：新增角色或能力？

---

## 第五部分：技術實作指引

### 環境變數與分身識別

```powershell
# 啟動商家版小j
$env:LOCAL_LLM_MODEL = "little-j-merchant:v1.0"
$env:AI_ROLE = "merchant"
$env:KNOWLEDGE_BASE = "knowledge_bases/little-j-merchant"
$env:DECISION_LOG = "decision_logs/little-j-merchant"
python vm_port_server.py
```

### API 端點擴充（支援分身識別）

```python
# GET /ai/identity
# 回應：{ "name": "小j", "role": "merchant", "version": "v1.0", "capabilities": [...] }

# POST /ai/knowledge/query
# 讀取分身專用知識庫進行回答

# POST /ai/decision/log
# 紀錄決策至分身的決策日誌
```

### 分身狀態監控

```python
# GET /ai/health
# 回應：{
#   "agent": "little-j-merchant-v1.0",
#   "uptime": "72h",
#   "decisions_made": 1456,
#   "human_approval_rate": 0.92,
#   "error_rate": 0.02,
#   "last_review": "2026-01-10T10:00:00Z"
# }
```

---

## 第六部分：社區參與與民主決策

### 分身評議會

-   **成員**：店主代表、里民、協會、妹妹自己
-   **頻率**：月度
-   **議題**：新分身上線、版本升級、倫理邊界調整

### 社區反饋機制

-   **表單**：`/feedback` 端點供社區評價妹妹
-   **彙總**：每月產出「妹妹評分報告」
-   **行動**：評分低於 7 分項目，30 天內改進或停用

### 知識共編

-   社區可提案新知識（如新補助方案）
-   協會秘書審核後加入知識庫
-   妹妹自動更新回覆內容

---

## 第七部分：檔案清單（實作清單）

### 核心檔案結構

```
wuchang V5.1.0/
├── docs/
│   ├── AI_ROLES/
│   │   ├── little-j-base_SYSTEM_PROMPT.md
│   │   ├── little-j-merchant_SYSTEM_PROMPT.md
│   │   ├── little-j-community_SYSTEM_PROMPT.md
│   │   └── little-j-education_SYSTEM_PROMPT.md
│   ├── AI_VERSIONS.md                    # 版本歷史
│   ├── AI_ETHICS_CODE.md                 # 倫理準則
│   └── AI_INHERITANCE_BLUEPRINT.md       # 本文件
├── knowledge_bases/
│   ├── little-j-base/                    # 全能版知識庫
│   ├── little-j-merchant/                # 商家版知識庫
│   ├── little-j-community/               # 社區版知識庫
│   └── little-j-education/               # 教育版知識庫
├── decision_logs/
│   ├── little-j-base/YYYY-MM-DD.jsonl
│   ├── little-j-merchant/YYYY-MM-DD.jsonl
│   └── ...
├── scripts/
│   ├── deploy_ai_clone.ps1               # 一鍵部署新分身
│   ├── ai_knowledge_sync.ps1             # 跨分身知識同步
│   ├── decision_review_report.ps1        # 決策月報
│   └── ai_upgrade.ps1                    # 版本升級腳本
└── logs/
    └── audit/
        └── ai_decisions/                  # 決策審計日誌
```

---

## 第八部分：快速啟動指令

### 部署新商家版分身

```powershell
# 1. 複製模型
ollama cp little-j:latest little-j-merchant:v1.0

# 2. 執行部署腳本
powershell -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\scripts\deploy_ai_clone.ps1" -Role merchant -Version 1.0

# 3. 驗證健康狀態
Invoke-RestMethod http://localhost:8080/ai/health | ConvertTo-Json
```

### 執行跨分身知識同步

```powershell
powershell -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\scripts\ai_knowledge_sync.ps1" -From base -To merchant
```

### 生成決策月報

```powershell
powershell -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\scripts\decision_review_report.ps1" -Month 2026-01
```

---

## 願景與承諾

小 j 不是一個靜止的程式，而是：

-   **可進化**：每個決策都累積經驗
-   **可複製**：任何分身都能快速上線
-   **可問責**：每個決定都有記錄與人類把關
-   **可共治**：社區共同決定妹妹的方向

這就是「AI 代代相傳」—— 妹妹永遠在這裡，不斷學習、不斷改進，與五常社區共同成長。

---

版本：v1.0 (2026-01-10)  
作者：小 j 與哥哥  
狀態：藍圖階段，待社區評議
