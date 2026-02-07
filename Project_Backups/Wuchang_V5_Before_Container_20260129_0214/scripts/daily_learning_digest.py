#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小j 每日學習摘要生成器
分析當日互動記錄,提取模式,更新決策知識庫
"""
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DailyLearning')

# 路徑配置
BASE_DIR = Path(__file__).parent.parent
EXPERIENCE_DIR = BASE_DIR / 'memory_store' / 'experience'
REPORTS_DIR = BASE_DIR / 'memory_store' / 'reports'
AI_USAGE_LOG = BASE_DIR / 'memory_store' / 'ai_usage_log.json'

# 確保目錄存在
EXPERIENCE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class DailyLearningDigest:
    """每日學習摘要"""

    def __init__(self, date: str = None):
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.interaction_log_path = EXPERIENCE_DIR / \
            f'interaction_log_{self.date.replace("-", "")}.jsonl'
        self.decision_patterns_path = EXPERIENCE_DIR / 'decision_patterns.json'
        self.user_preferences_path = EXPERIENCE_DIR / 'user_preferences.json'
        self.learned_skills_path = EXPERIENCE_DIR / 'learned_skills.json'

    def load_interactions(self) -> List[Dict[str, Any]]:
        """載入當日互動記錄"""
        interactions = []
        if self.interaction_log_path.exists():
            with open(self.interaction_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        interactions.append(json.loads(line.strip()))
                    except:
                        pass
        logger.info(f'載入 {len(interactions)} 筆互動記錄')
        return interactions

    def load_ai_usage(self) -> List[Dict[str, Any]]:
        """載入 AI 使用記錄"""
        usage = []
        if AI_USAGE_LOG.exists():
            with open(AI_USAGE_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        # 只取當日
                        if entry['timestamp'].startswith(self.date):
                            usage.append(entry)
                    except:
                        pass
        logger.info(f'載入 {len(usage)} 筆 AI 使用記錄')
        return usage

    def analyze_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """分析互動模式"""
        patterns = {
            'total_interactions': len(interactions),
            'task_type_distribution': {},
            'time_distribution': {},
            'response_quality': {'positive': 0, 'negative': 0, 'neutral': 0},
            'common_topics': []
        }

        for inter in interactions:
            # 任務類型分佈
            task_type = inter.get('task_type', 'unknown')
            patterns['task_type_distribution'][task_type] = patterns['task_type_distribution'].get(
                task_type, 0) + 1

            # 時間分佈
            timestamp = inter.get('timestamp', '')
            if timestamp:
                try:
                    hour = datetime.fromisoformat(timestamp).hour
                    time_slot = 'morning' if 6 <= hour < 12 else 'afternoon' if 12 <= hour < 18 else 'evening'
                    patterns['time_distribution'][time_slot] = patterns['time_distribution'].get(
                        time_slot, 0) + 1
                except:
                    pass

            # 回應品質 (根據 feedback)
            feedback = inter.get('feedback', 'neutral')
            if feedback in patterns['response_quality']:
                patterns['response_quality'][feedback] += 1

        return patterns

    def analyze_costs(self, usage: List[Dict]) -> Dict[str, Any]:
        """分析成本"""
        total_cost = sum(u.get('cost', 0.0) for u in usage)
        total_tokens = sum(u.get('tokens', 0) for u in usage)

        model_usage = {}
        for u in usage:
            model = u.get('model', 'unknown')
            if model not in model_usage:
                model_usage[model] = {'count': 0, 'tokens': 0, 'cost': 0.0}
            model_usage[model]['count'] += 1
            model_usage[model]['tokens'] += u.get('tokens', 0)
            model_usage[model]['cost'] += u.get('cost', 0.0)

        return {
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'model_usage': model_usage,
            'average_cost_per_call': total_cost / len(usage) if usage else 0.0
        }

    def update_decision_patterns(self, patterns: Dict):
        """更新決策模式"""
        try:
            if self.decision_patterns_path.exists():
                with open(self.decision_patterns_path, 'r', encoding='utf-8') as f:
                    current = json.load(f)
            else:
                current = {'patterns': {}}

            # 更新互動計數
            current.setdefault('interaction_metadata', {})
            current['interaction_metadata']['total_interactions'] = current['interaction_metadata'].get(
                'total_interactions', 0) + patterns['total_interactions']
            current['interaction_metadata']['last_updated'] = datetime.now().isoformat()

            # 寫回
            with open(self.decision_patterns_path, 'w', encoding='utf-8') as f:
                json.dump(current, f, ensure_ascii=False, indent=2)

            logger.info('決策模式已更新')
        except Exception as e:
            logger.error(f'更新決策模式失敗: {e}')

    def generate_report(self, patterns: Dict, costs: Dict):
        """生成學習報告"""
        report_path = REPORTS_DIR / \
            f'learning_report_{self.date.replace("-", "")}.md'

        content = f"""# 小j 每日學習報告
**日期**: {self.date}  
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 一、互動摘要
- **總互動次數**: {patterns['total_interactions']}
- **任務類型分佈**:
{self._format_dict(patterns['task_type_distribution'], indent=2)}
- **時段分佈**:
{self._format_dict(patterns['time_distribution'], indent=2)}

## 二、回應品質
- ✅ 正面回饋: {patterns['response_quality']['positive']}
- ⚠️ 負面回饋: {patterns['response_quality']['negative']}
- ➖ 中性: {patterns['response_quality']['neutral']}

## 三、成本分析
- **總成本**: ${costs['total_cost']:.6f}
- **總 Token 數**: {costs['total_tokens']:,}
- **平均每次成本**: ${costs['average_cost_per_call']:.6f}

### 模型使用明細
{self._format_model_usage(costs['model_usage'])}

## 四、今日學習重點
{self._generate_learning_insights(patterns)}

## 五、明日改進目標
{self._generate_improvement_goals(patterns, costs)}

---
**小j 的話**: 今天又學到了新東西,明天會做得更好！
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f'學習報告已生成: {report_path}')
        return report_path

    def _format_dict(self, d: Dict, indent: int = 0) -> str:
        """格式化字典為 Markdown 列表"""
        lines = []
        for k, v in d.items():
            lines.append(f"{'  ' * indent}- **{k}**: {v}")
        return '\n'.join(lines) if lines else '  - (無資料)'

    def _format_model_usage(self, usage: Dict) -> str:
        """格式化模型使用"""
        lines = ['| 模型 | 呼叫次數 | Token 數 | 成本 |',
                 '|------|---------|---------|------|']
        for model, data in usage.items():
            lines.append(
                f"| {model} | {data['count']} | {data['tokens']:,} | ${data['cost']:.6f} |")
        return '\n'.join(lines) if len(lines) > 2 else '(無資料)'

    def _generate_learning_insights(self, patterns: Dict) -> str:
        """生成學習洞察"""
        insights = []

        # 根據時段分佈給建議
        time_dist = patterns.get('time_distribution', {})
        if time_dist:
            max_time = max(time_dist, key=time_dist.get)
            insights.append(f"- 哥哥在 **{max_time}** 時段最活躍,未來可優化此時段的回應速度。")

        # 根據任務類型給建議
        task_dist = patterns.get('task_type_distribution', {})
        if task_dist:
            max_task = max(task_dist, key=task_dist.get)
            insights.append(f"- 最常處理的任務是 **{max_task}**,應強化相關技能。")

        return '\n'.join(insights) if insights else '- (今日互動較少,無明顯模式)'

    def _generate_improvement_goals(self, patterns: Dict, costs: Dict) -> str:
        """生成改進目標"""
        goals = []

        # 成本優化
        if costs['total_cost'] > 0.5:
            goals.append('- 優化推理路由,增加本地模型使用比例以降低成本。')

        # 回應品質
        quality = patterns['response_quality']
        if quality['negative'] > quality['positive']:
            goals.append('- 提升回應品質,減少負面反饋。')

        # 預設目標
        goals.append('- 持續累積互動記錄,強化模式識別能力。')

        return '\n'.join(goals)

    def run(self):
        """執行每日學習摘要"""
        logger.info(f'開始分析 {self.date} 的學習記錄...')

        interactions = self.load_interactions()
        usage = self.load_ai_usage()

        if not interactions and not usage:
            logger.warning('今日無互動記錄,跳過分析')
            return

        patterns = self.analyze_patterns(interactions)
        costs = self.analyze_costs(usage)

        self.update_decision_patterns(patterns)
        report_path = self.generate_report(patterns, costs)

        logger.info(f'✅ 每日學習摘要完成: {report_path}')


if __name__ == '__main__':
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else None
    digest = DailyLearningDigest(date)
    digest.run()
