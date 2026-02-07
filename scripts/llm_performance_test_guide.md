# 本地 LLM 模型性能測試指南

## 概述

本指南說明如何進行 Wuchang OS 本地 LLM 模型的性能測試。

## 測試工具

### 1. 完整性能測試腳本
- **文件**: `scripts/test_local_llm_performance.py`
- **功能**: 全面的性能測試，包括多個模型和多種測試場景
- **測試指標**:
  - 響應時間 (Latency)
  - Token 生成速度 (Throughput)
  - 響應質量
  - 不同提示長度的性能

### 2. 簡化測試腳本
- **文件**: `scripts/test_llm_performance_simple.py`
- **功能**: 快速性能測試
- **適用**: 快速驗證模型可用性

### 3. 自動啟動版本
- **文件**: `scripts/test_llm_performance_with_auto_start.ps1`
- **功能**: 自動檢查並啟動 Ollama 服務，然後運行測試

## 使用方法

### 方法一：使用自動啟動腳本（推薦）

```powershell
cd "C:\wuchang V5.1.0"
.\scripts\test_llm_performance_with_auto_start.ps1
```

### 方法二：手動啟動服務後測試

1. **啟動 Ollama 服務**:
```powershell
docker-compose --profile ui up -d
```

2. **運行測試**:
```powershell
python scripts/test_local_llm_performance.py
```

或使用簡化版本:
```powershell
python scripts/test_llm_performance_simple.py
```

### 方法三：使用自動安裝腳本

```powershell
.\scripts\auto_install_ai.ps1
```

然後運行測試腳本。

## 測試模型

默認測試以下模型（如果可用）：
- `llama3.1` - Llama 3.1 模型
- `qwen2:0.5b` - Qwen2 0.5B 輕量模型
- `phi4` - Phi-4 模型
- `mistral` - Mistral 模型

## 測試場景

完整測試包含以下場景：

1. **短提示** - 簡單問候和介紹
2. **中長提示** - 複雜問題解釋
3. **複雜任務** - 創意生成任務
4. **代碼生成** - 編程任務
5. **翻譯任務** - 多語言翻譯

## 測試指標

### 性能指標
- **響應時間** (Response Time): 從發送請求到收到完整響應的時間
- **Token 生成速度** (Tokens/Second): 每秒生成的 token 數量
- **總 Token 數**: 單次響應生成的 token 總數

### 質量指標
- **成功率** (Success Rate): 成功響應的百分比
- **響應長度**: 生成文本的字符數
- **響應相關性**: 響應是否與提示相關（需要人工評估）

## 測試結果

測試結果會自動保存到：
- `logs/llm_performance_test_YYYYMMDD_HHMMSS.json`

包含完整的測試數據和統計信息。

## 故障排除

### Ollama 服務不可用
```
錯誤: Ollama 服務不可用
```

**解決方案**:
1. 檢查 Docker 是否運行: `docker ps`
2. 啟動 Ollama: `docker-compose --profile ui up -d`
3. 等待服務啟動（約 10-30 秒）
4. 檢查服務狀態: `curl http://localhost:11434/api/tags`

### 模型未找到
```
錯誤: 模型 'xxx' 不可用
```

**解決方案**:
1. 檢查可用模型: 訪問 http://localhost:11434/api/tags
2. 下載模型: `ollama pull <model_name>`
3. 或使用可用模型進行測試

### 響應超時
```
錯誤: 請求超時
```

**解決方案**:
1. 增加超時時間（修改腳本中的 timeout 參數）
2. 使用更小的模型（如 qwen2:0.5b）
3. 減少 `num_predict` 參數值

## 性能優化建議

### 根據需求選擇模型

| 模型 | 大小 | 速度 | 質量 | 適用場景 |
|------|------|------|------|----------|
| qwen2:0.5b | 很小 | 很快 | 一般 | 簡單對話、快速響應 |
| llama3.1 | 中等 | 中等 | 好 | 通用任務 |
| phi4 | 小 | 快 | 好 | 代碼生成 |
| mistral | 大 | 慢 | 很好 | 複雜任務 |

### 配置建議

1. **開發環境**: 使用 `qwen2:0.5b` 或 `phi4` 以獲得快速響應
2. **生產環境**: 根據任務複雜度選擇 `llama3.1` 或 `mistral`
3. **資源受限**: 優先使用輕量模型

## 參考文檔

- Ollama 官方文檔: https://ollama.com/
- Wuchang OS AI 配置: `wuchang_os/addons/wuchang_core/models/ai_logic.py`
- 系統配置: `config/official_ai_identity.json`