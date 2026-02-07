# 本地 LLM vs 雲端 Gemini 性能比較報告模板

## 測試環境

- **測試時間**: {timestamp}
- **測試平台**: Wuchang OS V5.1.0
- **本地模型**: Ollama (qwen2:0.5b, llama3.1)
- **雲端模型**: Google Gemini 1.5 Flash

## 比較指標

### 1. 性能指標

| 指標 | 本地 Ollama | 雲端 Gemini | 優勢 |
|------|------------|------------|------|
| 平均響應時間 | {local_avg_time}s | {gemini_avg_time}s | {winner_time} |
| 平均生成速度 | {local_speed} t/s | {gemini_speed} t/s | {winner_speed} |
| 成功率 | {local_success}% | {gemini_success}% | {winner_success} |
| 總響應時間 | {local_total}s | {gemini_total}s | {winner_total} |

### 2. 成本指標

| 指標 | 本地 Ollama | 雲端 Gemini |
|------|------------|------------|
| 每次請求成本 | $0.00 (免費) | ${gemini_cost} |
| 月預估成本 | $0.00 | ${monthly_estimate} |
| 年度成本 | $0.00 | ${yearly_estimate} |

### 3. 詳細測試結果

| 測試案例 | 本地模型 | Gemini | 優勢 | 備註 |
|---------|---------|--------|------|------|
| 短問答 | {local_q1}s | {gemini_q1}s | {winner_q1} | - |
| 中長回答 | {local_q2}s | {gemini_q2}s | {winner_q2} | - |
| 創意任務 | {local_q3}s | {gemini_q3}s | {winner_q3} | - |
| 代碼生成 | {local_q4}s | {gemini_q4}s | {winner_q4} | - |
| 翻譯任務 | {local_q5}s | {gemini_q5}s | {winner_q5} | - |

## 分析結論

### 性能優勢
- **響應速度**: {time_analysis}
- **生成質量**: {quality_analysis}
- **穩定性**: {stability_analysis}

### 成本分析
- **本地模型**: 完全免費，無使用限制
- **雲端模型**: 按 token 計費，適合高質量需求

### 使用建議

1. **開發/測試環境**: 推薦使用本地 Ollama
   - 無成本
   - 快速響應
   - 數據隱私

2. **生產環境**: 根據需求選擇
   - **高質量需求**: 使用 Gemini
   - **成本敏感**: 使用本地模型
   - **混合模式**: 本地處理 + 雲端備份

3. **最佳實踐**
   - 簡單任務 → 本地模型
   - 複雜任務 → 雲端模型
   - 敏感數據 → 本地模型

## 配置要求

### 本地 Ollama
- Docker 容器運行
- 最低 2GB RAM
- 模型下載（首次）

### 雲端 Gemini
- Google API Key
- 網絡連接
- API 配額管理

## 下一步

1. 下載測試模型: `.\scripts\download_test_model.ps1`
2. 配置 API Key (如需要): 設置環境變量 `GOOGLE_API_KEY`
3. 運行比較測試: `python scripts/compare_llm_performance.py`
