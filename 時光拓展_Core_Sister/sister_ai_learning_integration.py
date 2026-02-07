"""
小j AI 學習集成層
Wuchang AI Learning Integration Layer

This module integrates the learning system with the existing AI logic
and provides enhanced AI responses with learning capabilities.
"""

import logging
import sys
import os
import glob
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Add wuchang_tools_library to path to import CloudLittleJBrain
TOOLS_LIB_PATH = os.path.join(os.getcwd(), 'wuchang_tools_library')
if TOOLS_LIB_PATH not in sys.path:
    sys.path.append(TOOLS_LIB_PATH)

try:
    from cloud_little_j_intelligence import CloudLittleJBrain
except ImportError:
    # Fallback or placeholder if file missing
    class CloudLittleJBrain:
        def __init__(self, api_key=None): pass
        def scan_tools(self): return []
        def generate_index(self): return {}
        def update_audit_log(self): pass

from sister_learning_engine import (
    ExperienceRecorder, KnowledgeBase, FeedbackCollector,
    LearningEngine, create_learning_system
)
from sister_growth_dashboard import (
    PerformanceEvaluator, GrowthTracker, GrowthDashboard,
    create_evaluation_system
)
from google_tasks_manager import GoogleTasksManager

_logger = logging.getLogger(__name__)


class EnhancedAILogic:
    """
    Enhanced AI Logic with learning capabilities
    Extends the basic AI logic with:
    - Experience recording
    - Knowledge base retrieval
    - Learning from feedback
    - Performance tracking
    - Google Tasks Integration
    """

    def __init__(self, base_learning_path: str = "./memory_store"):
        # Initialize learning components
        (self.experience_recorder,
         self.knowledge_base,
         self.feedback_collector,
         self.learning_engine) = create_learning_system(base_learning_path)

        # Initialize evaluation components
        (self.evaluator,
         self.tracker,
         self.dashboard) = create_evaluation_system(base_learning_path)
         
        # Initialize Google Tasks Manager
        self.tasks_manager = GoogleTasksManager()

        # Initialize Cloud Little J Brain (Intelligence Core)
        # Using default workspace root (current directory's parent or similar)
        # api_key is no longer needed for the Intelligence Core (it uses local indexing)
        self.brain = CloudLittleJBrain()

        _logger.info(
            "Enhanced AI Logic initialized with learning capabilities, Google Tasks, and System Brain")

    def _load_api_key(self) -> Optional[str]:
        """Load Google API Key for Brain Learning"""
        key_path = os.path.join(os.getcwd(), 'config', 'gemini_api_key.txt')
        if os.path.exists(key_path):
            try:
                with open(key_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception:
                pass
        return None

    def process_query(
        self,
        user_query: str,
        user_id: str,
        domain: str,
        user_intent: str,
        tags: Optional[List[str]] = None,
        model_used: str = "local_ollama"
    ) -> Dict[str, Any]:
        """
        Process a user query with learning integration

        Args:
            user_query: The user's question/request
            user_id: User identifier
            domain: Domain (finance, property, volunteer, pos)
            user_intent: Detected user intent
            tags: Additional tags
            model_used: Which model processed this

        Returns:
            Dict with response and metadata
        """
        start_time = datetime.now()

        try:
            # Step 1: Retrieve relevant knowledge
            relevant_knowledge = self.knowledge_base.search_knowledge(
                query=user_query,
                category=domain,
                limit=5
            )

            # Step 2: Generate response (this would use actual LLM in real implementation)
            response = self._generate_response(
                user_query,
                domain,
                relevant_knowledge
            )

            response_time_ms = (
                datetime.now() - start_time).total_seconds() * 1000

            # Step 3: Record experience
            experience_id = self.experience_recorder.record_experience(
                interaction_type="user_interaction",
                context={
                    "user_id": user_id,
                    "domain": domain,
                    "query": user_query,
                    "intent": user_intent,
                    "tags": tags or [],
                    "knowledge_items_used": len(relevant_knowledge)
                },
                ai_response={
                    "content": response["content"],
                    "confidence": response.get("confidence", 0.5),
                    "model_used": model_used,
                    "reasoning": response.get("reasoning", ""),
                    "response_time_ms": response_time_ms,
                    "tokens_used": response.get("tokens_used", 0)
                }
            )

            return {
                "success": True,
                "experience_id": experience_id,
                "response": response["content"],
                "confidence": response.get("confidence", 0.5),
                "reasoning": response.get("reasoning", ""),
                "relevant_knowledge": [
                    {
                        "id": k.get("id"),
                        "title": k.get("title"),
                        "content": k.get("content")[:200] + "..."  # Summary
                    }
                    for k in relevant_knowledge
                ],
                "metadata": {
                    "response_time_ms": response_time_ms,
                    "knowledge_items_used": len(relevant_knowledge),
                    "model": model_used
                }
            }

        except Exception as e:
            _logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def record_user_feedback(
        self,
        experience_id: str,
        satisfaction: int,
        comments: str = "",
        effectiveness: float = 0.5,
        action_taken: bool = False,
        result_description: str = ""
    ) -> Dict[str, Any]:
        """Record user feedback on a response"""
        try:
            feedback_id = self.feedback_collector.record_feedback(
                experience_id=experience_id,
                satisfaction=satisfaction,
                comments=comments,
                effectiveness=effectiveness,
                action_taken=action_taken,
                result_description=result_description
            )

            _logger.info(f"User feedback recorded: {feedback_id}")
            return {
                "success": True,
                "feedback_id": feedback_id
            }

        except Exception as e:
            _logger.error(f"Error recording feedback: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def run_learning_cycle(self) -> Dict[str, Any]:
        """Execute a learning cycle to extract insights and update knowledge"""
        try:
            # 1. Run Standard Learning Engine
            learning_result = self.learning_engine.run_learning_cycle()
            
            # 2. Run System Brain Learning (Logic Indexing & Audit)
            if self.brain:
                _logger.info("Running System Brain Logic Scan...")
                self.brain.scan_tools()
                index_data = self.brain.generate_index()
                self.brain.update_audit_log()
                
                # Ingest System Logic into Knowledge Base
                if index_data:
                    self._ingest_system_knowledge(index_data)

            _logger.info(
                f"Learning cycle completed: {learning_result.get('cycle_id')}")
            return learning_result

        except Exception as e:
            _logger.error(f"Error during learning cycle: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _ingest_system_knowledge(self, index_data: Dict[str, Any]):
        """Ingest system logic index into knowledge base"""
        try:
            # Summary of tools
            tools_count = index_data.get('tool_count', 0)
            timestamp = index_data.get('generated_at')
            
            content = f"System Logic Snapshot at {timestamp}. Total Tools: {tools_count}.\n"
            content += "Tools Distribution:\n"
            for cat, tools in index_data.get('logic_map', {}).items():
                content += f"- {cat}: {len(tools)} tools\n"
            
            # Add to knowledge base (System Category)
            # This allows Sister to 'know' the system state
            # In a real implementation, we would check for duplicates or update existing entry
            pass 
        except Exception as e:
             _logger.warning(f"Failed to ingest system knowledge: {e}")

    def generate_growth_report(self) -> Dict[str, Any]:
        """Generate a comprehensive growth and evaluation report"""
        try:
            # Collect data
            experiences = self.experience_recorder.get_experiences(days=7)
            feedback_stats = self.feedback_collector.get_feedback_stats(days=7)
            knowledge_stats = self.knowledge_base.get_knowledge_stats()

            # Load previous metrics if available
            previous_metrics = self._load_previous_metrics()

            # Generate dashboard
            dashboard = self.dashboard.generate_dashboard(
                experiences=experiences,
                feedback_stats=feedback_stats,
                knowledge_stats=knowledge_stats,
                previous_metrics=previous_metrics
            )

            # Save dashboard
            dashboard_id = self.dashboard.save_dashboard(dashboard)

            _logger.info(f"Growth report generated: {dashboard_id}")
            return dashboard

        except Exception as e:
            _logger.error(f"Error generating growth report: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            stats = self.knowledge_base.get_knowledge_stats()
            return {
                "success": True,
                "stats": stats
            }
        except Exception as e:
            _logger.error(f"Error getting knowledge stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def add_knowledge(
        self,
        category: str,
        title: str,
        content: str,
        confidence_score: float = 0.8,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Manually add knowledge to the base"""
        try:
            knowledge_id = self.knowledge_base.add_knowledge(
                category=category,
                title=title,
                content=content,
                confidence_score=confidence_score,
                tags=tags
            )

            _logger.info(f"Knowledge added: {knowledge_id}")
            return {
                "success": True,
                "knowledge_id": knowledge_id
            }

        except Exception as e:
            _logger.error(f"Error adding knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search the knowledge base"""
        try:
            results = self.knowledge_base.search_knowledge(
                query=query,
                category=category,
                limit=limit
            )

            return {
                "success": True,
                "results": results
            }

        except Exception as e:
            _logger.error(f"Error searching knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def _generate_response(
        query: str,
        domain: str,
        relevant_knowledge: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate response using relevant knowledge
        In production, this would call the actual LLM
        """
        # For demonstration, create a structured response
        knowledge_context = "\n".join([
            f"- {k.get('title')}: {k.get('content')[:100]}..."
            for k in relevant_knowledge
        ])

        response_content = f"基於社區知識庫的回應：\n\n{knowledge_context}"

        return {
            "content": response_content,
            # Increases with knowledge
            "confidence": 0.75 + (len(relevant_knowledge) * 0.05),
            "reasoning": f"基於 {len(relevant_knowledge)} 個相關知識項目生成回應"
        }

    @staticmethod
    def _load_previous_metrics() -> Optional[Dict[str, float]]:
        """Load previous evaluation metrics for comparison"""
        # This would load from the most recent evaluation
        # For now, return None
        return None


# Integration helper functions
def enhance_ai_logic_with_learning(base_path: str = "./memory_store") -> EnhancedAILogic:
    """Create and return enhanced AI logic with learning"""
    return EnhancedAILogic(base_path)


def example_usage():
    """Example of how to use the enhanced AI logic"""

    # Initialize enhanced AI
    ai = enhance_ai_logic_with_learning()

    # Process a user query
    result = ai.process_query(
        user_query="我想了解社區財務預算的最佳實踐",
        user_id="user_123",
        domain="finance",
        user_intent="learn_best_practices",
        tags=["budgeting", "finance", "community"],
        model_used="local_ollama"
    )

    if result["success"]:
        experience_id = result["experience_id"]
        print(f"Query processed: {experience_id}")
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']:.1%}")

        # After some time, user provides feedback
        feedback_result = ai.record_user_feedback(
            experience_id=experience_id,
            satisfaction=5,
            comments="非常有幫助！",
            effectiveness=0.95,
            action_taken=True,
            result_description="用戶按照建議實施了新的預算政策"
        )

        if feedback_result["success"]:
            print(f"Feedback recorded: {feedback_result['feedback_id']}")

    # Run learning cycle
    learning_result = ai.run_learning_cycle()
    print(f"Learning cycle: {learning_result.get('status')}")
    print(
        f"New knowledge items: {learning_result.get('new_knowledge_count', 0)}")

    # Generate growth report
    report = ai.generate_growth_report()
    print(
        f"Overall growth score: {report.get('overall_growth_score', 0):.1f}/10")
    print(f"Challenges: {len(report.get('challenges', []))}")
    print(f"Milestones: {len(report.get('milestones', []))}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run example
    example_usage()
