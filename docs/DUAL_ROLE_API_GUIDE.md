# 五常 POS 系統 - 雙角色小 j 使用指南

## 快速開始

### 1. 啟動伺服器

```powershell
# 方式 1：使用新的雙角色伺服器
cd "C:\wuchang V5.1.0"
$env:LOCAL_LLM_ENDPOINT="http://127.0.0.1:11434/v1/chat/completions"
$env:LOCAL_LLM_MODEL="little-j"
$env:LLM_FALLBACK="1"
python -m uvicorn vm_fastapi_main_dual_role:app --host 0.0.0.0 --port 8080

# 或使用舊版（相容性）
python -m uvicorn vm_fastapi_main_new:app --host 0.0.0.0 --port 8080
```

### 2. 確認伺服器運行

```bash
curl http://localhost:8080/
# 應回傳：
# {
#   "system": "Wuchang 雙角色小j",
#   "version": "2.0",
#   "status": "Active"
# }
```

### 3. 開啟儀表板

```
http://localhost:8080/dashboard
```

---

## 身份驗證與 Token

所有 API 呼叫需提供 `X-Auth-Token` 標頭：

```bash
curl -H "X-Auth-Token: merchant-demo-001" http://localhost:8080/llm/chat \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "今天營業額多少？"}'
```

### 可用的預設 Token

| Token                | 角色               | 權限                       |
| -------------------- | ------------------ | -------------------------- |
| `merchant-demo-001`  | 店家 (MERCHANT)    | POS 營業、查詢、報表       |
| `merchant-demo-002`  | 店家 (MERCHANT)    | 支門市店家                 |
| `architect-demo-001` | 架構師 (ARCHITECT) | 全系統存取、決策日誌、配置 |

---

## API 端點詳解

### 🗣️ 語音交互

#### POST /voice/recognize

**功能**：上傳語音檔，轉換為文字

**範例（店家角色）**

```bash
curl -F "file=@voice.wav" \
  -H "X-Auth-Token: merchant-demo-001" \
  http://localhost:8080/voice/recognize
```

**回傳**

```json
{
    "text": "今天營業額多少？",
    "confidence": 0.85,
    "language": "zh-TW",
    "timestamp": "2026-01-10T12:00:00"
}
```

#### POST /voice/synthesize

**功能**：將文字轉成語音（MP3）

**範例**

```bash
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  "http://localhost:8080/voice/synthesize?text=今日營業額五千元" \
  -o response.mp3
```

#### POST /voice/command

**功能**：完整語音流程（語音輸入 → LLM → 語音輸出）

**範例（店家語音查詢）**

```bash
curl -F "file=@question.wav" \
  -H "X-Auth-Token: merchant-demo-001" \
  http://localhost:8080/voice/command \
  -o answer.mp3

# 播放回應
# Windows: start answer.mp3
# macOS: open answer.mp3
# Linux: ffplay answer.mp3
```

### 💬 智慧對話

#### POST /llm/chat

**功能**：與小 j 對話（支援角色特定提示詞）

**範例（店家 - 營業查詢）**

```bash
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "A 產品剩多少？", "context": {"product_id": "A001"}}' \
  http://localhost:8080/llm/chat
```

**回傳**

```json
{
    "response": "A 產品目前庫存 45 件。上週銷售 12 件，預計本週售完建議進貨。",
    "source": "local",
    "role": "MERCHANT",
    "timestamp": "2026-01-10T12:00:00"
}
```

**範例（架構師 - 系統設計）**

```bash
curl -X POST \
  -H "X-Auth-Token: architect-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "設計一個新的社區補助審批流程", "context": {"service": "subsidy_approval"}}' \
  http://localhost:8080/llm/chat
```

**回傳**

```json
{
    "response": "建議的社區補助審批流程：...",
    "source": "local",
    "role": "ARCHITECT",
    "timestamp": "2026-01-10T12:00:00"
}
```

### 📊 決策日誌（架構師限定）

#### GET /admin/decisions

**功能**：查看所有決策記錄

```bash
curl -H "X-Auth-Token: architect-demo-001" \
  http://localhost:8080/admin/decisions?role_filter=MERCHANT
```

**回傳**

```json
{
    "decisions_count": 125,
    "decisions": [
        {
            "timestamp": "2026-01-10T12:00:00",
            "decision_id": "uuid-...",
            "user_role": "MERCHANT",
            "user_name": "五常社區 - 主門市",
            "action": "llm_chat",
            "payload": { "message": "A 產品剩多少？" },
            "result": { "response": "...", "source": "local" },
            "status": "recorded"
        }
    ]
}
```

#### GET /admin/audit

**功能**：完整審計報告

```bash
curl -H "X-Auth-Token: architect-demo-001" \
  http://localhost:8080/admin/audit
```

**回傳**

```json
{
    "audit_timestamp": "2026-01-10T12:00:00",
    "total_decisions": 125,
    "decisions_by_role": {
        "MERCHANT": 100,
        "ARCHITECT": 25
    },
    "decisions_by_action": {
        "llm_chat": 80,
        "voice_recognize": 30,
        "voice_synthesize": 15
    },
    "devices_count": 5,
    "events_logged": 342
}
```

### 📱 裝置管理

#### GET /devices

```bash
curl -H "X-Auth-Token: merchant-demo-001" \
  http://localhost:8080/devices
```

#### POST /devices/register

```bash
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "device_type=POS&hostname=pos-001&ip=192.168.50.100" \
  http://localhost:8080/devices/register
```

### 🎯 儀表板

```
http://localhost:8080/dashboard
```

---

## 店家角色（MERCHANT）使用場景

### 場景 1：查詢庫存

```bash
# 語音查詢
curl -F "file=@q1.wav" \
  -H "X-Auth-Token: merchant-demo-001" \
  http://localhost:8080/voice/command -o answer.mp3

# 文字查詢
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "B 產品還有多少？"}' \
  http://localhost:8080/llm/chat
```

### 場景 2：客人應收帳款

```bash
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "王先生還欠多少錢？"}' \
  http://localhost:8080/llm/chat
```

### 場景 3：推薦搭售

```bash
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "這位客人適合推薦什麼？"}' \
  http://localhost:8080/llm/chat
```

### 場景 4：營運報告

```bash
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "產生今日營運報告"}' \
  http://localhost:8080/llm/chat
```

---

## 架構師角色（ARCHITECT）使用場景

### 場景 1：決策分析

```bash
curl -H "X-Auth-Token: architect-demo-001" \
  http://localhost:8080/admin/decisions | jq '.decisions | length'
```

### 場景 2：系統優化建議

```bash
curl -X POST \
  -H "X-Auth-Token: architect-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "分析最近的決策日誌，找出系統瓶頸"}' \
  http://localhost:8080/llm/chat
```

### 場景 3：新流程設計

```bash
curl -X POST \
  -H "X-Auth-Token: architect-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "設計新的補助申請與核核流程"}' \
  http://localhost:8080/llm/chat
```

### 場景 4：社區民主決策

```bash
curl -X POST \
  -H "X-Auth-Token: architect-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "為下月 AI Council 會議撰寫提案內容"}' \
  http://localhost:8080/llm/chat
```

---

## 環境變數配置

| 變數                  | 說明                       | 預設值     |
| --------------------- | -------------------------- | ---------- |
| `LOCAL_LLM_ENDPOINT`  | 本地 LLM 伺服器地址        | (未設定)   |
| `LOCAL_LLM_MODEL`     | 使用的模型名稱             | `little-j` |
| `LLM_FALLBACK`        | 是否允許雲端備援           | `1` (允許) |
| `AZURE_SPEECH_KEY`    | Azure Speech Services 金鑰 | (未設定)   |
| `AZURE_SPEECH_REGION` | Azure Speech 地區          | (未設定)   |

**啟動時設定**

```powershell
$env:LOCAL_LLM_ENDPOINT="http://127.0.0.1:11434/v1/chat/completions"
$env:LOCAL_LLM_MODEL="little-j"
$env:LLM_FALLBACK="1"
$env:AZURE_SPEECH_KEY="your-key-here"
$env:AZURE_SPEECH_REGION="eastasia"

python -m uvicorn vm_fastapi_main_dual_role:app --host 0.0.0.0 --port 8080
```

---

## 權限矩陣

| 操作         | 店家 | 架構師 |
| ------------ | ---- | ------ |
| 查詢裝置     | ✓    | ✓      |
| 修改裝置     | ✗    | ✓      |
| LLM 對話     | ✓    | ✓      |
| 語音交互     | ✓    | ✓      |
| 技能執行     | ✓    | ✓      |
| 查看決策日誌 | ✗    | ✓      |
| 審計報告     | ✗    | ✓      |
| AI 克隆部署  | ✗    | ✓      |
| 知識庫上傳   | ✗    | ✓      |
| 系統關閉     | ✗    | ✓      |

---

## 決策日誌文件結構

所有決策自動存檔於 `decision_logs/` 目錄：

```
decision_logs/
├── MERCHANT/
│   ├── decisions_2026-01-10.jsonl
│   ├── decisions_2026-01-11.jsonl
│   └── ...
└── ARCHITECT/
    ├── decisions_2026-01-10.jsonl
    ├── decisions_2026-01-11.jsonl
    └── ...
```

每條記錄格式：

```json
{
  "timestamp": "2026-01-10T12:00:00",
  "decision_id": "uuid-string",
  "user_role": "MERCHANT",
  "user_name": "五常社區 - 主門市",
  "action": "llm_chat",
  "payload": { ... },
  "result": { ... },
  "notes": "角色: MERCHANT",
  "status": "recorded"
}
```

---

## 常見問題

### Q1: 如何新增店家帳號？

在 `VALID_TOKENS` 字典中新增：

```python
"merchant-shop-003": {
    "role": Role.MERCHANT,
    "shop_name": "五常社區 - 第三門市",
    "created_at": datetime.datetime.utcnow().isoformat()
}
```

### Q2: 如何禁用雲端備援？

設定環境變數：

```powershell
$env:LLM_FALLBACK="0"
```

### Q3: 語音辨識支援哪些語言？

目前配置為 Traditional Chinese (`zh-TW`)。  
可在 `transcribe_audio_*` 函數中修改。

### Q4: 如何匯出決策日誌？

```bash
# 架構師可查詢，然後用 jq 匯出為 CSV
curl -H "X-Auth-Token: architect-demo-001" \
  http://localhost:8080/admin/decisions | \
  jq -r '.decisions[] | [.timestamp, .user_role, .action, .user_name] | @csv' > decisions.csv
```

### Q5: 決策日誌保留多久？

目前無自動刪除；建議定期備份並封存舊日期的檔案。

---

## 版本資訊

| 組件          | 版本   | 狀態                     |
| ------------- | ------ | ------------------------ |
| 五常 POS 系統 | 2.0    | ✓ 雙角色、語音、決策日誌 |
| Ollama        | 0.13.5 | ✓ 本地 LLM               |
| little-j 模型 | 4.7GB  | ✓ 測試中                 |
| FastAPI       | 0.100+ | ✓                        |
| Uvicorn       | 0.23+  | ✓                        |

---

## 下一步

1. 配置 Azure Speech Services（生產環境推薦）
2. 建立真實店家帳號與權限表
3. 建立 AI Council 會議與決策覆核流程
4. 實現 POS UI 與小 j 的實時整合
5. 部署至實際店鋪設備

---

文件版本：v1.0  
最後更新：2026-01-10  
維護者：Wuchang AI System
