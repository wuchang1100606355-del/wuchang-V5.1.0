# 本地 LLM vs 雲端 Gemini 性能比較指南

## 概述

本指南說明如何進行本地 Ollama 和雲端 Google Gemini 的性能比較測試，並生成量化比較表格。

## 前置準備

### 1. 本地 Ollama 設置

```powershell
# 1. 啟動 Ollama 服務（如果尚未啟動）
docker-compose -f docker-compose-ai.yml up -d ollama

# 2. 下載測試模型
.\scripts\download_test_model.ps1 -Model "qwen2:0.5b"

# 3. 驗證服務
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
```

### 2. 雲端 Gemini 設置

```powershell
# 設置 Google API Key
$env:GOOGLE_API_KEY = "your-api-key-here"

# 或添加到配置文件
# 編輯 config/official_ai_identity.json，添加 "google_api_key" 字段
```

## 運行比較測試

### 方法一：完整比較測試

```powershell
cd "C:\wuchang V5.1.0"
python scripts/compare_llm_performance.py
```

### 方法二：僅測試本地模型

```powershell
python scripts/test_local_llm_performance.py
```

### 方法三：僅測試雲端模型

（需要配置 API Key）

## 測試結果解讀

### 性能指標

- **平均響應時間**: 從發送請求到收到完整響應的時間
- **平均生成速度**: 每秒生成的 token 數量
- **成功率**: 成功響應的百分比

### 成本指標

- **本地模型**: 免費，無使用限制
- **雲端 Gemini**: 
  - 輸入: $0.075 per 1M tokens
  - 輸出: $0.30 per 1M tokens

## 比較維度

### 1. 速度比較

| 場景 | 本地優勢 | 雲端優勢 |
|------|---------|---------|
| 簡單任務 | ⚡ 更快（無網絡延遲） | - |
| 複雜任務 | - | ⚡ 更快（更強算力） |

### 2. 質量比較

| 場景 | 本地優勢 | 雲端優勢 |
|------|---------|---------|
| 通用對話 | ✅ 可接受 | ⭐⭐⭐ 優秀 |
| 專業任務 | ✅ 可接受 | ⭐⭐⭐ 優秀 |
| 代碼生成 | ✅ 可接受 | ⭐⭐⭐ 優秀 |

### 3. 成本比較

| 使用量 | 本地 | 雲端 |
|-------|------|------|
| 1000 次請求 | $0 | ~$0.50 |
| 10,000 次請求 | $0 | ~$5.00 |
| 100,000 次請求 | $0 | ~$50.00 |

### 4. 隱私比較

| 項目 | 本地 | 雲端 |
|------|------|------|
| 數據傳輸 | ❌ 無 | ✅ 需要 |
| 數據存儲 | ❌ 本地 | ✅ 雲端 |
| 數據隱私 | ⭐⭐⭐ 完全私密 | ⭐ 依賴供應商 |

## 使用建議

### 開發階段
- ✅ 使用本地模型（快速迭代、無成本）

### 生產環境
- **高質量需求**: 使用 Gemini
- **成本敏感**: 使用本地模型
- **混合模式**: 
  - 簡單任務 → 本地
  - 複雜任務 → 雲端

### 數據敏感場景
- ✅ 強烈推薦本地模型
- ❌ 避免使用雲端模型

## 故障排除

### Ollama 不可用

```powershell
# 檢查容器狀態
docker ps | Select-String ollama

# 重啟服務
docker-compose -f docker-compose-ai.yml restart ollama
```

### Gemini API 失敗

1. 檢查 API Key 是否正確設置
2. 檢查網絡連接
3. 檢查 API 配額是否用完

## 結果保存

測試結果會自動保存到：
- `logs/llm_comparison_YYYYMMDD_HHMMSS.json`

包含完整的測試數據和統計信息。
