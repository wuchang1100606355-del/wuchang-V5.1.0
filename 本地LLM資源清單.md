# 本地 LLM 資源完整清單

**生成時間**: 2026-01-07  
**系統版本**: Wuchang OS V5.1.0

---

## 📦 本地 LLM 模型

### 1. Ollama 容器模型

**服務位置**: Docker 容器 `wuchangv510-ollama-1`  
**訪問端點**: 
- 容器內: `http://ollama:11434`
- 主機訪問: `http://localhost:11434`
- Docker 內部網絡: `http://host.docker.internal:11434`

**Docker Volume**: `wuchangv510_ollama-data`  
**Volume 掛載點**: `/root/.ollama` (容器內)

**已下載的模型**:

| 模型名稱 | 模型 ID | 大小 | 格式 | 量化級別 | 修改時間 | 狀態 |
|---------|---------|------|------|----------|----------|------|
| `qwen2:0.5b` | `6f48b936a09f` | 352 MB | GGUF | Q4_0 | 2026-01-07 | ✅ 可用 |

**詳細信息**:
- **家族**: Qwen2
- **參數大小**: 494.03M
- **量化級別**: Q4_0
- **模型摘要**: `6f48b936a09f7743c7dd30e72fdb14cba296bc5861902e4d0c387e8fb5050b39`

---

## 📁 地端檔案夾內的模型位置

### 實體模型文件存儲位置

1. **Docker Volume 實際位置** (Windows):
   - **Docker Volume 名稱**: `wuchangv510_ollama-data`
   - **Linux 容器內路徑**: `/var/lib/docker/volumes/wuchangv510_ollama-data/_data`
   - **Windows WSL 路徑**: `\\wsl$\docker-desktop-data\data\docker\volumes\wuchangv510_ollama-data\_data`
   - **或使用**: `\\wsl.localhost\docker-desktop-data\data\docker\volumes\wuchangv510_ollama-data\_data`
   - **容器內掛載點**: `/root/.ollama`
   - **配置文件**: `docker-compose.yml` (第 108 行)

2. **模型備份文件**:
   - **備份位置**: `C:\wuchang V5.1.0\migration_pack\volumes\ollama-data.tar.gz`
   - **說明**: 這是一個打包的備份文件，包含 Ollama 模型數據

2. **配置文件中引用的模型**:
   - **Odoo 系統參數**: `wuchang_os/addons/wuchang_core/data/system_params.xml`
     - 預設模型: `llama3.1` (第 50 行)
     - 實際使用: `qwen2:0.5b`
   - **AI 邏輯代碼**: `wuchang_os/addons/wuchang_core/models/ai_logic.py`
     - 預設模型: `qwen2:0.5b` (第 22 行)
   - **小J運動控制腳本**: `小J運動控制.py`
     - 模型名稱: `qwen2:0.5b` (第 23 行)

---

## 🔧 配置參數位置

### Odoo 系統參數

| 參數名稱 | 默認值 | 配置文件位置 |
|---------|--------|-------------|
| `wuchang.ai_mode` | `local_ollama` | `wuchang_os/addons/wuchang_core/data/system_params.xml:22` |
| `wuchang.llm_base_url` | `http://host.docker.internal:11434` | `system_params.xml:38` |
| `wuchang.ollama_model` | `llama3.1` | `system_params.xml:50` |
| `wuchang.gen_model` | `gemini-1.5-flash` | `system_params.xml:46` |
| `wuchang.gemini_api_key` | (空) | `system_params.xml:34` |
| `wuchang.google.api_key` | (空) | `system_params.xml:42` |
| `wuchang.google.project_id` | `coffee-spark-ai-barista-b10b5` | `ai_logic.py:46` |
| `wuchang.google.location` | `us-central1` | `ai_logic.py:47` |

### 代碼文件中的模型配置

1. **AI 邏輯模型** (`wuchang_os/addons/wuchang_core/models/ai_logic.py`):
   - 本地 Ollama 預設模型: `qwen2:0.5b` (第 22 行)
   - 本地 Ollama URL: `http://host.docker.internal:11434` (第 21 行)
   - Vertex AI 模型: `gemini-1.5-pro-preview-0409` (第 77 行)
   - 翻譯模型: `gemini-1.0-pro` (第 121 行)

2. **Mail Bot 模型** (`wuchang_os/addons/wuchang_core/models/mail_bot.py`):
   - Gemini 模型: `gemini-1.5-flash` (第 127 行)

3. **小J運動控制腳本** (`小J運動控制.py`):
   - 模型名稱: `qwen2:0.5b` (第 23 行)
   - Ollama URL: `http://ollama:11434` (容器內) 或 `http://localhost:11434` (主機)

---

## 🌐 服務端點

### 本地 LLM 服務

1. **Ollama API**:
   - **端點**: `http://localhost:11434/api/generate`
   - **模型列表**: `http://localhost:11434/api/tags`
   - **聊天 API**: `http://localhost:11434/api/chat`
   - **狀態**: ✅ 運行中

2. **模型管理**:
   - **查看模型**: `docker exec wuchangv510-ollama-1 ollama list`
   - **拉取模型**: `docker exec wuchangv510-ollama-1 ollama pull <model_name>`
   - **刪除模型**: `docker exec wuchangv510-ollama-1 ollama rm <model_name>`

---

## 📝 相關配置文件

### Docker Compose 配置

**文件**: `docker-compose.yml`  
**Ollama 服務配置** (第 103-111 行):
```yaml
ollama:
  image: ollama/ollama:latest
  ports:
    - "11434:11434"
  volumes:
    - ollama-data:/root/.ollama
  restart: unless-stopped
  profiles:
    - ui
```

### AI 路由器配置

**文件**: `ai_router.json`  
**配置內容**:
```json
{
  "providers": [
    {
      "name": "google",
      "model": "gemini-1.5-pro",
      "weight": 10,
      "healthy": true
    },
    {
      "name": "local",
      "model": "ollama",
      "weight": 5,
      "healthy": true
    }
  ]
}
```

---

## ✅ 總結

### 本地可用的 LLM

1. **qwen2:0.5b** (352 MB)
   - **位置**: Ollama 容器 (`wuchangv510_ollama-data` volume)
   - **狀態**: ✅ 已下載並可用
   - **用途**: 快速響應、簡單指令解析、JSON 轉換

### 配置中的模型引用

- **預設本地模型**: `qwen2:0.5b` (實際使用)
- **配置中的預設**: `llama3.1` (未下載)
- **雲端備援**: Gemini 系列模型 (需 API Key)

---

**最後更新**: 2026-01-07  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)
