# Ollama 模型服務未啟動診斷報告

**診斷時間**: 2026-01-07
**問題**: Ollama 本地 LLM 服務未運行

---

## 問題發現

### 1. 根本原因

在 `docker-compose.yml` 文件中，Ollama 服務配置被**完全註釋掉**了：

```yaml
# AI Services moved to AI VM
# ollama:
#   image: ollama/ollama:latest
#   ports:
#     - "11434:11434"
#   volumes:
#     - ${AI_MEMORY_PATH:-/mnt/ai-memory}/ollama:/root/.ollama
#   restart: unless-stopped
#   profiles:
#     - ui
```

**註釋說明**: "AI Services moved to AI VM" - AI 服務已移至 AI VM

### 2. 當前容器狀態

通過 `docker ps -a` 檢查，發現：
- ✅ Odoo 服務運行中 (`wuchangv510-wuchang-web-1`)
- ✅ 數據庫運行中 (`wuchangv510-db-1`)
- ✅ Caddy 運行中
- ❌ **Ollama 容器不存在**（未啟動）

### 3. 可用配置文件

發現存在先先
---

## 解決方案

### 方案一：取消註釋 Ollama 服務（推薦用於本地開發）

在 `docker-compose.yml` 中取消註釋 Ollama 服務配置。

**優點**:
- 統一管理所有服務
- 使用現有的 profile 機制
- 與系統其他服務在同一 compose 文件中

**缺點**:
- 需要手動修改配置文件

### 方案二：使用 docker-compose-ai.yml（推薦用於生產環境）

使用單獨的 AI 服務配置文件啟動 Ollama。

**優點**:
- 服務分離，便於管理
- 已有完整配置
- 不影響主系統配置

**缺點**:
- 需要管理兩個 compose 文件
- 網絡配置需要協調

### 方案三：使用獨立 Ollama 容器

直接在 Docker 中運行 Ollama，不通過 Compose。

---

## 修復步驟

### 方法一：啟用 docker-compose.yml 中的 Ollama（推薦）

1. 編輯 `docker-compose.yml`
2. 取消註釋 Ollama 服務（第 115-123 行）
3. 運行：`docker-compose --profile ui up -d`

### 方法二：使用 docker-compose-ai.yml

1. 運行：`docker-compose -f docker-compose-ai.yml up -d`
2. 等待服務啟動（約 10-30 秒）
3. 驗證服務：訪問 `http://localhost:11434/api/tags`

---

## 詳細診斷

### 配置檢查

| 項目 | 狀態 | 說明 |
|------|------|------|
| docker-compose.yml | ⚠️ Ollama 被註釋 | 需要啟用 |
| docker-compose-ai.yml | ✅ 配置完整 | 可用 |
| 端口 11434 | ❌ 未監聽 | 服務未啟動 |
| 容器 ollama | ❌ 不存在 | 未啟動 |

### 依賴關係

- Ollama 服務：獨立的 LLM 服務
- Open WebUI（可選）：需要 Ollama 運行
- Odoo AI 模組：可以通過 `wuchang.llm_base_url` 配置連接 Ollama

### 網絡配置

如果需要 Ollama 與 Odoo 通信：
- 使用 `host.docker.internal:11434`（從 Docker 容器內訪問宿主機）
- 或使用 Docker 網絡（在同一個 compose 文件中）

---

## 建議操作

根據註釋 "AI Services moved to AI VM"，建議：

1. **本地開發環境**：啟用 `docker-compose.yml` 中的 Ollama
2. **生產環境**：使用 AI VM 上的 Ollama 服務
3. **混合環境**：Ollama 在 AI VM，Odoo 通過網絡連接

---

## 下一步行動

1. 決定使用哪種方案（本地還是遠程）
2. 根據選擇修復配置
3. 啟動 Ollama 服務
4. 運行性能測試驗證
