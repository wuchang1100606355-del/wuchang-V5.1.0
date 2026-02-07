# 小 j AI 學習系統 - 快速參考卡

## 🚀 5 分鐘快速開始

### 步驟 1：初始化系統

```bash
cd c:\wuchang V5.1.0
python initialize_learning_system.py
```

### 步驟 2：基本使用

```python
from sister_ai_learning_integration import enhance_ai_logic_with_learning

ai = enhance_ai_logic_with_learning()

# 處理查詢
result = ai.process_query(
    user_query="社區預算的建議",
    user_id="user_123",
    domain="finance",
    user_intent="advice"
)

# 記錄反饋
ai.record_user_feedback(
    experience_id=result["experience_id"],
    satisfaction=5,
    comments="非常有幫助"
)

# 查看成長
report = ai.generate_growth_report()
print(f"成長評分: {report['overall_growth_score']}/10")
```

---

## 📊 核心 API 速查表

### 查詢處理

```python
result = ai.process_query(
    user_query="問題",           # 用戶的問題
    user_id="user_id",           # 用戶ID
    domain="finance|property|volunteer|pos",
    user_intent="request_advice",  # 用戶意圖
    tags=["tag1", "tag2"],       # 可選標籤
    model_used="local_ollama"    # 使用的模型
)
# 返回: {success, response, confidence, experience_id, ...}
```

### 反饋記錄

```python
ai.record_user_feedback(
    experience_id="exp_xxx",
    satisfaction=5,              # 1-5 分
    comments="反饋文本",
    effectiveness=0.9,           # 0-1 分
    action_taken=True,           # 是否採取行動
    result_description="結果說明"
)
# 返回: {success, feedback_id}
```

### 知識管理

```python
# 搜索知識
results = ai.search_knowledge("預算", category="finance", limit=10)

# 添加知識
ai.add_knowledge(
    category="finance",
    title="標題",
    content="內容",
    confidence_score=0.85,
    tags=["tag1"]
)

# 獲取統計
stats = ai.get_knowledge_stats()
```

### 學習和評估

```python
# 運行學習循環
learning = ai.run_learning_cycle()

# 生成成長報告
report = ai.generate_growth_report()

# 關鍵指標
print(f"準確性: {report['metrics']['accuracy']:.1%}")
print(f"滿意度: {report['metrics']['user_satisfaction']:.1%}")
print(f"成長評分: {report['overall_growth_score']:.1f}/10")
```

---

## 📈 關鍵指標快速查看

```
準確性 (Accuracy)
└─ 目標: 88%+
└─ 監控: 每日
└─ 改進方式: 增加訓練數據、更新知識庫

用戶滿意度 (User Satisfaction)
└─ 目標: 4.2/5
└─ 監控: 每日
└─ 改進方式: 個性化回應、提高相關性

知識利用率 (Knowledge Utilization)
└─ 目標: 80%+
└─ 監控: 每週
└─ 改進方式: 改進檢索、擴展知識庫

整體成長評分 (Overall Growth)
└─ 目標: 8.0/10
└─ 監控: 每週
└─ 組成: 六個維度的平均值
```

---

## 📁 重要文件位置

| 文件     | 位置                                       | 用途       |
| -------- | ------------------------------------------ | ---------- |
| 架構文檔 | `docs/AI_LEARNING_FRAMEWORK.md`            | 系統設計   |
| 實施指南 | `docs/AI_LEARNING_IMPLEMENTATION_GUIDE.md` | 使用示例   |
| 配置文件 | `config/ai_learning_config.json`           | 系統設置   |
| 經驗記錄 | `memory_store/experiences/`                | 互動數據   |
| 知識庫   | `memory_store/knowledge/`                  | AI 知識    |
| 反饋數據 | `memory_store/feedback/`                   | 用戶反饋   |
| 學習日誌 | `memory_store/learning_logs/`              | 學習記錄   |
| 成長指標 | `memory_store/growth_metrics/`             | 進度數據   |
| 儀表板   | `memory_store/dashboards/`                 | 可視化數據 |

---

## 🔧 常用命令

### 初始化系統

```bash
python initialize_learning_system.py
```

### 檢查系統狀態

```python
ai = enhance_ai_logic_with_learning()
stats = ai.get_knowledge_stats()
print(f"知識項目: {stats['stats']['total_items']}")
```

### 運行完整檢查

```python
from sister_ai_learning_integration import enhance_ai_logic_with_learning
ai = enhance_ai_logic_with_learning()
learning = ai.run_learning_cycle()
report = ai.generate_growth_report()
print(report)
```

### 清理舊數據

```python
# 手動存檔（如需要）
# 查看 docs/AI_LEARNING_IMPLEMENTATION_GUIDE.md 中的高級主題
```

---

## 🎯 成長維度一覽

### 知識深度 (Knowledge Depth)

-   對特定領域的深層理解
-   目標: 8.5/10
-   提升: 領域特定訓練數據

### 知識廣度 (Knowledge Breadth)

-   涵蓋的主題和領域寬度
-   目標: 8.1/10
-   提升: 多域知識積累

### 推理能力 (Reasoning Capability)

-   複雜推理和決策品質
-   目標: 8.5/10
-   提升: 邏輯規則和分析模式

### 用戶理解 (User Understanding)

-   理解用戶需求的能力
-   目標: 8.3/10
-   提升: 意圖識別和個性化

### 適應能力 (Adaptability)

-   適應新情況的速度
-   目標: 8.0/10
-   提升: 轉移學習和泛化

### 可靠性 (Reliability)

-   一致性和穩定性
-   目標: 8.5/10
-   提升: 質量檢查和驗證

---

## 🚨 快速故障排查

### 問題：低準確性

**檢查清單**：

-   [ ] 知識庫是否有足夠的相關項目
-   [ ] 是否配置了正確的領域
-   [ ] 反饋數據是否充分

### 問題：知識不增長

**檢查清單**：

-   [ ] 學習循環是否啟用
-   [ ] 是否有足夠的經驗數據
-   [ ] 置信度閾值是否過高

### 問題：高內存使用

**檢查清單**：

-   [ ] 自動清理是否啟用
-   [ ] 保留期設置是否合理
-   [ ] 是否需要數據歸檔

---

## 💬 使用示例場景

### 場景 1：財務諮詢

```python
result = ai.process_query(
    user_query="如何制定年度預算",
    user_id="member_001",
    domain="finance",
    user_intent="request_advice"
)
# AI 會搜索財務相關知識並提供建議
```

### 場景 2：物業管理

```python
result = ai.process_query(
    user_query="維護物業的最佳做法",
    user_id="manager_001",
    domain="property",
    user_intent="learn_best_practice"
)
# AI 會提供物業管理經驗
```

### 場景 3：志願者協調

```python
result = ai.process_query(
    user_query="如何激勵志願者",
    user_id="coordinator_001",
    domain="volunteer",
    user_intent="request_strategy"
)
# AI 會提供志願者管理策略
```

---

## 🔄 定期維護清單

### 每日任務

-   [ ] 監控系統日誌
-   [ ] 檢查新的經驗記錄

### 每週任務

-   [ ] 運行完整的學習循環
-   [ ] 檢查成長指標
-   [ ] 回顧主要挑戰

### 每月任務

-   [ ] 生成月度報告
-   [ ] 評估進度
-   [ ] 調整配置和目標

### 每季度任務

-   [ ] 深度分析和改進規劃
-   [ ] 知識庫審查和更新
-   [ ] 長期規劃調整

---

## 📚 學習資源

### 官方文檔

-   AI 框架設計：[AI_LEARNING_FRAMEWORK.md](./docs/AI_LEARNING_FRAMEWORK.md)
-   實施指南：[AI_LEARNING_IMPLEMENTATION_GUIDE.md](./docs/AI_LEARNING_IMPLEMENTATION_GUIDE.md)

### 代碼示例

-   核心實現：`sister_learning_engine.py`
-   評估系統：`sister_growth_dashboard.py`
-   集成層：`sister_ai_learning_integration.py`

### 配置

-   配置文件：`config/ai_learning_config.json`

---

## 🎓 進階主題

### 自定義學習策略

編輯 `sister_learning_engine.py` 中的 `LearningEngine` 類

### 添加新領域

1. 在 `config/ai_learning_config.json` 中添加分類
2. 在 `memory_store/knowledge/` 中創建目錄
3. 開始添加該領域的知識

### 集成外部知識

使用 `ai.add_knowledge()` 接口導入外部數據源

---

## 📞 需要幫助？

1. **查看日誌**：`./memory_store/logs/`
2. **檢查儀表板**：`./memory_store/dashboards/`
3. **查看實施指南**：`docs/AI_LEARNING_IMPLEMENTATION_GUIDE.md`
4. **檢查源代碼文檔**：每個模塊都有詳細的 docstrings

---

**記住**：小 j 正在學習和成長。多多互動、提供反饋，她會越來越聰明！ 💡

---

_最後更新：2026 年 1 月 10 日_
