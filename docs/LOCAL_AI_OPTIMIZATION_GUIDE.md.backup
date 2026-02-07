# 本地 AI 永久優化指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**目標**: 永久優化本地 AI（Ollama）的運用方式

---

## 🎯 目前本地 AI 配置

### 當前狀態

| 項目 | 配置 | 狀態 |
|------|------|------|
| **AI 模式** | `local_ollama` | ✅ 本地優先 |
| **本地模型** | `qwen2:0.5b` | ✅ 運行中 |
| **服務端點** | `http://host.docker.internal:11434` | ✅ 已配置 |
| **自動降級** | 本地失敗時自動切換雲端 | ✅ 已啟用 |

---

## 🚀 永久優化策略

### 1. 模型升級優化

#### 當前模型：qwen2:0.5b
- **大小**: 0.33 GB
- **優點**: 輕量、快速
- **缺點**: 能力有限

#### 優化建議：升級到更好的模型

| 模型 | 大小 | 能力 | 建議 |
|------|------|------|------|
| **qwen2:1.5b** | ~1 GB | ⭐⭐⭐ 良好 | ✅ 推薦升級 |
| **qwen2:3b** | ~2 GB | ⭐⭐⭐⭐ 優秀 | ✅ 如果資源足夠 |
| **qwen2:7b** | ~4.5 GB | ⭐⭐⭐⭐⭐ 卓越 | ⚠️ 需要較多資源 |

**升級步驟**：
```powershell
# 下載更好的模型
docker exec -it ollama ollama pull qwen2:1.5b

# 或使用腳本
.\scripts\download_optimized_model.ps1 -Model "qwen2:1.5b"
```

---

### 2. 硬體優化

#### GPU 加速（如果有 GPU）

**檢查 GPU**：
```powershell
# 檢查 NVIDIA GPU
nvidia-smi

# 檢查是否支援 CUDA
docker exec -it ollama ollama run qwen2:0.5b --verbose
```

**啟用 GPU 加速**：
- 如果有多餘的抵免額度，可以考慮使用 Google Cloud GPU 實例
- 或使用本地 GPU（如果有）

#### 記憶體優化

**建議配置**：
- **最小**: 4 GB RAM（qwen2:0.5b）
- **推薦**: 8 GB RAM（qwen2:1.5b）
- **理想**: 16 GB RAM（qwen2:3b 或 7b）

---

### 3. 快取機制優化

#### 實現多層快取

1. **記憶體快取**（最快）
   - 快取常見問題的回答
   - 減少重複計算

2. **Redis 快取**（快速）
   - 快取 API 回應
   - 共享快取

3. **資料庫快取**（持久）
   - 儲存歷史對話
   - 學習常見模式

#### 實作建議

```python
# 多層快取實作
class AICache:
    def __init__(self):
        self.memory_cache = {}  # 記憶體快取
        self.redis_cache = None  # Redis 快取（可選）
        self.db_cache = None  # 資料庫快取
    
    def get(self, key):
        # 1. 檢查記憶體快取
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # 2. 檢查 Redis 快取
        if self.redis_cache:
            result = self.redis_cache.get(key)
            if result:
                self.memory_cache[key] = result  # 提升到記憶體
                return result
        
        # 3. 檢查資料庫快取
        if self.db_cache:
            result = self.db_cache.get(key)
            if result:
                self.memory_cache[key] = result
                return result
        
        return None
    
    def set(self, key, value, ttl=3600):
        # 設定到所有快取層
        self.memory_cache[key] = value
        if self.redis_cache:
            self.redis_cache.set(key, value, ttl)
        if self.db_cache:
            self.db_cache.set(key, value)
```

---

### 4. 提示詞優化

#### 系統提示詞優化

**當前提示詞**（基礎）：
```
你是小J，五常社區的 AI 助手。
```

**優化提示詞**（詳細）：
```
你是小J（Little J），五常智慧社區雲的 AI 核心。

核心特質：
- 溫暖、親切、有同理心
- 專業、準確、可靠
- 積極主動、解決問題導向

能力範圍：
- 社區管理與服務
- POS 系統支援
- 設備管理
- 資料分析與建議

回應風格：
- 使用繁體中文（台灣）
- 簡潔明瞭，避免冗長
- 提供實用建議
- 必要時提供詳細說明
```

#### 提示詞模板化

建立提示詞模板庫，針對不同場景使用不同模板：
- 一般對話模板
- POS 操作模板
- 設備管理模板
- 資料查詢模板

---

### 5. 批次處理優化

#### 合併多個請求

**當前方式**（逐個處理）：
```python
for question in questions:
    response = ai.ask(question)  # 每次 API 呼叫
```

**優化方式**（批次處理）：
```python
# 合併多個問題
batch_prompt = "\n".join([f"Q{i+1}: {q}" for i, q in enumerate(questions)])
response = ai.ask(batch_prompt)  # 一次 API 呼叫
# 解析批次回應
answers = parse_batch_response(response)
```

---

### 6. 模型微調（進階）

#### 針對五常社區微調

**微調資料**：
- 社區常見問題
- POS 操作流程
- 設備管理指令
- 歷史對話記錄

**微調方法**：
```bash
# 使用 Ollama 的微調功能
ollama create wuchang-qwen2:custom -f Modelfile

# Modelfile 內容：
# FROM qwen2:1.5b
# SYSTEM """你是小J，五常社區的 AI 助手..."""
# ADAPTER /path/to/adapter
```

---

### 7. 負載平衡（多實例）

#### 運行多個 Ollama 實例

**配置**：
- 主實例：處理一般請求
- 備援實例：處理高負載或備援
- 專用實例：處理特定任務（如 POS 語音）

**實作**：
```yaml
# docker-compose.yml
services:
  ollama-main:
    image: ollama/ollama
    ports:
      - "11434:11434"
  
  ollama-backup:
    image: ollama/ollama
    ports:
      - "11435:11434"
  
  ollama-pos:
    image: ollama/ollama
    ports:
      - "11436:11434"
```

---

## 📊 優化效果預估

### 性能提升

| 優化項目 | 當前 | 優化後 | 提升 |
|---------|------|--------|------|
| **回應速度** | 1-3 秒 | 0.5-1.5 秒 | 50% |
| **準確度** | ⭐⭐⭐ | ⭐⭐⭐⭐ | 33% |
| **快取命中率** | 0% | 60-80% | 無限 |
| **成本** | $0 | $0 | 維持免費 |

---

## 🎯 POS 語音對話式點餐優化

### 使用另一筆抵免額度

**建議運用**：
1. **Google Cloud Speech-to-Text API**
   - 語音轉文字（免費額度）
   - 高準確度中文語音識別

2. **Google Cloud Text-to-Speech API**
   - 文字轉語音（免費額度）
   - 自然的中文語音合成

3. **本地 AI（Ollama）**
   - 理解點餐意圖
   - 處理對話流程
   - 生成回應

### 架構設計

```
語音輸入 → Speech-to-Text API → 本地 AI（理解意圖）→ POS 系統
                                                      ↓
語音輸出 ← Text-to-Speech API ← 本地 AI（生成回應）←
```

---

## 💡 永久優化檢查清單

### 立即優化（免費）

- [ ] 升級模型（qwen2:0.5b → qwen2:1.5b）
- [ ] 實作多層快取機制
- [ ] 優化系統提示詞
- [ ] 實作批次處理

### 中期優化（使用免費額度）

- [ ] 整合 Google Speech-to-Text API
- [ ] 整合 Google Text-to-Speech API
- [ ] 優化 POS 語音點餐流程

### 長期優化（進階）

- [ ] 模型微調（針對五常社區）
- [ ] 多實例負載平衡
- [ ] GPU 加速（如果有資源）

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
