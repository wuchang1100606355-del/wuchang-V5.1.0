#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 小 J 代理
本地 AI 功能的智能運用
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import logging
from .spatiotemporal import SpatiotemporalSystem, SpatiotemporalEvent

logger = logging.getLogger(__name__)


class AIAgent:
    """AI 小 J 代理"""
    
    def __init__(self, spatiotemporal_system: SpatiotemporalSystem):
        """
        初始化 AI 小 J
        
        Args:
            spatiotemporal_system: 時空系統
        """
        self.st_system = spatiotemporal_system
        self.name = "AI 小 J"
        self.version = "1.0.0"
        self.logger = logging.getLogger(__name__)
    
    def suggest_optimal_time_and_space(
        self,
        event_type: str,
        participants: int,
        duration_hours: float,
        preferred_village: Optional[str] = None,
        preferred_time: Optional[datetime] = None,
        constraints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        建議最佳時間和空間
        
        Args:
            event_type: 事件類型（'meeting', 'activity', 'service'）
            participants: 參與人數
            duration_hours: 持續時間（小時）
            preferred_village: 偏好里別
            preferred_time: 偏好時間
            constraints: 其他約束條件
        
        Returns:
            建議方案
        """
        suggestions = []
        
        # 根據事件類型選擇合適的空間
        space_requirements = self._get_space_requirements(event_type, participants)
        
        # 可用的里別
        available_villages = ["wuchang_li", "wushun_li", "renzhong_li"]
        if preferred_village:
            available_villages = [preferred_village] if preferred_village in available_villages else available_villages
        
        # 時間範圍（未來 30 天）
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        # 為每個里別生成建議
        for village_id in available_villages:
            # 查找可用時間段
            available_slots = self._find_available_time_slots(
                village_id=village_id,
                duration_hours=duration_hours,
                start_date=start_date,
                end_date=end_date,
                preferred_time=preferred_time
            )
            
            for slot in available_slots[:5]:  # 每個里別最多 5 個建議
                suggestion = {
                    "village_id": village_id,
                    "village_name": self._get_village_name(village_id),
                    "start_time": slot["start_time"].isoformat(),
                    "end_time": slot["end_time"].isoformat(),
                    "location": slot.get("location", f"{self._get_village_name(village_id)}活動中心"),
                    "score": slot.get("score", 0),
                    "reason": slot.get("reason", "")
                }
                suggestions.append(suggestion)
        
        # 按分數排序
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "event_type": event_type,
            "participants": participants,
            "duration_hours": duration_hours,
            "suggestions": suggestions[:10],  # 返回前 10 個建議
            "generated_at": datetime.now().isoformat()
        }
    
    def optimize_schedule(
        self,
        events: List[Dict],
        constraints: Optional[Dict] = None
    ) -> List[Dict]:
        """
        優化排程
        
        Args:
            events: 事件列表
            constraints: 約束條件
        
        Returns:
            優化後的排程
        """
        optimized = []
        
        # 按時間排序
        sorted_events = sorted(events, key=lambda e: e.get("start_time", ""))
        
        for i, event in enumerate(sorted_events):
            # 檢查與前一個事件的衝突
            if i > 0:
                prev_event = sorted_events[i - 1]
                # 如果時間或空間衝突，調整時間
                if self._has_conflict(prev_event, event):
                    # 建議調整
                    suggested_time = self._suggest_adjusted_time(prev_event, event)
                    event["suggested_start_time"] = suggested_time
                    event["optimization_note"] = "時間已調整以避免衝突"
            
            optimized.append(event)
        
        return optimized
    
    def analyze_community_activity_patterns(
        self,
        village_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        分析社區活動模式
        
        Args:
            village_id: 可選的里別 ID
            days: 分析天數
        
        Returns:
            分析結果
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        patterns = self.st_system.analyze_spatiotemporal_patterns(
            village_id=village_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # AI 分析洞察
        insights = []
        
        if patterns["village_distribution"]:
            most_active = patterns["most_active_village"]
            insights.append(f"最活躍的里別是 {self._get_village_name(most_active)}")
        
        if patterns["time_distribution"]:
            most_active_time = patterns["most_active_time"]
            time_names = {
                "morning": "上午",
                "afternoon": "下午",
                "evening": "晚上",
                "night": "夜間"
            }
            insights.append(f"最活躍的時段是 {time_names.get(most_active_time, most_active_time)}")
        
        # 建議
        recommendations = []
        if patterns["total_events"] < 10:
            recommendations.append("建議增加社區活動以提升社區凝聚力")
        
        return {
            "patterns": patterns,
            "insights": insights,
            "recommendations": recommendations,
            "analyzed_by": self.name
        }
    
    def predict_space_utilization(
        self,
        village_id: str,
        date: datetime
    ) -> Dict[str, Any]:
        """
        預測空間使用率
        
        Args:
            village_id: 里別 ID
            date: 日期
        
        Returns:
            預測結果
        """
        # 取得歷史數據
        historical_events = self.st_system.get_events_by_village(
            village_id,
            time_range=(
                date - timedelta(days=30),
                date - timedelta(days=1)
            )
        )
        
        # 取得當天事件
        day_events = self.st_system.get_village_schedule(village_id, date)
        
        # 簡單預測（基於歷史平均）
        avg_events_per_day = len(historical_events) / 30 if historical_events else 0
        predicted_events = max(avg_events_per_day, len(day_events["events"]))
        
        utilization_rate = min(100, (predicted_events / 10) * 100)  # 假設最大 10 個事件為 100%
        
        return {
            "village_id": village_id,
            "village_name": self._get_village_name(village_id),
            "date": date.date().isoformat(),
            "predicted_events": round(predicted_events, 1),
            "utilization_rate": round(utilization_rate, 1),
            "current_events": len(day_events["events"]),
            "confidence": "medium"  # 可根據歷史數據質量調整
        }
    
    def _get_space_requirements(self, event_type: str, participants: int) -> Dict:
        """取得空間需求"""
        requirements = {
            "meeting": {
                "min_area": participants * 2,  # 每人 2 平方米
                "indoor": True,
                "equipment": ["桌椅", "投影設備"]
            },
            "activity": {
                "min_area": participants * 3,
                "indoor": False,
                "equipment": ["音響", "活動道具"]
            },
            "service": {
                "min_area": participants * 1.5,
                "indoor": True,
                "equipment": ["服務台", "資料"]
            }
        }
        return requirements.get(event_type, requirements["meeting"])
    
    def _find_available_time_slots(
        self,
        village_id: str,
        duration_hours: float,
        start_date: datetime,
        end_date: datetime,
        preferred_time: Optional[datetime] = None
    ) -> List[Dict]:
        """查找可用時間段"""
        slots = []
        
        # 取得該里別的所有事件
        existing_events = self.st_system.get_events_by_village(
            village_id,
            time_range=(start_date, end_date)
        )
        
        # 生成候選時間段
        current = start_date
        duration = timedelta(hours=duration_hours)
        
        preferred_hours = [9, 14, 19]  # 偏好時間：上午 9 點、下午 2 點、晚上 7 點
        
        while current < end_date:
            # 嘗試每個偏好時間
            for hour in preferred_hours:
                slot_start = current.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + duration
                
                if slot_end > end_date:
                    break
                
                # 檢查是否與現有事件衝突
                conflicts = self.st_system.check_time_space_conflict(
                    slot_start, slot_end, village_id
                )
                
                if not conflicts:
                    # 計算分數
                    score = self._calculate_slot_score(slot_start, preferred_time, hour)
                    
                    slots.append({
                        "start_time": slot_start,
                        "end_time": slot_end,
                        "score": score,
                        "reason": f"無衝突，{hour}點時段"
                    })
            
            current += timedelta(days=1)
        
        return slots
    
    def _calculate_slot_score(
        self,
        slot_time: datetime,
        preferred_time: Optional[datetime],
        hour: int
    ) -> float:
        """計算時間段分數"""
        score = 50.0  # 基礎分數
        
        # 偏好時間加分
        if preferred_time:
            time_diff = abs((slot_time - preferred_time).total_seconds() / 3600)
            score += max(0, 30 - time_diff * 2)
        
        # 時段偏好加分
        if hour in [9, 14, 19]:
            score += 20
        
        return score
    
    def _has_conflict(self, event1: Dict, event2: Dict) -> bool:
        """檢查兩個事件是否衝突"""
        # 簡化實現
        return False
    
    def _suggest_adjusted_time(self, prev_event: Dict, current_event: Dict) -> str:
        """建議調整後的時間"""
        # 簡化實現
        return current_event.get("start_time", "")
    
    def _get_village_name(self, village_id: str) -> str:
        """取得里別名稱"""
        names = {
            "wuchang_li": "五常里",
            "wushun_li": "五順里",
            "renzhong_li": "仁忠里"
        }
        return names.get(village_id, village_id)


# 範例使用
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    from .spatiotemporal import SpatiotemporalSystem
    
    # 初始化
    st_system = SpatiotemporalSystem()
    ai_j = AIAgent(st_system)
    
    # AI 建議
    suggestions = ai_j.suggest_optimal_time_and_space(
        event_type="meeting",
        participants=10,
        duration_hours=2
    )
    
    print(f"AI 小 J 建議: {len(suggestions['suggestions'])} 個方案")
    for i, suggestion in enumerate(suggestions["suggestions"][:3], 1):
        print(f"{i}. {suggestion['village_name']} @ {suggestion['start_time']} (分數: {suggestion['score']})")
    
    print(f"\n{ai_j.name} 已載入")
