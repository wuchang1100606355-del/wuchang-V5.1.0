# 時空整合系統 - AI 小 J 本地功能運用

**系統版本**: 1.0.0  
**建立時間**: 2026-01-18  
**開發者**: AI 小 J (Little J)  
**整合**: 時間邏輯系統 + 空間邏輯系統

---

## 📋 系統概述

本系統整合時間邏輯（Google Calendar + 系統時間）與空間邏輯（3D 空間模型），建立完整的時空系統，提供：

- ⏰ **時間維度**: Google Calendar 整合、系統時間同步、事件排程
- 🌍 **空間維度**: 五常里、五順里、仁忠里 3D 空間模型
- 🔗 **時空整合**: 時間與空間的關聯分析
- 🤖 **AI 功能**: 本地 AI 小 J 的智能運用
- 📊 **本地運用**: 社區服務、活動管理、空間規劃

---

## 🏗️ 系統架構

```
spatiotemporal_system/
├── core/                    # 核心模組
│   ├── spatiotemporal.py   # 時空整合核心
│   ├── ai_agent.py         # AI 小 J 代理
│   └── local_services.py   # 本地服務
├── time/                    # 時間邏輯
│   ├── calendar_sync.py    # Calendar 同步
│   └── time_logic.py       # 時間邏輯處理
├── space/                   # 空間邏輯
│   ├── village_model.py    # 里別模型
│   └── spatial_query.py    # 空間查詢
├── applications/            # 本地運用
│   ├── event_management.py # 活動管理
│   ├── space_booking.py    # 空間預約
│   ├── community_service.py # 社區服務
│   └── analytics.py         # 時空分析
├── api/                     # API 服務
│   └── spatiotemporal_api.py # 時空 API
└── config/                  # 配置
    └── system_config.py     # 系統配置
```

---

## 🎯 核心功能

### 1. 時空整合

- **時空事件**: 結合時間與空間的事件管理
- **時空查詢**: 查詢特定時間和空間範圍的事件
- **時空分析**: 分析時間與空間的關聯性

### 2. AI 小 J 功能

- **智能排程**: 根據空間可用性和時間衝突智能排程
- **空間建議**: 根據活動類型建議合適的空間
- **時空優化**: 優化活動的時間和空間安排

### 3. 本地運用

- **活動管理**: 社區活動的時間和空間管理
- **空間預約**: 社區空間的預約系統
- **服務規劃**: 社區服務的時間和空間規劃
- **數據分析**: 時空數據的分析和視覺化

---

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 初始化系統

```python
from spatiotemporal_system.core.spatiotemporal import SpatiotemporalSystem
from spatiotemporal_system.core.ai_agent import AIAgent

# 初始化時空系統
st_system = SpatiotemporalSystem()

# 初始化 AI 小 J
ai_j = AIAgent(st_system)
```

### 使用範例

```python
# 建立時空事件
event = st_system.create_spatiotemporal_event(
    title="理監事會會議",
    start_time=datetime(2026, 1, 20, 14, 0),
    end_time=datetime(2026, 1, 20, 16, 0),
    location="五常里",
    village_id="wuchang_li",
    description="每月理監事會會議"
)

# AI 小 J 智能建議
suggestions = ai_j.suggest_optimal_time_and_space(
    event_type="meeting",
    participants=10,
    duration_hours=2
)
```

---

## 📚 詳細文檔

- [時空整合指南](./docs/spatiotemporal_integration.md)
- [AI 小 J 使用手冊](./docs/ai_agent_guide.md)
- [本地運用開發](./docs/local_applications.md)

---

## 🔗 相關資源

- [時間邏輯系統](../time_logic_system/)
- [空間邏輯系統](../spatial_3d_system/)
