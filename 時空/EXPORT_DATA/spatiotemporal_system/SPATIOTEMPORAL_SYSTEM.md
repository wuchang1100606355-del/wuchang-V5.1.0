# 時空整合系統 - AI 小 J 本地功能運用

**系統版本**: 1.0.0  
**建立時間**: 2026-01-18  
**開發者**: AI 小 J (Little J)

---

## 🎯 系統目標

整合時間邏輯（Google Calendar + 系統時間）與空間邏輯（3D 空間模型），建立完整的時空系統，提供 AI 小 J 的智能本地功能運用。

---

## 🏗️ 系統架構

### 核心模組

1. **時空整合核心** (`spatiotemporal.py`)
   - 時空事件管理
   - 時空查詢
   - 時空分析

2. **AI 小 J 代理** (`ai_agent.py`)
   - 智能時間空間建議
   - 排程優化
   - 活動模式分析
   - 空間使用率預測

3. **社區服務** (`community_service.py`)
   - 活動排程
   - 日程管理
   - 社區健康度分析

---

## 📊 核心功能

### 1. 時空事件管理

- **建立時空事件**: 結合時間和空間的事件
- **時空查詢**: 查詢特定時間和空間範圍的事件
- **衝突檢測**: 檢測時間和空間衝突

### 2. AI 小 J 智能功能

#### 時間空間建議

```python
suggestions = ai_j.suggest_optimal_time_and_space(
    event_type="meeting",
    participants=10,
    duration_hours=2,
    preferred_village="wuchang_li"
)
```

#### 排程優化

```python
optimized = ai_j.optimize_schedule(events)
```

#### 活動模式分析

```python
patterns = ai_j.analyze_community_activity_patterns(
    village_id="wuchang_li",
    days=30
)
```

#### 空間使用率預測

```python
prediction = ai_j.predict_space_utilization(
    village_id="wuchang_li",
    date=datetime(2026, 1, 20)
)
```

### 3. 社區服務應用

#### 活動排程

```python
result = community_service.schedule_community_event(
    title="理監事會會議",
    event_type="meeting",
    participants=15,
    duration_hours=2,
    preferred_village="wuchang_li"
)
```

#### 日程管理

```python
schedule = community_service.get_village_activity_schedule(
    village_id="wuchang_li",
    days=7
)
```

#### 健康度分析

```python
health = community_service.analyze_community_health(
    village_id="wuchang_li"
)
```

---

## 🚀 使用範例

### 基本使用

```python
from spatiotemporal_system.core.spatiotemporal import SpatiotemporalSystem
from spatiotemporal_system.core.ai_agent import AIAgent
from spatiotemporal_system.applications.community_service import CommunityService

# 初始化
st_system = SpatiotemporalSystem()
ai_j = AIAgent(st_system)
service = CommunityService(st_system, ai_j)

# 建立時空事件
event = st_system.create_spatiotemporal_event(
    title="理監事會會議",
    start_time=datetime(2026, 1, 20, 14, 0),
    end_time=datetime(2026, 1, 20, 16, 0),
    location="五常里活動中心",
    village_id="wuchang_li",
    coordinates=[121.4898, 25.0818, 10]
)

# AI 建議
suggestions = ai_j.suggest_optimal_time_and_space(
    event_type="meeting",
    participants=10,
    duration_hours=2
)

# 社區服務
result = service.schedule_community_event(
    title="社區活動",
    event_type="activity",
    participants=20,
    duration_hours=3
)
```

### API 使用

```bash
# 建立事件
curl -X POST http://localhost:8080/api/spatiotemporal/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "理監事會會議",
    "start_time": "2026-01-20T14:00:00",
    "end_time": "2026-01-20T16:00:00",
    "location": "五常里活動中心",
    "village_id": "wuchang_li"
  }'

# AI 建議
curl -X POST http://localhost:8080/api/ai/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "meeting",
    "participants": 10,
    "duration_hours": 2,
    "preferred_village": "wuchang_li"
  }'

# 查詢日程
curl http://localhost:8080/api/spatiotemporal/villages/wuchang_li/schedule?date=2026-01-20

# 社區健康度
curl http://localhost:8080/api/community/health?village_id=wuchang_li
```

---

## 📚 功能清單

### 時空整合

- ✅ 時空事件建立
- ✅ 時空查詢
- ✅ 衝突檢測
- ✅ 時空分析

### AI 小 J 功能

- ✅ 時間空間建議
- ✅ 排程優化
- ✅ 活動模式分析
- ✅ 空間使用率預測

### 社區服務

- ✅ 活動排程
- ✅ 日程管理
- ✅ 健康度分析
- ✅ 活動摘要

---

## 🔧 配置

### 系統配置

```python
# config/system_config.py
SYSTEM_CONFIG = {
    "timezone": "Asia/Taipei",
    "default_villages": ["wuchang_li", "wushun_li", "renzhong_li"],
    "ai_agent": {
        "name": "AI 小 J",
        "version": "1.0.0"
    }
}
```

---

## 🔗 相關系統

- **時間邏輯系統**: Google Calendar 整合、系統時間同步
- **空間邏輯系統**: 五常里、五順里、仁忠里 3D 空間模型

---

**系統狀態**: ✅ 完成  
**維護者**: AI 小 J (Little J)


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:33:43
---
