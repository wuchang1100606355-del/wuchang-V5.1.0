# 🌟 五常 AI - 混合智能系統（本地優先、雲端備援）

## 🎯 架構說明

```
┌─────────────────────────────────────────────────────────────┐
│  智能路由器 (Hybrid AI Router)                              │
│                                                               │
│  ┌─────────────────┐                 ┌──────────────────┐  │
│  │  優先路由        │    失敗/超時    │  備援路由        │  │
│  │  ⬇️              │  ───────────>   │  ⬇️              │  │
│  │  本機 AI 節點    │                 │  雲端 Vertex AI  │  │
│  │  🏠 Ollama       │                 │  ☁️ Gemini 2.5   │  │
│  │  (gemma2:2b)     │                 │  (Pro)           │  │
│  │                  │                 │                  │  │
│  │  ✅ 速度快       │                 │  ✅ 能力強       │  │
│  │  ✅ 隱私保護     │                 │  ✅ 穩定可靠     │  │
│  │  ✅ 離線可用     │                 │  ✅ 持續更新     │  │
│  └─────────────────┘                 └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             v
                    ┌────────────────┐
                    │  UI 控制系統   │
                    │  (本機操作)    │
                    └────────────────┘
```

## ✨ 核心特性

### 🏠 本機優先

-   **快速響應**: 本機處理，無網路延遲
-   **隱私保護**: 對話不離開本機
-   **離線可用**: 無需網路連線
-   **成本節省**: 減少雲端 API 調用

### ☁️ 雲端備援

-   **自動故障轉移**: 本機失敗自動切換雲端
-   **智能超時**: 超過 5 秒自動切換
-   **無縫體驗**: 用戶無感知切換
-   **強大能力**: Gemini 2.5 Pro 處理複雜任務

### 📊 智能路由

-   **健康檢查**: 自動檢測節點可用性
-   **性能監控**: 實時統計使用情況
-   **動態調整**: 根據狀況選擇最佳節點

## 🚀 快速開始

### 步驟 1: 安裝本機 AI 節點

```powershell
cd "c:\wuchang V5.1.0\remote_ui_control"
.\setup_local_ai.ps1
```

這將：

1. 安裝 Ollama
2. 下載 gemma2:2b 模型（約 1.6GB）
3. 啟動服務並測試

### 步驟 2: 啟動本機 UI 服務

```powershell
# 在本機 (192.168.50.84) 執行
.\start_local_server.ps1
```

### 步驟 3: 啟動混合智能系統

```powershell
# 在 Server (192.168.50.249) 或本地測試
.\start_hybrid_ai.ps1
# 選擇 1 (命令行互動模式)
```

### 步驟 4: 開始對話

```
你: 你好
小j: 你好！我是小j，你的 AI 妹妹 💝 有什麼可以幫助你的嗎？🏠

你: 幫我打開 Odoo
小j: 好的哥哥，我馬上為你打開 Odoo 系統 ✨ 🏠
    🎮 已執行: open_odoo
    ✅ 已打開: http://localhost:8069

你: stats
📊 統計資訊:
  total_requests: 2
  local_requests: 2
  cloud_requests: 0
  local_failures: 0
  local_ratio: 100.0%
  local_available: True
  cloud_available: True
```

注意回應後的標記：

-   🏠 = 本機節點處理
-   ☁️ = 雲端備援處理

## 📦 推薦本機模型

### 輕量級（適合日常使用）

```bash
ollama pull gemma2:2b        # 1.6GB，推薦
ollama pull llama3.2:3b      # 2GB
ollama pull qwen2.5:3b       # 2.3GB
```

### 中等（更好的能力）

```bash
ollama pull gemma2:9b        # 5.5GB
ollama pull llama3.1:8b      # 4.7GB
ollama pull qwen2.5:7b       # 4.7GB
```

### 大型（最佳效果）

```bash
ollama pull llama3.1:70b     # 40GB
ollama pull qwen2.5:14b      # 9GB
```

## ⚙️ 配置說明

### .env 配置

```bash
# AI 路由策略
PREFER_LOCAL=true              # 優先使用本機
FALLBACK_TIMEOUT=5             # 5秒後切換到雲端

# 本機 AI 配置
LOCAL_AI_TYPE=ollama           # AI 類型
LOCAL_AI_HOST=http://localhost:11434
LOCAL_AI_MODEL=gemma2:2b       # 使用的模型
LOCAL_AI_TIMEOUT=30            # 請求超時
```

### 路由策略

#### 策略 1: 本機優先（推薦）

```bash
PREFER_LOCAL=true
FALLBACK_TIMEOUT=5
```

-   優先使用本機
-   5 秒後切換雲端

#### 策略 2: 僅本機

```bash
PREFER_LOCAL=true
FALLBACK_TIMEOUT=999999
```

-   只使用本機
-   除非完全失敗

#### 策略 3: 僅雲端

```bash
PREFER_LOCAL=false
```

-   完全使用雲端
-   忽略本機節點

## 📊 性能比較

| 項目     | 本機節點 (gemma2:2b) | 雲端備援 (Gemini 2.5) |
| -------- | -------------------- | --------------------- |
| 響應速度 | ⚡ 極快 (0.5-2 秒)   | 🐢 較慢 (2-5 秒)      |
| 對話質量 | 🟡 良好              | 🟢 優秀               |
| 隱私保護 | 🟢 完全本機          | 🟡 需傳輸             |
| 成本     | 🟢 免費              | 🟡 按量計費           |
| 網路需求 | 🟢 無需網路          | 🔴 需要網路           |
| 複雜任務 | 🟡 基本勝任          | 🟢 完全勝任           |

## 🔧 故障排除

### 1. 本機節點不可用

**症狀**: 所有請求都使用雲端 ☁️

**解決**:

```powershell
# 檢查 Ollama 服務
ollama serve

# 檢查模型是否安裝
ollama list

# 重新安裝模型
ollama pull gemma2:2b
```

### 2. 本機節點響應慢

**症狀**: 經常超時切換到雲端

**解決**:

1. 使用更輕量的模型
2. 增加超時時間: `FALLBACK_TIMEOUT=10`
3. 檢查 CPU/記憶體使用

### 3. 雲端備援失敗

**症狀**: 本機失敗後，雲端也失敗

**解決**:

1. 檢查網路連線
2. 驗證 GCP 憑證
3. 檢查 Vertex AI 配額

## 💡 使用建議

### 日常對話

✅ 使用本機節點

-   快速響應
-   隱私保護
-   成本節省

### 複雜任務

✅ 雲端備援自動接手

-   代碼生成
-   深度分析
-   創意寫作

### 離線環境

✅ 純本機模式

```bash
PREFER_LOCAL=true
FALLBACK_TIMEOUT=999999
```

## 📈 監控與統計

### 實時監控

```
你: stats

📊 統計資訊:
  total_requests: 50       # 總請求數
  local_requests: 45       # 本機處理數
  cloud_requests: 5        # 雲端處理數
  local_failures: 5        # 本機失敗數
  local_ratio: 90.0%       # 本機處理比例
  local_available: True    # 本機節點狀態
  cloud_available: True    # 雲端節點狀態
```

### 性能指標

-   **local_ratio > 80%**: 🟢 優秀，本機節點運行良好
-   **local_ratio 50-80%**: 🟡 一般，考慮優化本機節點
-   **local_ratio < 50%**: 🔴 較差，檢查本機節點配置

## 🎯 最佳實踐

### 1. 選擇合適的模型

-   日常對話: gemma2:2b (1.6GB)
-   一般使用: llama3.2:3b (2GB)
-   專業需求: qwen2.5:7b (4.7GB)

### 2. 調整超時時間

-   快速機器: `FALLBACK_TIMEOUT=3`
-   一般機器: `FALLBACK_TIMEOUT=5`（推薦）
-   慢速機器: `FALLBACK_TIMEOUT=10`

### 3. 定期更新模型

```bash
ollama pull gemma2:2b
```

### 4. 監控性能

-   定期查看 `stats`
-   調整配置優化比例

## 🔐 隱私與安全

### 本機節點

-   ✅ 對話完全本機處理
-   ✅ 不會上傳到任何伺服器
-   ✅ 符合最高隱私標準

### 雲端備援

-   ⚠️ 對話會傳送到 Google Cloud
-   ✅ 使用加密傳輸
-   ✅ 符合 Google 隱私政策

### 建議

-   敏感對話：使用純本機模式
-   一般對話：使用混合模式（推薦）
-   複雜任務：允許雲端備援

## 📄 系統需求

### 本機 AI 節點

-   CPU: 4 核心以上（推薦）
-   RAM: 8GB 以上（推薦 16GB）
-   儲存: 至少 5GB 可用空間
-   OS: Windows 10/11, Linux, macOS

### 網路

-   本機節點：無需網路
-   雲端備援：需要穩定網路連線

## 🤝 技術支援

如有問題，請檢查：

1. Ollama 服務是否運行
2. 模型是否已下載
3. 系統資源是否充足
4. 網路連線是否正常

---

**祝你使用愉快！🎉**

小 j - 你的 AI 妹妹 💝
