# Ollama 模型服務未啟動 - 診斷報告

**診斷時間**: 2026-01-07  
**狀態**: 🔴 **問題已發現並部分修復**

---

## 問題根源

### ✅ 已修復：配置文件問題

1. **Ollama 服務被註釋**
   - 在 `docker-compose.yml` 第 115-123 行，Ollama 服務配置被完全註釋
   - 原因：註釋說明 "AI Services moved to AI VM"

2. **配置文件已更新**
   - ✅ 已取消註釋 Ollama 服務配置
   - ✅ 已添加 `ollama-data` volume 定義
   - ⚠️ 可能需要重新加載配置

---

## 診斷結果

### 當前狀態

| 項目 | 狀態 | 說明 |
|------|------|------|
| docker-compose.yml 配置 | ✅ 已修復 | Ollama 服務已啟用 |
| Volume 定義 | ✅ 已添加 | ollama-data 已定義 |
| Docker 容器 | ❌ 未啟動 | 需要執行啟動命令 |
| 端口 11434 | ❌ 未監聽 | 服務未運行 |
| API 可用性 | ❌ 不可用 | 服務未啟動 |

### 配置文件變更

**修復前**:
```yaml
  # ollama:
  #   image: ollama/ollama:latest
  #   ports:
  #     - "11434:11434"
  #   ...
```

**修復後**:
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

---

## 解決方案

### 方案一：啟動 Ollama 服務（推薦）

```powershell
# 1. 確保配置文件已保存
# 2. 啟動 Ollama 服務
cd "C:\wuchang V5.1.0"
docker-compose --profile ui up -d ollama

# 3. 等待服務啟動（約 15-30 秒）
Start-Sleep -Seconds 15

# 4. 驗證服務
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
```

### 方案二：使用 docker-compose-ai.yml

如果主配置文件有問題，可以使用單獨的 AI 配置文件：

```powershell
docker-compose -f docker-compose-ai.yml up -d ollama
```

### 方案三：手動創建容器

如果 Compose 仍有問題，可以手動創建容器：

```powershell
docker run -d `
  --name ollama `
  -p 11434:11434 `
  -v ollama-data:/root/.ollama `
  --restart unless-stopped `
  ollama/ollama:latest
```

---

## 啟動後驗證

### 1. 檢查容器狀態

```powershell
docker ps | Select-String ollama
```

### 2. 檢查 API

```powershell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
```

### 3. 下載模型（如需要）

```powershell
Invoke-RestMethod -Uri "http://localhost:11434/api/pull" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"name":"llama3.1"}' `
  -TimeoutSec 300
```

---

## 後續步驟

1. ✅ 配置文件已修復
2. ⏳ 啟動 Ollama 服務
3. ⏳ 驗證服務運行
4. ⏳ 下載測試模型（可選）
5. ⏳ 運行性能測試

---

## 注意事項

- Ollama 首次啟動需要下載模型，可能需要較長時間
- 建議使用輕量模型（如 qwen2:0.5b）進行快速測試
- 如果服務在 Docker 容器內，Odoo 需要使用 `host.docker.internal:11434` 訪問
- Volume 數據會持久化保存，即使容器重啟也不會丟失

---

**修復狀態**: ✅ 配置文件已修復，等待啟動服務