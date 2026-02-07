#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時空系統 API
提供時空系統的 RESTful API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import sys
import os

# 添加父目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.spatiotemporal import SpatiotemporalSystem
from core.ai_agent import AIAgent
from applications.community_service import CommunityService

app = Flask(__name__)
CORS(app)

# 初始化系統
st_system = SpatiotemporalSystem()
ai_j = AIAgent(st_system)
community_service = CommunityService(st_system, ai_j)


@app.route('/api/spatiotemporal/events', methods=['POST'])
def create_event():
    """建立時空事件"""
    data = request.json
    
    try:
        event = st_system.create_spatiotemporal_event(
            title=data.get('title'),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            location=data.get('location'),
            village_id=data.get('village_id'),
            coordinates=data.get('coordinates'),
            description=data.get('description')
        )
        
        return jsonify({
            "status": "success",
            "event": event.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/spatiotemporal/events', methods=['GET'])
def get_events():
    """查詢事件"""
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    village_id = request.args.get('village_id')
    
    if start_time and end_time:
        events = st_system.get_events_by_time_range(
            datetime.fromisoformat(start_time),
            datetime.fromisoformat(end_time),
            village_id
        )
    elif village_id:
        events = st_system.get_events_by_village(village_id)
    else:
        events = list(st_system.events.values())
    
    return jsonify({
        "status": "success",
        "events": [e.to_dict() for e in events],
        "count": len(events)
    })


@app.route('/api/spatiotemporal/villages/<village_id>/schedule', methods=['GET'])
def get_village_schedule(village_id: str):
    """取得里別日程"""
    date_str = request.args.get('date')
    date = datetime.fromisoformat(date_str) if date_str else datetime.now()
    
    schedule = st_system.get_village_schedule(village_id, date)
    return jsonify(schedule)


@app.route('/api/ai/suggest', methods=['POST'])
def ai_suggest():
    """AI 小 J 建議"""
    data = request.json
    
    suggestions = ai_j.suggest_optimal_time_and_space(
        event_type=data.get('event_type', 'meeting'),
        participants=data.get('participants', 10),
        duration_hours=data.get('duration_hours', 2),
        preferred_village=data.get('preferred_village'),
        preferred_time=datetime.fromisoformat(data['preferred_time']) if data.get('preferred_time') else None
    )
    
    return jsonify(suggestions)


@app.route('/api/community/schedule-event', methods=['POST'])
def schedule_community_event():
    """排程社區活動"""
    data = request.json
    
    result = community_service.schedule_community_event(
        title=data.get('title'),
        event_type=data.get('event_type', 'meeting'),
        participants=data.get('participants', 10),
        duration_hours=data.get('duration_hours', 2),
        preferred_village=data.get('preferred_village'),
        description=data.get('description')
    )
    
    return jsonify(result)


@app.route('/api/community/health', methods=['GET'])
def analyze_community_health():
    """分析社區健康度"""
    village_id = request.args.get('village_id')
    
    health = community_service.analyze_community_health(village_id)
    return jsonify(health)


@app.route('/api/spatiotemporal/analyze', methods=['GET'])
def analyze_patterns():
    """分析時空模式"""
    village_id = request.args.get('village_id')
    days = int(request.args.get('days', 30))
    
    patterns = st_system.analyze_spatiotemporal_patterns(
        village_id=village_id,
        start_date=datetime.now() - timedelta(days=days),
        end_date=datetime.now()
    )
    
    return jsonify(patterns)


@app.route('/api/ai/agent/info', methods=['GET'])
def ai_agent_info():
    """取得 AI 小 J 資訊"""
    return jsonify({
        "name": ai_j.name,
        "version": ai_j.version,
        "capabilities": [
            "時間空間建議",
            "排程優化",
            "活動模式分析",
            "空間使用率預測"
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5500))
    print("時空系統 API 啟動中...")
    print(f"API 文檔: http://localhost:{port}/api/spatiotemporal/events")
    print(f"AI 小 J 資訊: http://localhost:{port}/api/ai/agent/info")
    app.run(host='0.0.0.0', port=port, debug=True)


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:33:44
---
