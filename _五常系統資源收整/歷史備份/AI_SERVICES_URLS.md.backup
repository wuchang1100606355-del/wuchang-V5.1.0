# AI 服務端口和網址

## 🤖 本地 AI 服務 (Ollama)

### 服務信息
- **容器名稱**: ollama
- **服務狀態**: 運行中
- **端口映射**: `0.0.0.0:11434->11434/tcp`

### 訪問網址

#### 基礎 URL
- **本地訪問**: http://localhost:11434
- **API 基礎**: http://localhost:11434/api

#### 主要 API 端點

1. **模型列表**
   - URL: http://localhost:11434/api/tags
   - 方法: GET
   - 說明: 查看已安裝的模型

2. **生成文本**
   - URL: http://localhost:11434/api/generate
   - 方法: POST
   - 說明: 使用模型生成文本

3. **聊天**
   - URL: http://localhost:11434/api/chat
   - 方法: POST
   - 說明: 與模型進行對話

4. **模型信息**
   - URL: http://localhost:11434/api/show
   - 方法: POST
   - 說明: 查看特定模型的詳細信息

### 使用示例

#### 檢查已安裝的模型
```bash
curl http://localhost:11434/api/tags
```

#### 生成文本
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2:0.5b",
  "prompt": "你好",
  "stream": false
}'
```

#### 聊天
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2:0.5b",
  "messages": [
    {"role": "user", "content": "你好"}
  ]
}'
```

---

## 🔗 Odoo 中的 AI 配置

### 配置參數

在 Odoo 中，AI 服務通過以下配置參數設置：

1. **wuchang.llm_base_url**
   - 說明: LLM 服務的基礎 URL
   - 預設值: `/wuchang/llm/generate` (Odoo 內部路由)
   - 可設置為: `http://host.docker.internal:11434/api/generate` (使用本地 Ollama)

2. **wuchang.gemini_api_key**
   - 說明: Google Gemini API 金鑰
   - 用途: 雲端 AI 功能

### 在 Odoo 中設置

1. **訪問設置**
   - 登入 Odoo
   - 進入「設定」→「技術」→「參數」→「系統參數」

2. **設置 LLM Base URL**
   - 參數名稱: `wuchang.llm_base_url`
   - 參數值: `http://host.docker.internal:11434/api/generate`

3. **設置 Gemini API Key** (可選)
   - 參數名稱: `wuchang.gemini_api_key`
   - 參數值: (您的 Gemini API 金鑰)

---

## 🌐 網絡配置

### Docker 內部訪問

從 Odoo 容器內部訪問 Ollama：
- **URL**: `http://host.docker.internal:11434`
- **說明**: `host.docker.internal` 是 Docker 的特殊主機名，指向宿主機

### 本地訪問

從宿主機訪問：
- **URL**: `http://localhost:11434`

---

## 📝 相關服務

### Open WebUI (可選)

如果安裝了 Open WebUI：
- **端口**: 8080
- **URL**: http://localhost:8080
- **說明**: 提供 Web 界面管理 Ollama 模型

**注意**: 當前配置中 Open WebUI 被註釋掉了，如需使用需要取消註釋。

---

## 🔧 故障排除

### 檢查服務狀態
```powershell
docker-compose ps ollama
```

### 檢查端口監聽
```powershell
netstat -an | findstr 11434
```

### 測試連接
```powershell
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET
```

### 查看日誌
```powershell
docker-compose logs ollama
```

---

## ✅ 合規聲明

符合 Google 非營利組織合規要求

---

## 📝 最後更新

- **檢查時間**: 2026-01-07 22:55
- **服務狀態**: Ollama 運行中
- **端口**: 11434
