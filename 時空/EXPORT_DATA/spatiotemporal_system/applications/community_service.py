#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社區服務應用
基於時空系統的社區服務功能
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
import sys
import os

# 添加父目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.spatiotemporal import SpatiotemporalSystem
from core.ai_agent import AIAgent

logger = logging.getLogger(__name__)


class CommunityService:
    """社區服務"""
    
    def __init__(self, spatiotemporal_system: SpatiotemporalSystem, ai_agent: AIAgent):
        """
        初始化社區服務
        
        Args:
            spatiotemporal_system: 時空系統
            ai_agent: AI 小 J
        """
        self.st_system = spatiotemporal_system
        self.ai_j = ai_agent
        self.logger = logging.getLogger(__name__)
    
    def schedule_community_event(
        self,
        title: str,
        event_type: str,
        participants: int,
        duration_hours: float,
        preferred_village: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        排程社區活動
        
        Args:
            title: 活動標題
            event_type: 活動類型
            participants: 參與人數
            duration_hours: 持續時間
            preferred_village: 偏好里別
            description: 描述
        
        Returns:
            排程結果
        """
        # 使用 AI 小 J 建議最佳時間和空間
        suggestions = self.ai_j.suggest_optimal_time_and_space(
            event_type=event_type,
            participants=participants,
            duration_hours=duration_hours,
            preferred_village=preferred_village
        )
        
        if not suggestions["suggestions"]:
            return {
                "status": "failed",
                "message": "找不到可用的時間和空間"
            }
        
        # 選擇最佳建議
        best_suggestion = suggestions["suggestions"][0]
        
        # 建立事件
        event = self.st_system.create_spatiotemporal_event(
            title=title,
            start_time=datetime.fromisoformat(best_suggestion["start_time"]),
            end_time=datetime.fromisoformat(best_suggestion["end_time"]),
            location=best_suggestion["location"],
            village_id=best_suggestion["village_id"],
            description=description,
            space_type="indoor" if event_type == "meeting" else "outdoor",
            capacity=participants,
            metadata={
                "event_type": event_type,
                "suggested_by": "AI 小 J",
                "suggestion_score": best_suggestion["score"]
            }
        )
        
        return {
            "status": "success",
            "event": event.to_dict(),
            "suggestion_used": best_suggestion,
            "alternative_suggestions": suggestions["suggestions"][1:5]
        }
    
    def get_village_activity_schedule(
        self,
        village_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        取得里別活動日程
        
        Args:
            village_id: 里別 ID
            days: 天數
        
        Returns:
            日程表
        """
        schedules = []
        current_date = datetime.now().date()
        
        for i in range(days):
            date = current_date + timedelta(days=i)
            schedule = self.st_system.get_village_schedule(
                village_id,
                datetime.combine(date, datetime.min.time())
            )
            schedules.append(schedule)
        
        return {
            "village_id": village_id,
            "village_name": self.ai_j._get_village_name(village_id),
            "period": {
                "start": current_date.isoformat(),
                "end": (current_date + timedelta(days=days-1)).isoformat()
            },
            "schedules": schedules,
            "total_events": sum(s["total_events"] for s in schedules)
        }
    
    def analyze_community_health(
        self,
        village_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析社區健康度
        
        Args:
            village_id: 可選的里別 ID
        
        Returns:
            健康度分析
        """
        # 分析活動模式
        patterns = self.ai_j.analyze_community_activity_patterns(
            village_id=village_id,
            days=30
        )
        
        # 計算健康度指標
        total_events = patterns["patterns"]["total_events"]
        village_distribution = patterns["patterns"]["village_distribution"]
        
        # 健康度評分（0-100）
        activity_score = min(100, (total_events / 20) * 100)  # 假設 20 個事件為滿分
        distribution_score = 100 if len(village_distribution) >= 3 else (len(village_distribution) / 3) * 100
        
        health_score = (activity_score * 0.7 + distribution_score * 0.3)
        
        # 建議
        recommendations = []
        if health_score < 50:
            recommendations.append("建議增加社區活動頻率")
        if len(village_distribution) < 3:
            recommendations.append("建議平衡各里別的活動分布")
        
        return {
            "health_score": round(health_score, 1),
            "activity_score": round(activity_score, 1),
            "distribution_score": round(distribution_score, 1),
            "patterns": patterns,
            "recommendations": recommendations,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def get_upcoming_events_summary(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        取得即將到來的活動摘要
        
        Args:
            days: 未來天數
        
        Returns:
            活動摘要
        """
        end_date = datetime.now() + timedelta(days=days)
        events = self.st_system.get_events_by_time_range(
            datetime.now(),
            end_date
        )
        
        # 按里別分組
        by_village = {}
        for event in events:
            village_id = event.village_id or "unknown"
            if village_id not in by_village:
                by_village[village_id] = []
            by_village[village_id].append(event.to_dict())
        
        return {
            "period": {
                "start": datetime.now().isoformat(),
                "end": end_date.isoformat()
            },
            "total_events": len(events),
            "events_by_village": {
                self.ai_j._get_village_name(k): v
                for k, v in by_village.items()
            },
            "upcoming_today": [
                e.to_dict() for e in events
                if e.start_time and e.start_time.date() == datetime.now().date()
            ]
        }


# 範例使用
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 初始化
    st_system = SpatiotemporalSystem()
    ai_j = AIAgent(st_system)
    service = CommunityService(st_system, ai_j)
    
    # 排程活動
    result = service.schedule_community_event(
        title="社區理監事會",
        event_type="meeting",
        participants=15,
        duration_hours=2,
        preferred_village="wuchang_li"
    )
    
    print(f"排程結果: {result['status']}")
    if result["status"] == "success":
        print(f"活動: {result['event']['title']}")
        print(f"地點: {result['event']['location']}")
        print(f"時間: {result['event']['start_time']}")
    
    # 取得日程
    schedule = service.get_village_activity_schedule("wuchang_li", days=7)
    print(f"\n五常里未來 7 天活動數: {schedule['total_events']}")
    
    # 健康度分析
    health = service.analyze_community_health()
    print(f"\n社區健康度: {health['health_score']}/100")
    
    print("\n社區服務系統已載入")


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:33:44
---
