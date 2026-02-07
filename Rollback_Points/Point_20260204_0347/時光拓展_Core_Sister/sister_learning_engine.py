"""
小j 經驗記錄和學習系統
Wuchang AI Experience & Learning System

This module handles:
- Experience recording and storage
- Knowledge base management
- Learning cycle orchestration
- Feedback collection and analysis
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import uuid
from collections import defaultdict
import statistics
import logging

_logger = logging.getLogger(__name__)


class ExperienceRecorder:
    """Records and stores AI interactions and experiences"""

    def __init__(self, base_path: str = "./memory_store/experiences"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def record_experience(
        self,
        interaction_type: str,
        context: Dict[str, Any],
        ai_response: str,
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Records a single AI interaction experience

        Args:
            interaction_type: 'user_query', 'system_event', 'feedback'
            context: {'user_id', 'domain', 'query', 'intent', ...}
            ai_response: The response content and metadata
            user_feedback: {'satisfaction': 1-5, 'comments': str, ...}

        Returns:
            experience_id: Unique identifier for this experience
        """
        experience_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        experience = {
            "id": experience_id,
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "context": context,
            "ai_response": {
                "content": ai_response.get("content", ""),
                "confidence": ai_response.get("confidence", 0.5),
                "model_used": ai_response.get("model_used", "unknown"),
                "reasoning": ai_response.get("reasoning", "")
            },
            "outcome": user_feedback or {
                "user_satisfaction": 0,
                "effectiveness": 0
            },
            "metadata": {
                "tokens_used": ai_response.get("tokens_used", 0),
                "response_time_ms": ai_response.get("response_time_ms", 0),
                "tags": context.get("tags", [])
            }
        }

        # Save to date-based directory
        date_dir = self.base_path / datetime.now().strftime("%Y-%m")
        date_dir.mkdir(parents=True, exist_ok=True)

        filepath = date_dir / f"{experience_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(experience, f, ensure_ascii=False, indent=2)

        _logger.info(f"Experience recorded: {experience_id}")
        return experience_id

    def get_experiences(
        self,
        domain: Optional[str] = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Retrieves experiences from the past N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        experiences = []

        for json_file in self.base_path.rglob("*.json"):
            if json_file.is_file():
                file_date = datetime.fromisoformat(
                    json_file.parent.name.replace("-", "-") + "-01"
                )

                if file_date >= cutoff_date:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        exp = json.load(f)
                        if domain is None or exp.get("context", {}).get("domain") == domain:
                            experiences.append(exp)

        return sorted(experiences, key=lambda x: x["timestamp"])


class KnowledgeBase:
    """Manages the AI's knowledge base and learning"""

    def __init__(self, base_path: str = "./memory_store/knowledge"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.knowledge_cache = {}  # In-memory cache for performance

    def add_knowledge(
        self,
        category: str,
        title: str,
        content: str,
        confidence_score: float = 0.8,
        source: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Adds new knowledge to the base

        Args:
            category: knowledge domain (finance, property, volunteer, pos)
            title: knowledge title
            content: detailed knowledge content
            confidence_score: confidence level 0-1
            source: {'origin', 'experience_ids', ...}
            tags: list of tags for categorization

        Returns:
            knowledge_id: unique identifier
        """
        knowledge_id = f"kn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        knowledge = {
            "id": knowledge_id,
            "category": category,
            "title": title,
            "content": content,
            "source": source or {
                "origin": "manual",
                "experience_ids": [],
                "confidence_score": confidence_score
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "usage_count": 0,
                "effectiveness_rating": 0.0,
                "tags": tags or []
            },
            "version": 1,
            "related_knowledge": []
        }

        # Save to category-based directory
        category_dir = self.base_path / category
        category_dir.mkdir(parents=True, exist_ok=True)

        filepath = category_dir / f"{knowledge_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, ensure_ascii=False, indent=2)

        self.knowledge_cache[knowledge_id] = knowledge
        _logger.info(f"Knowledge added: {knowledge_id}")
        return knowledge_id

    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search knowledge base by title or content"""
        results = []

        search_dir = self.base_path / category if category else self.base_path

        for json_file in search_dir.rglob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)

                # Simple text matching (could be enhanced with semantic search)
                if (query.lower() in knowledge.get("title", "").lower() or
                        query.lower() in knowledge.get("content", "").lower()):
                    results.append(knowledge)

        # Sort by effectiveness and usage
        results.sort(
            key=lambda x: (
                x.get("metadata", {}).get("effectiveness_rating", 0),
                -x.get("metadata", {}).get("usage_count", 0)
            ),
            reverse=True
        )

        return results[:limit]

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get overall knowledge base statistics"""
        stats = {
            "total_items": 0,
            "by_category": defaultdict(int),
            "avg_effectiveness": 0.0,
            "avg_confidence": 0.0,
            "total_usage_count": 0
        }

        effectiveness_scores = []
        confidence_scores = []

        for json_file in self.base_path.rglob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)
                stats["total_items"] += 1
                stats["by_category"][knowledge.get("category")] += 1

                effectiveness = knowledge.get(
                    "metadata", {}).get("effectiveness_rating", 0)
                effectiveness_scores.append(effectiveness)

                confidence = knowledge.get("source", {}).get(
                    "confidence_score", 0.5)
                confidence_scores.append(confidence)

                stats["total_usage_count"] += knowledge.get(
                    "metadata", {}).get("usage_count", 0)

        if effectiveness_scores:
            stats["avg_effectiveness"] = statistics.mean(effectiveness_scores)
        if confidence_scores:
            stats["avg_confidence"] = statistics.mean(confidence_scores)

        return stats


class FeedbackCollector:
    """Collects and analyzes user feedback"""

    def __init__(self, base_path: str = "./memory_store/feedback"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def record_feedback(
        self,
        experience_id: str,
        satisfaction: int,
        comments: str = "",
        effectiveness: float = 0.5,
        action_taken: bool = False,
        result_description: str = ""
    ) -> str:
        """Record user feedback on an AI response"""
        feedback_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        feedback = {
            "id": feedback_id,
            "experience_id": experience_id,
            "timestamp": datetime.now().isoformat(),
            "rating": {
                "satisfaction": min(5, max(1, satisfaction)),  # 1-5
                "effectiveness": min(1.0, max(0.0, effectiveness)),  # 0-1
                "comments": comments
            },
            "action": {
                "taken": action_taken,
                "description": result_description
            }
        }

        # Save to date-based directory
        date_dir = self.base_path / datetime.now().strftime("%Y-%m")
        date_dir.mkdir(parents=True, exist_ok=True)

        filepath = date_dir / f"{feedback_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, ensure_ascii=False, indent=2)

        _logger.info(f"Feedback recorded: {feedback_id}")
        return feedback_id

    def get_feedback_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get feedback statistics for recent period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        satisfaction_scores = []
        effectiveness_scores = []
        action_count = 0

        for json_file in self.base_path.rglob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                feedback = json.load(f)

                if datetime.fromisoformat(feedback["timestamp"]) >= cutoff_date:
                    satisfaction_scores.append(
                        feedback["rating"]["satisfaction"])
                    effectiveness_scores.append(
                        feedback["rating"]["effectiveness"])
                    if feedback["action"]["taken"]:
                        action_count += 1

        stats = {
            "period_days": days,
            "total_feedbacks": len(satisfaction_scores),
            "avg_satisfaction": statistics.mean(satisfaction_scores) if satisfaction_scores else 0,
            "avg_effectiveness": statistics.mean(effectiveness_scores) if effectiveness_scores else 0,
            "actions_taken_count": action_count,
            "action_rate": action_count / len(satisfaction_scores) if satisfaction_scores else 0
        }

        return stats


class LearningEngine:
    """Orchestrates the learning cycle"""

    def __init__(
        self,
        experience_recorder: ExperienceRecorder,
        knowledge_base: KnowledgeBase,
        feedback_collector: FeedbackCollector
    ):
        self.experience_recorder = experience_recorder
        self.knowledge_base = knowledge_base
        self.feedback_collector = feedback_collector
        self.learning_log = Path("./memory_store/learning_logs")
        self.learning_log.mkdir(parents=True, exist_ok=True)

    def analyze_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze patterns from recent experiences"""
        experiences = self.experience_recorder.get_experiences(days=days)

        patterns = {
            "timestamp": datetime.now().isoformat(),
            "period_days": days,
            "total_experiences": len(experiences),
            "by_domain": defaultdict(list),
            "by_type": defaultdict(int),
            "success_rate": 0.0,
            "common_intents": defaultdict(int),
            "knowledge_gaps": []
        }

        for exp in experiences:
            domain = exp.get("context", {}).get("domain", "unknown")
            patterns["by_domain"][domain].append(exp)
            patterns["by_type"][exp.get("type")] += 1

            intent = exp.get("context", {}).get("user_intent")
            if intent:
                patterns["common_intents"][intent] += 1

        # Calculate success rate
        successful = sum(
            1 for exp in experiences
            if exp.get("outcome", {}).get("user_satisfaction", 0) >= 4
        )
        if experiences:
            patterns["success_rate"] = successful / len(experiences)

        return patterns

    def extract_new_knowledge(
        self,
        pattern_analysis: Dict[str, Any]
    ) -> List[str]:
        """Extract new knowledge from pattern analysis"""
        new_knowledge_ids = []

        # Example: If success rate is high on a domain, create knowledge about best practices
        for domain, exps in pattern_analysis["by_domain"].items():
            if len(exps) >= 3:  # Minimum samples
                success_rate = sum(
                    1 for e in exps if e.get("outcome", {}).get("user_satisfaction", 0) >= 4
                ) / len(exps)

                if success_rate >= 0.8:
                    # Create knowledge about successful patterns in this domain
                    knowledge_id = self.knowledge_base.add_knowledge(
                        category=domain,
                        title=f"Best practice for {domain}",
                        content=f"Observed success rate: {success_rate:.1%}. "
                        f"Total interactions: {len(exps)}",
                        confidence_score=success_rate,
                        source={
                            "origin": "pattern_analysis",
                            "experience_ids": [e["id"] for e in exps],
                            "confidence_score": success_rate
                        },
                        tags=["pattern", "best_practice"]
                    )
                    new_knowledge_ids.append(knowledge_id)

        return new_knowledge_ids

    def run_learning_cycle(self) -> Dict[str, Any]:
        """Execute a complete learning cycle"""
        cycle_id = f"lc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Step 1: Analyze patterns
            patterns = self.analyze_patterns(days=7)

            # Step 2: Extract new knowledge
            new_knowledge = self.extract_new_knowledge(patterns)

            # Step 3: Get feedback stats
            feedback_stats = self.feedback_collector.get_feedback_stats(days=7)

            # Step 4: Get knowledge stats
            kb_stats = self.knowledge_base.get_knowledge_stats()

            # Step 5: Compile results
            learning_result = {
                "cycle_id": cycle_id,
                "timestamp": datetime.now().isoformat(),
                "patterns": patterns,
                "new_knowledge_count": len(new_knowledge),
                "new_knowledge_ids": new_knowledge,
                "feedback_stats": feedback_stats,
                "knowledge_stats": kb_stats,
                "status": "completed"
            }

            # Save learning log
            log_file = self.learning_log / \
                f"{datetime.now().strftime('%Y-%m-%d')}.json"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(learning_result, ensure_ascii=False) + "\n")

            _logger.info(f"Learning cycle completed: {cycle_id}")
            return learning_result

        except Exception as e:
            _logger.error(f"Learning cycle failed: {e}")
            return {
                "cycle_id": cycle_id,
                "status": "failed",
                "error": str(e)
            }


# Convenience functions
def create_learning_system(base_path: str = "./memory_store") -> tuple:
    """Create and return all learning system components"""
    experience_recorder = ExperienceRecorder(f"{base_path}/experiences")
    knowledge_base = KnowledgeBase(f"{base_path}/knowledge")
    feedback_collector = FeedbackCollector(f"{base_path}/feedback")
    learning_engine = LearningEngine(
        experience_recorder,
        knowledge_base,
        feedback_collector
    )

    return experience_recorder, knowledge_base, feedback_collector, learning_engine
