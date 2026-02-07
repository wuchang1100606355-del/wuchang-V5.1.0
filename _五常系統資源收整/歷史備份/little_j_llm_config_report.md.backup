# 小j (Little J) - LLM 模型配置報告

**生成時間**: 2026-01-07  
**系統版本**: Wuchang OS V5.1.0

---

## 核心策略：本地優先 + 雲端備援

小j採用**混合式LLM架構**，優先使用本地模型，失敗時自動降級到雲端模型。

### 模型選擇優先級

```
1. 本地 Ollama (優先)
   ↓ (失敗時)
2. 雲端 Gemini (備援)
   ↓ (失敗時)
3. 簡單規則邏輯 (最終備援)
```

---

## 本地模型配置 (Local Ollama)

### 默認配置

| 項目 | 值 | 備註 |
|------|-----|------|
| **服務端點** | `http://host.docker.internal:11434` | Docker 內部網絡 |
| **默認模型** | `qwen2:0.5b` | 0.33 GB |
| **配置參數** | `wuchang.ollama_model` | 可在 Odoo 設定中修改 |
| **配置參數** | `wuchang.llm_base_url` | 可自訂端點 |

### 當前可用模型

根據測試結果，系統目前有以下模型：
- **qwen2:0.5b** ✅ (0.33 GB) - 運行中

### 使用場景

- ✅ **一般對話**: Mail Bot 回應
- ✅ **簡單分析**: 操作建議、上下文分析
- ✅ **翻譯任務**: 菜單翻譯
- ✅ **日常問候**: 幸運籤文生成

---

## 雲端模型配置 (Cloud Gemini)

### Vertex AI 模型

| 模型 | 用途 | 適用場景 |
|------|------|----------|
| **gemini-1.5-pro-preview-0409** | 複雜任務 | 深度分析、安全協議處理 |
| **gemini-1.5-flash** | 快速響應 | Mail Bot 一般對話（主要） |
| **gemini-1.0-pro** | 翻譯任務 | 多語言翻譯 |
| **gemini-1.5-pro-preview-0409** | 圖像分析 | 視覺任務（僅雲端） |

### 配置項目

| 項目 | 值 | 備註 |
|------|-----|------|
| **專案 ID** | `coffee-spark-ai-barista-b10b5` | Google Cloud 專案 |
| **位置** | `us-central1` | 區域設定 |
| **API Key** | `wuchang.google.api_key` | 需要配置 |
| **配置參數** | `wuchang.google.project_id` | 可自訂 |
| **配置參數** | `wuchang.google.location` | 可自訂 |

---

## AI 模式設定 (AI Mode)

### 可用模式

| 模式 | 說明 | 優先順序 |
|------|------|----------|
| **local_ollama** | 本地優先模式（默認） | 本地 → 雲端 → 規則 |
| **vertex_ai** | 雲端優先模式 | 雲端 → 規則 |
| **standard** | 標準模式 | 雲端 → 規則 |

### 默認模式

```python
# 默認值
ai_mode = 'local_ollama'
```

### 配置位置

- **Odoo 設定**: `設置 > 技術 > 參數 > 系統參數 > wuchang.ai_mode`
- **Python 配置**: `wuchang_os/addons/wuchang_core/models/settings.py`
- **XML 初始化**: `wuchang_os/addons/wuchang_core/data/system_params.xml`

---

## 具體使用場景

### 1. Mail Bot 對話

**流程**:
```
本地 Ollama (qwen2:0.5b) 
  ↓ (失敗時)
雲端 Gemini (gemini-1.5-flash)
```

**Prompt 包含**:
- 小j的身份與等級資訊
- 知識庫（鐵律、判例、稽核日誌）
- 使用者輸入內容

---

### 2. 操作分析 (analyze_operations)

**流程**:
```
本地 Ollama (qwen2:0.5b) 
  ↓ (失敗時)
雲端 Gemini (gemini-1.5-pro-preview-0409)
  ↓ (失敗時)
簡單規則邏輯
```

**Prompt 包含**:
- 小j的身份定義
- 安全協議（自殺、暴力、緊急情況處理）
- 上下文資訊

---

### 3. 翻譯任務 (translate_menu)

**流程**:
```
本地 Ollama (qwen2:0.5b)
  ↓ (失敗時)
雲端 Gemini (gemini-1.0-pro)
  ↓ (失敗時)
簡單回傳
```

---

### 4. 圖像分析 (analyze_image)

**流程**:
```
雲端 Gemini (gemini-1.5-pro-preview-0409)
  ↓ (僅雲端，無本地備援)
```

**原因**: 本地視覺模型較重，目前僅使用雲端。

---

## 模型選擇邏輯

### 代碼邏輯 (ai_logic.py)

```python
# 1. 檢查 AI 模式
mode = self._get_ai_mode()  # 默認: 'local_ollama'

# 2. 本地優先（如果模式是 local_ollama）
if mode == 'local_ollama':
    local_res = self._call_local_ollama(prompt, system_prompt)
    if local_res:
        return local_res  # 成功，直接返回

# 3. 雲端備援
GenModel = self._configure_vertex_ai()
if GenModel:
    model = GenModel("gemini-1.5-pro-preview-0409")
    response = model.generate_content(prompt)
    return response.text

# 4. 最終備援（簡單規則）
return "收到，持續監控中。"
```

---

## 當前配置狀態

### ✅ 已配置

- [x] **本地 Ollama**: 運行中 (`qwen2:0.5b`)
- [x] **AI 模式**: `local_ollama` (本地優先)
- [x] **服務端點**: `http://host.docker.internal:11434`
- [x] **自動降級**: 本地失敗時自動切換雲端

### ⚠️ 待配置（可選）

- [ ] **Google API Key**: 需要配置才能使用雲端 Gemini
  - 配置位置: `wuchang.google.api_key`
  - 或環境變數: `GOOGLE_API_KEY`

---

## 性能特點

### 本地模型 (qwen2:0.5b)

| 指標 | 數值 |
|------|------|
| **模型大小** | 0.33 GB |
| **響應時間** | ~1-3 秒 |
| **成本** | 免費（無使用限制） |
| **隱私** | 完全本地，數據不外洩 |
| **可用性** | 依賴本地服務運行狀態 |

### 雲端模型 (Gemini)

| 模型 | 響應時間 | 成本（每百萬 tokens） | 質量 |
|------|---------|---------------------|------|
| **gemini-1.5-flash** | ~0.5-1 秒 | 輸入: $0.075<br>輸出: $0.30 | ⭐⭐⭐ 優秀 |
| **gemini-1.5-pro** | ~1-2 秒 | 輸入: $1.25<br>輸出: $5.00 | ⭐⭐⭐⭐⭐ 卓越 |
| **gemini-1.0-pro** | ~0.5-1 秒 | 輸入: $0.50<br>輸出: $1.50 | ⭐⭐⭐ 優秀 |

---

## 建議配置

### 推薦設定（性價比平衡）

1. **AI 模式**: `local_ollama` (保持本地優先)
2. **本地模型**: `qwen2:0.5b` (當前配置)
3. **雲端模型**: `gemini-1.5-flash` (快速且便宜)
4. **配置 Google API Key**: 以啟用雲端備援

### 高性能設定（追求質量）

1. **AI 模式**: `vertex_ai` (雲端優先)
2. **雲端模型**: `gemini-1.5-pro-preview-0409` (最強模型)
3. **注意**: 成本較高，適合關鍵任務

---

## 配置文件位置

### 系統參數 (Odoo)

- **模型**: `ir.config_parameter`
- **查詢**: `設置 > 技術 > 參數 > 系統參數`
- **關鍵參數**:
  - `wuchang.ai_mode`: AI 模式
  - `wuchang.ollama_model`: Ollama 模型名稱
  - `wuchang.llm_base_url`: Ollama 服務端點
  - `wuchang.google.api_key`: Google API Key
  - `wuchang.google.project_id`: Google Cloud 專案 ID
  - `wuchang.google.location`: Google Cloud 區域

### 代碼文件

- **AI 邏輯**: `wuchang_os/addons/wuchang_core/models/ai_logic.py`
- **Mail Bot**: `wuchang_os/addons/wuchang_core/models/mail_bot.py`
- **設定介面**: `wuchang_os/addons/wuchang_core/models/settings.py`
- **初始化配置**: `wuchang_os/addons/wuchang_core/data/system_params.xml`

---

## 總結

### 小j的慣用LLM

1. **主要**: **Ollama (qwen2:0.5b)** - 本地優先，免費且私密
2. **備援**: **Gemini (gemini-1.5-flash)** - 雲端備援，快速且可靠
3. **策略**: **本地優先 + 自動降級** - 確保服務不中斷

### 優勢

- ✅ **成本效益**: 本地免費，雲端按需付費
- ✅ **隱私保護**: 本地處理，數據不外洩
- ✅ **可靠性**: 多層備援，服務不中斷
- ✅ **靈活性**: 可根據任務選擇不同模型

---

**報告生成時間**: 2026-01-07  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)
