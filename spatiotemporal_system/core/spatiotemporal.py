#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時空整合核心系統
整合時間邏輯與空間邏輯
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class SpatiotemporalEvent:
    """時空事件"""
    event_id: str
    title: str
    description: Optional[str] = None
    
    # 時間維度
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: str = "Asia/Taipei"
    recurrence: Optional[Dict] = None
    
    # 空間維度
    location: Optional[str] = None
    village_id: Optional[str] = None  # 五常里、五順里、仁忠里
    coordinates: Optional[List[float]] = None  # [longitude, latitude, altitude]
    space_type: Optional[str] = None  # 'indoor', 'outdoor', 'virtual'
    capacity: Optional[int] = None
    
    # 其他屬性
    organizer: Optional[str] = None
    participants: List[str] = field(default_factory=list)
    status: str = "scheduled"  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "timezone": self.timezone,
            "location": self.location,
            "village_id": self.village_id,
            "coordinates": self.coordinates,
            "space_type": self.space_type,
            "capacity": self.capacity,
            "organizer": self.organizer,
            "participants": self.participants,
            "status": self.status,
            "metadata": self.metadata
        }
    
    def is_active(self, current_time: Optional[datetime] = None) -> bool:
        """檢查事件是否正在進行"""
        if current_time is None:
            current_time = datetime.now()
        
        if not self.start_time or not self.end_time:
            return False
        
        return self.start_time <= current_time <= self.end_time
    
    def is_in_village(self, village_id: str) -> bool:
        """檢查事件是否在指定里別"""
        return self.village_id == village_id


class SpatiotemporalSystem:
    """時空整合系統"""
    
    def __init__(self, time_system=None, space_system=None):
        """
        初始化時空系統
        
        Args:
            time_system: 時間邏輯系統
            space_system: 空間邏輯系統
        """
        self.time_system = time_system
        self.space_system = space_system
        self.events: Dict[str, SpatiotemporalEvent] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_spatiotemporal_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        location: Optional[str] = None,
        village_id: Optional[str] = None,
        coordinates: Optional[List[float]] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> SpatiotemporalEvent:
        """
        建立時空事件
        
        Args:
            title: 事件標題
            start_time: 開始時間
            end_time: 結束時間
            location: 地點
            village_id: 里別 ID
            coordinates: 座標 [lng, lat, alt]
            description: 描述
            **kwargs: 其他參數
        
        Returns:
            時空事件
        """
        event_id = f"st_event_{len(self.events) + 1}"
        
        event = SpatiotemporalEvent(
            event_id=event_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            village_id=village_id,
            coordinates=coordinates,
            **kwargs
        )
        
        self.events[event_id] = event
        
        # 同步到時間系統
        if self.time_system:
            try:
                self.time_system.create_event(
                    title=title,
                    start_time=start_time,
                    end_time=end_time,
                    description=description,
                    location=location
                )
            except Exception as e:
                self.logger.warning(f"同步到時間系統失敗: {e}")
        
        # 同步到空間系統
        if self.space_system and village_id:
            try:
                # 在空間系統中標記事件位置
                pass  # 待實現
            except Exception as e:
                self.logger.warning(f"同步到空間系統失敗: {e}")
        
        self.logger.info(f"時空事件已建立: {title} ({event_id})")
        return event
    
    def get_events_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        village_id: Optional[str] = None
    ) -> List[SpatiotemporalEvent]:
        """
        查詢時間範圍內的事件
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            village_id: 可選的里別 ID
        
        Returns:
            事件列表
        """
        results = []
        
        for event in self.events.values():
            # 檢查時間範圍
            if event.start_time and event.end_time:
                if not (event.end_time < start_time or event.start_time > end_time):
                    # 檢查里別
                    if village_id is None or event.village_id == village_id:
                        results.append(event)
        
        return sorted(results, key=lambda e: e.start_time if e.start_time else datetime.min)
    
    def get_events_by_village(
        self,
        village_id: str,
        time_range: Optional[tuple] = None
    ) -> List[SpatiotemporalEvent]:
        """
        查詢指定里別的事件
        
        Args:
            village_id: 里別 ID
            time_range: 可選的時間範圍 (start_time, end_time)
        
        Returns:
            事件列表
        """
        results = [e for e in self.events.values() if e.village_id == village_id]
        
        if time_range:
            start_time, end_time = time_range
            results = [
                e for e in results
                if e.start_time and e.end_time and
                not (e.end_time < start_time or e.start_time > end_time)
            ]
        
        return sorted(results, key=lambda e: e.start_time if e.start_time else datetime.min)
    
    def get_active_events(self, current_time: Optional[datetime] = None) -> List[SpatiotemporalEvent]:
        """
        取得正在進行的事件
        
        Args:
            current_time: 當前時間（預設為現在）
        
        Returns:
            正在進行的事件列表
        """
        if current_time is None:
            current_time = datetime.now()
        
        return [e for e in self.events.values() if e.is_active(current_time)]
    
    def check_time_space_conflict(
        self,
        start_time: datetime,
        end_time: datetime,
        village_id: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[SpatiotemporalEvent]:
        """
        檢查時間和空間衝突
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            village_id: 里別 ID
            location: 地點
        
        Returns:
            衝突的事件列表
        """
        conflicts = []
        
        for event in self.events.values():
            if event.status == "cancelled":
                continue
            
            # 檢查時間衝突
            time_conflict = False
            if event.start_time and event.end_time:
                time_conflict = not (event.end_time <= start_time or event.start_time >= end_time)
            
            # 檢查空間衝突
            space_conflict = False
            if village_id and event.village_id == village_id:
                if location and event.location == location:
                    space_conflict = True
                elif not location:  # 如果沒有指定具體地點，只要在同一里就認為可能衝突
                    space_conflict = True
            
            if time_conflict and space_conflict:
                conflicts.append(event)
        
        return conflicts
    
    def get_village_schedule(
        self,
        village_id: str,
        date: datetime
    ) -> Dict[str, Any]:
        """
        取得里別的日程表
        
        Args:
            village_id: 里別 ID
            date: 日期
        
        Returns:
            日程表資料
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        events = self.get_events_by_time_range(start_of_day, end_of_day, village_id)
        
        return {
            "village_id": village_id,
            "date": date.date().isoformat(),
            "events": [e.to_dict() for e in events],
            "total_events": len(events),
            "active_events": len([e for e in events if e.is_active()])
        }
    
    def analyze_spatiotemporal_patterns(
        self,
        village_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        分析時空模式
        
        Args:
            village_id: 可選的里別 ID
            start_date: 開始日期
            end_date: 結束日期
        
        Returns:
            分析結果
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        events = self.get_events_by_time_range(start_date, end_date, village_id)
        
        # 統計分析
        village_stats = {}
        time_stats = {
            "morning": 0,  # 6-12
            "afternoon": 0,  # 12-18
            "evening": 0,  # 18-22
            "night": 0  # 22-6
        }
        
        for event in events:
            # 里別統計
            if event.village_id:
                if event.village_id not in village_stats:
                    village_stats[event.village_id] = 0
                village_stats[event.village_id] += 1
            
            # 時段統計
            if event.start_time:
                hour = event.start_time.hour
                if 6 <= hour < 12:
                    time_stats["morning"] += 1
                elif 12 <= hour < 18:
                    time_stats["afternoon"] += 1
                elif 18 <= hour < 22:
                    time_stats["evening"] += 1
                else:
                    time_stats["night"] += 1
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_events": len(events),
            "village_distribution": village_stats,
            "time_distribution": time_stats,
            "most_active_village": max(village_stats.items(), key=lambda x: x[1])[0] if village_stats else None,
            "most_active_time": max(time_stats.items(), key=lambda x: x[1])[0] if time_stats else None
        }


# 範例使用
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 初始化時空系統
    st_system = SpatiotemporalSystem()
    
    # 建立時空事件
    event = st_system.create_spatiotemporal_event(
        title="理監事會會議",
        start_time=datetime(2026, 1, 20, 14, 0),
        end_time=datetime(2026, 1, 20, 16, 0),
        location="五常里活動中心",
        village_id="wuchang_li",
        coordinates=[121.4898, 25.0818, 10],
        description="每月理監事會會議"
    )
    
    print(f"事件已建立: {event.title}")
    print(f"時空資訊: {event.village_id} @ {event.start_time}")
    
    # 查詢事件
    events = st_system.get_events_by_village("wuchang_li")
    print(f"\n五常里事件數: {len(events)}")
    
    # 分析模式
    patterns = st_system.analyze_spatiotemporal_patterns()
    print(f"\n時空模式分析: {patterns}")
    
    print("\n時空整合系統已載入")
