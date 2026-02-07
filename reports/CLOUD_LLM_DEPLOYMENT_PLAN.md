# 雲端大型開源 LLM 部署計劃

**建立時間：** 2026-01-20  
**策略：** 善用雲端空間，部署大型開源模型  
**預算：** 使用免費試用額度 $8,334（6天內到期）

---

## 🎯 策略概述

### 核心想法

**既然雲端空間大，就得善用！**

1. **在 Google Cloud 部署大型開源 LLM**
   - 使用 Vertex AI 或 Cloud Run
   - 部署 qwen2:7b 或 llama3.1:8b
   - 通過 API 調用

2. **充分利用免費試用額度**
   - 使用 $8,334 剩餘額度
   - 建立雲端 LLM 服務
   - 6天內完成部署

3. **混合架構**
   - 本地：qwen2:0.5b（簡單任務，快速）
   - 雲端：qwen2:7b（複雜任務，強大）
   - 智能路由：根據任務選擇

---

## 💰 使用免費試用額度部署

### 方案 A：Vertex AI 部署（推薦）⭐⭐⭐⭐⭐

**使用額度：** $1,500-$2,500

#### 部署方式

**1. 使用 Vertex AI Model Garden**
- 支援多種開源模型
- 可直接部署
- 自動管理資源

**2. 自訂模型部署**
- 上傳模型到 Cloud Storage
- 使用 Vertex AI 部署
- 通過 API 調用

#### 成本估算

**部署成本：**
- 模型儲存（Cloud Storage）：$50-$100/月
- 推理實例（Vertex AI）：$200-$500/月
- 網路傳輸：$50-$100/月

**使用免費試用額度：**
- 初始部署：$500-$1,000
- 前3個月運行：$1,000-$2,000
- **總計：** $1,500-$3,000（完全由免費額度覆蓋）

---

### 方案 B：Cloud Run 部署 ⭐⭐⭐⭐⭐（最推薦）

**使用額度：** $800-$1,500

#### 為什麼推薦 Cloud Run？

1. **成本效益最佳**
   - 按需付費（無請求時不計費）
   - 自動擴展
   - 適合間歇性使用

2. **部署簡單**
   - 容器化部署
   - 支援 Ollama 容器
   - 易於管理

3. **靈活配置**
   - 可配置 CPU 和記憶體
   - 支援 GPU（如需要）

#### 部署架構

```
Cloud Run 服務
    ├── Ollama 容器
    │   ├── qwen2:7b 模型
    │   └── API 服務
    └── 自動擴展
```

#### 成本估算

**Cloud Run 配置：**
- CPU: 4-8 vCPU
- 記憶體: 16-32GB
- 請求處理: 按需計費

**月度成本：**
- 低使用量（1000請求/天）：$50-$150/月
- 中使用量（5000請求/天）：$150-$400/月
- 高使用量（10000請求/天）：$400-$800/月

**使用免費試用額度：**
- 初始部署：$200-$300
- 前3個月運行：$600-$1,200
- **總計：** $800-$1,500（完全由免費額度覆蓋）

---

### 方案 C：Compute Engine + Ollama ⭐⭐⭐⭐

**使用額度：** $1,000-$2,000

#### 部署方式

**1. 建立 VM 實例**
- 規格：n1-standard-4 或 n1-standard-8
- 記憶體：16-32GB
- 儲存：100GB SSD

**2. 安裝 Ollama**
- 在 VM 上安裝 Ollama
- 下載大型模型（qwen2:7b）
- 配置 API 服務

#### 成本估算

**VM 實例：**
- n1-standard-4 (4 vCPU, 15GB RAM): $150-$200/月
- n1-standard-8 (8 vCPU, 30GB RAM): $300-$400/月

**儲存：**
- 100GB SSD: $20-$30/月
- 模型儲存：$10-$20/月

**使用免費試用額度：**
- 初始部署：$300-$500
- 前3個月運行：$700-$1,500
- **總計：** $1,000-$2,000（完全由免費額度覆蓋）

---

## 🚀 推薦部署方案

### 最佳方案：Cloud Run + Ollama ⭐⭐⭐⭐⭐

**理由：**
1. ✅ 成本效益最佳（按需付費）
2. ✅ 部署最簡單
3. ✅ 自動擴展
4. ✅ 完全由免費額度覆蓋

**使用額度：** $800-$1,500

---

## 📋 詳細部署步驟

### 步驟 1：準備模型檔案

**下載大型開源模型：**

```bash
# 在本地下載模型
docker exec wuchangv510-ollama-1 ollama pull qwen2:7b

# 或下載 llama3.1:8b
docker exec wuchangv510-ollama-1 ollama pull llama3.1:8b
```

**上傳到 Cloud Storage：**
- 建立 Cloud Storage bucket
- 上傳模型檔案
- 設定適當的權限

---

### 步驟 2：建立 Cloud Run 服務

**建立 Dockerfile：**

```dockerfile
FROM ollama/ollama:latest

# 複製模型檔案
COPY models/ /root/.ollama/models/

# 暴露端口
EXPOSE 11434

# 啟動 Ollama
CMD ["ollama", "serve"]
```

**部署到 Cloud Run：**

```bash
# 建立 Cloud Run 服務
gcloud run deploy ollama-llm \
  --image gcr.io/my-j-483304/ollama-llm \
  --platform managed \
  --region asia-east1 \
  --memory 16Gi \
  --cpu 4 \
  --allow-unauthenticated
```

---

### 步驟 3：配置 API 端點

**建立 API 閘道：**

```python
# API 路由服務
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
CLOUD_RUN_URL = "https://ollama-llm-xxx.run.app"

@app.route('/api/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    model = request.json.get('model', 'qwen2:7b')
    
    response = requests.post(
        f"{CLOUD_RUN_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    
    return jsonify(response.json())
```

---

### 步驟 4：整合到現有系統

**更新系統配置：**

```python
# wuchang_os/addons/wuchang_core/models/ai_logic.py

class WuchangAILogic:
    def __init__(self):
        self.local_ollama_url = "http://localhost:11434"
        self.cloud_ollama_url = "https://ollama-llm-xxx.run.app"
        self.local_model = "qwen2:0.5b"
        self.cloud_model = "qwen2:7b"
    
    def process(self, prompt: str, task_type: str = "simple"):
        """智能路由：簡單任務用本地，複雜任務用雲端"""
        
        if task_type == "simple":
            # 簡單任務：使用本地模型
            return self._call_local(prompt)
        else:
            # 複雜任務：使用雲端模型
            return self._call_cloud(prompt)
    
    def _call_local(self, prompt: str):
        # 調用本地 Ollama
        pass
    
    def _call_cloud(self, prompt: str):
        # 調用雲端 Ollama
        pass
```

---

## 💡 智能路由策略

### 路由規則

**本地模型（qwen2:0.5b）：**
- ✅ 簡單問答
- ✅ 快速回應需求
- ✅ 隱私敏感資料
- ✅ 離線使用

**雲端模型（qwen2:7b）：**
- ✅ 複雜推理
- ✅ 長文本生成
- ✅ 多語言處理
- ✅ 需要高準確度

---

## 📊 成本效益分析

### 使用免費試用額度

**投資：** $800-$1,500（完全由免費額度覆蓋）

**效益：**
- ✅ 立即獲得 7B 模型能力（14倍提升）
- ✅ 無需硬體升級
- ✅ 自動擴展和負載均衡
- ✅ 前3個月完全免費

**長期成本（3個月後）：**
- 低使用量：$50-$150/月
- 中使用量：$150-$400/月
- 可用 Google Cloud 非營利抵免額（$350/月）覆蓋

---

## 🎯 與四個月後採購計劃整合

### 現在（6天內）

**使用免費試用額度：**
- ✅ 部署雲端 LLM（qwen2:7b）
- ✅ 建立智能路由系統
- ✅ 測試和優化

### 四個月後（新伺服器）

**混合架構：**
- 本地：升級到 64GB RAM，運行 7B 模型
- 雲端：作為備援和擴展
- 智能路由：根據負載和需求選擇

---

## ✅ 立即行動計劃

### 今天（緊急）

1. **建立 Cloud Storage bucket**
   ```bash
   gsutil mb gs://wuchang-llm-models
   ```

2. **下載模型到本地**
   ```bash
   docker exec wuchangv510-ollama-1 ollama pull qwen2:7b
   ```

3. **準備部署腳本**

### 明天

1. **上傳模型到 Cloud Storage**
2. **建立 Cloud Run 服務**
3. **配置 API 端點**

### 第3-4天

1. **測試雲端 LLM 服務**
2. **整合到現有系統**
3. **設定智能路由**

### 第5-6天

1. **優化配置**
2. **監控使用量**
3. **調整資源配置**

---

## 📋 檢查清單

### 部署前

- [ ] 確認免費試用額度剩餘：$8,334
- [ ] 選擇部署方案（推薦：Cloud Run）
- [ ] 準備模型檔案
- [ ] 建立 Cloud Storage bucket

### 部署中

- [ ] 建立 Cloud Run 服務
- [ ] 上傳模型檔案
- [ ] 配置 API 端點
- [ ] 測試服務可用性

### 部署後

- [ ] 整合到現有系統
- [ ] 設定智能路由
- [ ] 監控使用量和成本
- [ ] 優化配置

---

## 💡 優勢總結

### 為什麼這個策略很棒？

1. **充分利用免費額度**
   - ✅ 6天內使用 $8,334
   - ✅ 建立永久價值的服務
   - ✅ 前3個月完全免費

2. **立即獲得強大能力**
   - ✅ 7B 模型（14倍能力提升）
   - ✅ 無需等待硬體升級
   - ✅ 自動擴展和負載均衡

3. **靈活的混合架構**
   - ✅ 本地 + 雲端
   - ✅ 智能路由
   - ✅ 最佳成本效益

4. **為未來做準備**
   - ✅ 四個月後新伺服器可本地運行
   - ✅ 雲端作為備援和擴展
   - ✅ 最佳化資源使用

---

**建立時間：** 2026-01-20  
**策略：** 善用雲端空間，部署大型開源模型 ⭐⭐⭐⭐⭐  
**緊急度：** 6天內完成部署，充分利用免費試用額度！
