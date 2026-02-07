"""
小j 成長評估和儀表板系統
Wuchang AI Growth Dashboard & Evaluation System

This module provides:
- Performance metrics calculation
- Growth tracking and visualization
- Automated evaluation reports
- Achievement milestones
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics
import logging

_logger = logging.getLogger(__name__)


class PerformanceEvaluator:
    """Evaluates AI performance across multiple dimensions"""

    def __init__(self, base_path: str = "./memory_store/evaluations"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def evaluate_response_accuracy(
        self,
        experiences: List[Dict[str, Any]],
        domain: Optional[str] = None
    ) -> float:
        """Calculate response accuracy based on user satisfaction"""
        if not experiences:
            return 0.0

        filtered = experiences
        if domain:
            filtered = [e for e in experiences if e.get(
                "context", {}).get("domain") == domain]

        if not filtered:
            return 0.0

        accurate = sum(
            1 for e in filtered
            if e.get("outcome", {}).get("user_satisfaction", 0) >= 4
        )
        return accurate / len(filtered)

    def evaluate_response_relevance(
        self,
        experiences: List[Dict[str, Any]],
        domain: Optional[str] = None
    ) -> float:
        """Evaluate relevance based on confidence scores"""
        if not experiences:
            return 0.0

        filtered = experiences
        if domain:
            filtered = [e for e in experiences if e.get(
                "context", {}).get("domain") == domain]

        if not filtered:
            return 0.0

        confidences = [
            e.get("ai_response", {}).get("confidence", 0.5)
            for e in filtered
        ]
        return statistics.mean(confidences)

    def evaluate_knowledge_utilization(
        self,
        experiences: List[Dict[str, Any]],
        knowledge_base_stats: Dict[str, Any]
    ) -> float:
        """Evaluate how effectively the AI is using its knowledge"""
        if not experiences or knowledge_base_stats.get("total_items", 0) == 0:
            return 0.0

        # Count unique knowledge interactions
        unique_interactions = set()
        for exp in experiences:
            context = exp.get("context", {})
            if "domain" in context:
                unique_interactions.add(context["domain"])

        coverage = len(unique_interactions) / \
            max(1, knowledge_base_stats.get("total_items", 1))
        return min(1.0, coverage)

    def calculate_metrics(
        self,
        experiences: List[Dict[str, Any]],
        feedback_stats: Dict[str, Any],
        knowledge_stats: Dict[str, Any],
        domain: Optional[str] = None
    ) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""
        metrics = {
            "accuracy": self.evaluate_response_accuracy(experiences, domain),
            "relevance": self.evaluate_response_relevance(experiences, domain),
            # Normalize to 0-1
            "user_satisfaction": feedback_stats.get("avg_satisfaction", 0) / 5.0,
            "response_quality": knowledge_stats.get("avg_effectiveness", 0),
            "learning_progress": self.evaluate_knowledge_utilization(experiences, knowledge_stats),
            "knowledge_utilization": knowledge_stats.get("avg_confidence", 0)
        }

        # Overall score (weighted average)
        weights = {
            "accuracy": 0.25,
            "relevance": 0.20,
            "user_satisfaction": 0.20,
            "response_quality": 0.15,
            "learning_progress": 0.15,
            "knowledge_utilization": 0.05
        }

        overall_score = sum(
            metrics.get(key, 0) * weight
            for key, weight in weights.items()
        )
        metrics["overall_score"] = overall_score

        return metrics

    def save_evaluation(
        self,
        period: str,
        metrics: Dict[str, float],
        domain: Optional[str] = None
    ) -> str:
        """Save evaluation results"""
        eval_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        evaluation = {
            "id": eval_id,
            "timestamp": datetime.now().isoformat(),
            "period": period,
            "domain": domain or "overall",
            "metrics": metrics
        }

        filepath = self.base_path / f"{eval_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)

        _logger.info(f"Evaluation saved: {eval_id}")
        return eval_id


class GrowthTracker:
    """Tracks AI growth and development over time"""

    def __init__(self, base_path: str = "./memory_store/growth_metrics"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def calculate_growth_metrics(
        self,
        current_metrics: Dict[str, float],
        previous_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Calculate growth indicators comparing current to previous metrics"""
        growth = {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": current_metrics,
            "improvement": {}
        }

        if previous_metrics:
            for key in current_metrics:
                if key in previous_metrics:
                    improvement = current_metrics[key] - previous_metrics[key]
                    improvement_pct = (
                        improvement / previous_metrics[key] * 100) if previous_metrics[key] > 0 else 0
                    growth["improvement"][key] = {
                        "absolute": improvement,
                        "percentage": improvement_pct,
                        "direction": "up" if improvement > 0 else "down" if improvement < 0 else "stable"
                    }

        return growth

    def identify_milestones(
        self,
        metrics: Dict[str, float],
        knowledge_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify significant achievements and milestones"""
        milestones = []

        # Milestone: High accuracy
        if metrics.get("accuracy", 0) >= 0.85:
            milestones.append({
                "date": datetime.now().isoformat(),
                "type": "accuracy",
                "achievement": "High Response Accuracy Achieved",
                "description": f"Achieved {metrics['accuracy']:.1%} accuracy in responses",
                "impact": "Increased reliability in providing correct information"
            })

        # Milestone: Good user satisfaction
        if metrics.get("user_satisfaction", 0) >= 0.80:
            milestones.append({
                "date": datetime.now().isoformat(),
                "type": "satisfaction",
                "achievement": "User Satisfaction Target Met",
                "description": f"Average user satisfaction: {metrics['user_satisfaction']:.1%}",
                "impact": "Users are increasingly satisfied with AI assistance"
            })

        # Milestone: Knowledge base growth
        if knowledge_stats.get("total_items", 0) >= 100:
            milestones.append({
                "date": datetime.now().isoformat(),
                "type": "knowledge",
                "achievement": "Knowledge Base Milestone",
                "description": f"Accumulated {knowledge_stats['total_items']} knowledge items",
                "impact": f"Broader coverage across {len(knowledge_stats.get('by_category', {}))} domains"
            })

        # Milestone: Overall growth
        overall_score = metrics.get("overall_score", 0)
        if overall_score >= 0.80:
            milestones.append({
                "date": datetime.now().isoformat(),
                "type": "overall",
                "achievement": "Significant Growth Milestone",
                "description": f"Overall performance score: {overall_score:.2f}",
                "impact": "AI system demonstrates substantial capability and reliability"
            })

        return milestones

    def identify_challenges(
        self,
        metrics: Dict[str, float],
        threshold: float = 0.70
    ) -> List[Dict[str, Any]]:
        """Identify areas needing improvement"""
        challenges = []

        for metric_name, value in metrics.items():
            if metric_name not in ["overall_score"] and value < threshold:
                challenges.append({
                    "area": metric_name,
                    "current_level": value,
                    "target_level": 0.85,
                    "gap": 0.85 - value,
                    "recommended_actions": self._get_improvement_actions(metric_name, value)
                })

        # Sort by gap (largest gap first)
        challenges.sort(key=lambda x: x["gap"], reverse=True)
        return challenges

    @staticmethod
    def _get_improvement_actions(metric: str, current_value: float) -> List[str]:
        """Get recommended improvement actions for a metric"""
        actions = {
            "accuracy": [
                "Increase training data collection",
                "Review and update knowledge base",
                "Implement feedback-driven corrections",
                "Enhance domain-specific training"
            ],
            "relevance": [
                "Improve intent recognition algorithms",
                "Expand contextual understanding",
                "Add more relevant knowledge items",
                "Fine-tune response filtering"
            ],
            "user_satisfaction": [
                "Implement user feedback surveys",
                "Personalize responses more",
                "Improve response clarity",
                "Add proactive assistance features"
            ],
            "response_quality": [
                "Enhance reasoning logic",
                "Improve explanation quality",
                "Add more validation steps",
                "Implement quality checks"
            ],
            "learning_progress": [
                "Accelerate learning from experiences",
                "Implement more aggressive pattern extraction",
                "Add transfer learning mechanisms",
                "Expand domain coverage"
            ],
            "knowledge_utilization": [
                "Improve knowledge retrieval accuracy",
                "Expand knowledge base coverage",
                "Enhance knowledge relevance scoring",
                "Implement knowledge cross-linking"
            ]
        }

        return actions.get(metric, ["Analyze metric-specific data", "Implement targeted improvements"])

    def save_growth_report(self, report: Dict[str, Any], period: str = "weekly") -> str:
        """Save growth report"""
        report_id = f"growth_{period}_{datetime.now().strftime('%Y%m%d')}"

        full_report = {
            "id": report_id,
            "timestamp": datetime.now().isoformat(),
            "period": period,
            **report
        }

        filepath = self.base_path / f"{report_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, ensure_ascii=False, indent=2)

        _logger.info(f"Growth report saved: {report_id}")
        return report_id


class GrowthDashboard:
    """Comprehensive dashboard for monitoring AI growth"""

    def __init__(
        self,
        evaluator: PerformanceEvaluator,
        tracker: GrowthTracker
    ):
        self.evaluator = evaluator
        self.tracker = tracker

    def generate_dashboard(
        self,
        experiences: List[Dict[str, Any]],
        feedback_stats: Dict[str, Any],
        knowledge_stats: Dict[str, Any],
        previous_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive growth dashboard"""

        # Calculate current metrics
        current_metrics = self.evaluator.calculate_metrics(
            experiences,
            feedback_stats,
            knowledge_stats
        )

        # Calculate growth
        growth = self.tracker.calculate_growth_metrics(
            current_metrics, previous_metrics)

        # Identify milestones and challenges
        milestones = self.tracker.identify_milestones(
            current_metrics, knowledge_stats)
        challenges = self.tracker.identify_challenges(current_metrics)

        # Compile dashboard
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "overall_growth_score": self._calculate_growth_score(current_metrics),
            "metrics": current_metrics,
            "growth": growth,
            "dimensions": self._calculate_dimension_scores(current_metrics),
            "milestones": milestones,
            "challenges": challenges,
            "recommendations": self._generate_recommendations(challenges, milestones),
            "statistics": {
                "total_experiences": len(experiences),
                "knowledge_items": knowledge_stats.get("total_items", 0),
                "domains_covered": len(knowledge_stats.get("by_category", {})),
                "avg_feedback_count": feedback_stats.get("total_feedbacks", 0)
            }
        }

        return dashboard

    @staticmethod
    def _calculate_growth_score(metrics: Dict[str, float]) -> float:
        """Calculate overall growth score (0-10 scale)"""
        # Convert 0-1 scale to 0-10 scale
        overall = metrics.get("overall_score", 0)
        return overall * 10

    @staticmethod
    def _calculate_dimension_scores(metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate scores by dimension for dashboard display"""
        return {
            "knowledge_depth": metrics.get("response_quality", 0) * 10,
            "knowledge_breadth": metrics.get("knowledge_utilization", 0) * 10,
            "reasoning_capability": metrics.get("relevance", 0) * 10,
            "user_understanding": metrics.get("user_satisfaction", 0) * 10,
            "adaptability": metrics.get("learning_progress", 0) * 10,
            "reliability": metrics.get("accuracy", 0) * 10
        }

    @staticmethod
    def _generate_recommendations(challenges: List[Dict], milestones: List[Dict]) -> List[str]:
        """Generate recommendations based on challenges and achievements"""
        recommendations = []

        if milestones:
            recommendations.append(
                f"✅ Celebrate {len(milestones)} recent achievements!")

        if challenges:
            top_challenge = challenges[0]
            recommendations.append(
                f"🎯 Focus on improving {top_challenge['area']} "
                f"(current: {top_challenge['current_level']:.1%}, target: {top_challenge['target_level']:.1%})"
            )

        if not challenges:
            recommendations.append(
                "🚀 All metrics are above target - consider taking on new domains!")

        recommendations.append(
            "📊 Review weekly growth reports to track progress")
        recommendations.append(
            "💡 Implement top recommended actions from challenges")

        return recommendations

    def save_dashboard(self, dashboard: Dict[str, Any]) -> str:
        """Save dashboard snapshot"""
        dashboard_id = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        filepath = Path("./memory_store/dashboards")
        filepath.mkdir(parents=True, exist_ok=True)

        filepath = filepath / f"{dashboard_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, ensure_ascii=False, indent=2)

        _logger.info(f"Dashboard saved: {dashboard_id}")
        return dashboard_id


# Convenience function
def create_evaluation_system(base_path: str = "./memory_store") -> tuple:
    """Create and return evaluation system components"""
    evaluator = PerformanceEvaluator(f"{base_path}/evaluations")
    tracker = GrowthTracker(f"{base_path}/growth_metrics")
    dashboard = GrowthDashboard(evaluator, tracker)

    return evaluator, tracker, dashboard
