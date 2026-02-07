# 小 j AI 學習系統實施指南

## 📋 快速開始

### 1. 初始化學習系統

```python
from sister_ai_learning_integration import enhance_ai_logic_with_learning

# Create enhanced AI with learning capabilities
ai = enhance_ai_logic_with_learning()
```

### 2. 處理用戶查詢（帶學習記錄）

```python
# Process a query
result = ai.process_query(
    user_query="我需要財務建議",
    user_id="user_001",
    domain="finance",
    user_intent="request_advice",
    tags=["budgeting", "finance"],
    model_used="local_ollama"
)

if result["success"]:
    experience_id = result["experience_id"]
    response = result["response"]
    print(f"Response: {response}")
```

### 3. 記錄用戶反饋

```python
# After user interacts with the response
feedback = ai.record_user_feedback(
    experience_id=experience_id,
    satisfaction=5,  # 1-5 scale
    comments="非常有幫助",
    effectiveness=0.9,
    action_taken=True,
    result_description="用戶實施了建議"
)
```

### 4. 運行學習循環

```python
# Periodically run learning cycle (e.g., hourly)
learning_result = ai.run_learning_cycle()

print(f"Status: {learning_result.get('status')}")
print(f"New knowledge: {learning_result.get('new_knowledge_count')}")
print(f"Patterns found: {learning_result.get('patterns')}")
```

### 5. 生成成長報告

```python
# Generate weekly/monthly growth report
report = ai.generate_growth_report()

print(f"Overall Score: {report.get('overall_growth_score')}/10")
print(f"Accuracy: {report['metrics']['accuracy']:.1%}")
print(f"User Satisfaction: {report['metrics']['user_satisfaction']:.1%}")
print(f"Milestones: {report.get('milestones')}")
print(f"Challenges: {report.get('challenges')}")
```

---

## 🔧 系統配置

### 環境變數

```bash
# Optional: Set custom memory store path
export WUCHANG_MEMORY_STORE="./memory_store"

# Optional: Enable detailed logging
export WUCHANG_LOG_LEVEL="DEBUG"
```

### 配置文件 (config.json)

```json
{
    "learning": {
        "enabled": true,
        "auto_learning_cycle": true,
        "learning_cycle_interval_seconds": 3600,
        "batch_learning": true,
        "batch_size": 100
    },
    "memory": {
        "max_experiences": 100000,
        "max_knowledge_items": 50000,
        "retention_period_days": 365,
        "auto_cleanup": true
    },
    "evaluation": {
        "enabled": true,
        "evaluation_interval_seconds": 3600,
        "metrics_update_interval_seconds": 86400
    },
    "optimization": {
        "enabled": true,
        "auto_optimization": true,
        "optimization_interval_seconds": 86400
    }
}
```

---

## 📊 監控和診斷

### 檢查知識庫統計

```python
stats = ai.get_knowledge_stats()
print(f"Total items: {stats['stats']['total_items']}")
print(f"By category: {stats['stats']['by_category']}")
print(f"Avg effectiveness: {stats['stats']['avg_effectiveness']:.2f}")
```

### 搜索知識庫

```python
results = ai.search_knowledge(
    query="預算",
    category="finance",
    limit=5
)

for item in results["results"]:
    print(f"- {item['title']}: {item['content'][:100]}...")
```

### 手動添加知識

```python
knowledge_id = ai.add_knowledge(
    category="finance",
    title="季度預算編制最佳實踐",
    content="詳細的預算編制流程...",
    confidence_score=0.9,
    tags=["budgeting", "quarterly", "best_practice"]
)

print(f"Knowledge added: {knowledge_id}")
```

---

## 🔄 集成到現有系統

### 與 Odoo 模型集成

```python
# In wuchang_os/addons/wuchang_core/models/ai_logic.py

from sister_ai_learning_integration import enhance_ai_logic_with_learning

class WuchangAILogicEnhanced:
    def __init__(self):
        self.learning_ai = enhance_ai_logic_with_learning()

    def analyze_operations_with_learning(self, context_text):
        """Enhanced analysis with learning"""
        # Process with learning
        result = self.learning_ai.process_query(
            user_query=context_text,
            user_id=self.env.user.id,
            domain="operations",
            user_intent="analysis"
        )

        return result["response"] if result["success"] else None
```

### 與 Streamlit 應用集成

```python
# In sister_agent.py or similar

import streamlit as st
from sister_ai_learning_integration import enhance_ai_logic_with_learning

# Initialize in session state
if 'ai' not in st.session_state:
    st.session_state.ai = enhance_ai_logic_with_learning()

ai = st.session_state.ai

# Process query
if user_input := st.text_input("Ask小j:"):
    result = ai.process_query(
        user_query=user_input,
        user_id=st.session_state.get('user_id', 'anonymous'),
        domain="general",
        user_intent="chat"
    )

    if result["success"]:
        st.write(result["response"])

        # Feedback collection
        satisfaction = st.slider("滿意度", 1, 5)
        if st.button("提交反饋"):
            ai.record_user_feedback(
                experience_id=result["experience_id"],
                satisfaction=satisfaction
            )
```

---

## 📈 成長指標解釋

### 核心指標

| 指標                  | 含義       | 目標    | 解釋                    |
| --------------------- | ---------- | ------- | ----------------------- |
| **Accuracy**          | 回應準確性 | > 85%   | AI 提供的信息正確度     |
| **Relevance**         | 相關性     | > 0.85  | 回應與查詢的關聯度      |
| **User Satisfaction** | 用戶滿意度 | > 4.0/5 | 用戶對回應的滿意度      |
| **Response Quality**  | 回應品質   | > 0.85  | 回應的整體質量          |
| **Learning Progress** | 學習進度   | > 0.75  | AI 的學習和成長速度     |
| **Knowledge Util.**   | 知識利用率 | > 0.80  | AI 有效使用知識庫的程度 |

### 成長維度

| 維度                   | 描述               | 監控 |
| ---------------------- | ------------------ | ---- |
| **Knowledge Depth**    | 特定領域的專業程度 | 月   |
| **Knowledge Breadth**  | 涵蓋的領域寬度     | 月   |
| **Reasoning**          | 推理和邏輯能力     | 周   |
| **User Understanding** | 對用戶需求的理解   | 周   |
| **Adaptability**       | 適應新情況的能力   | 月   |
| **Reliability**        | 一致性和可靠性     | 周   |

---

## 🚨 故障排查

### 問題：知識庫不增長

**症狀**：新知識項目未被創建

**檢查清單**：

1. 確認學習循環已啟用
2. 檢查是否有足夠的經驗數據
3. 驗證知識提取的置信度閾值
4. 查看學習日誌找出錯誤

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 問題：低滿意度評分

**症狀**：用戶反饋顯示低滿意度

**檢查清單**：

1. 查看回應相關性分數
2. 檢查知識庫中的相關項目數
3. 驗證領域特定的性能
4. 考慮添加更多訓練數據

```python
# Analyze by domain
for domain in ["finance", "property", "volunteer"]:
    result = ai.search_knowledge(
        query="general_question",
        category=domain
    )
    print(f"{domain}: {len(result['results'])} items")
```

### 問題：高記憶使用量

**症狀**：內存和磁盤使用量快速增長

**檢查清單**：

1. 檢查是否啟用了自動清理
2. 驗證保留期設置
3. 考慮歸檔舊數據
4. 實施數據壓縮

```python
# Manual cleanup
from sister_learning_engine import ExperienceRecorder
recorder = ExperienceRecorder()
# Implement archival of experiences older than 1 year
```

---

## 📚 高級主題

### 自定義學習策略

```python
class CustomLearningStrategy:
    """Implement domain-specific learning"""

    def extract_financial_patterns(self, experiences):
        # Custom logic for financial domain
        pass

    def extract_volunteer_patterns(self, experiences):
        # Custom logic for volunteer domain
        pass
```

### 多域協作學習

```python
# Transfer learning between domains
finance_knowledge = ai.search_knowledge("budget", "finance")

# Apply finance insights to property domain
property_context = {
    "finance_insights": finance_knowledge,
    "domain": "property"
}
```

### 外部知識集成

```python
# Import knowledge from external sources
external_data = load_external_knowledge("https://api.example.com")

for item in external_data:
    ai.add_knowledge(
        category=item["category"],
        title=item["title"],
        content=item["content"],
        confidence_score=0.85,
        tags=item.get("tags", [])
    )
```

---

## 🎯 最佳實踐

### 定期維護

```python
# Weekly maintenance script
def weekly_maintenance():
    ai = enhance_ai_logic_with_learning()

    # Run learning cycle
    ai.run_learning_cycle()

    # Generate report
    report = ai.generate_growth_report()

    # Archive reports
    save_report_archive(report)

    # Optimize knowledge base
    optimize_knowledge_base()
```

### 設置自動化

```bash
# Add to crontab for hourly learning cycles
0 * * * * python -c "from sister_ai_learning_integration import enhance_ai_logic_with_learning; enhance_ai_logic_with_learning().run_learning_cycle()"

# Daily growth reports
0 2 * * * python -c "from sister_ai_learning_integration import enhance_ai_logic_with_learning; enhance_ai_logic_with_learning().generate_growth_report()"
```

### 監控和警報

```python
def monitor_ai_health():
    """Monitor AI system health"""
    ai = enhance_ai_logic_with_learning()
    report = ai.generate_growth_report()

    if report["overall_growth_score"] < 6.0:
        alert("AI performance degrading")

    if len(report["challenges"]) > 3:
        alert("Multiple performance issues detected")
```

---

## 📞 支持和反饋

-   查看日誌：`./memory_store/learning_logs/`
-   檢查儀表板：`./memory_store/dashboards/`
-   訪問知識庫：`./memory_store/knowledge/`
-   反饋數據：`./memory_store/feedback/`

---

**最後更新**：2026 年 1 月 10 日
