
import sys
import os
import json
import datetime
import random
from dataclasses import asdict

# Ensure we can import the core module
sys.path.append(os.path.join(os.getcwd(), 'spatiotemporal_system'))
from core.spatiotemporal import SpatiotemporalSystem, SpatiotemporalEvent

# Initialize System
st_system = SpatiotemporalSystem()

# Research Topics (10 Topics)
research_topics = [
    {
        "id": "RES-001",
        "name": "人口結構與長者需求分析",
        "category": "Demographics",
        "description": "深度分析五常社區19.3%老年人口的生活需求與行動模式",
        "target_data": ["老年人口分佈", "活動中心利用率", "無障礙設施覆蓋率"]
    },
    {
        "id": "RES-002",
        "name": "商業生態與零售熱點映射",
        "category": "Business",
        "description": "針對五華街與龍江路之零售與B2B隱性商業網絡進行普查",
        "target_data": ["店面空置率", "人流熱點", "消費時段分佈"]
    },
    {
        "id": "RES-003",
        "name": "交通流量與物流動線優化",
        "category": "Traffic",
        "description": "監測4200-5800輛機車之流動規律與停車痛點",
        "target_data": ["違停熱點", "尖峰車流", "物流卸貨區需求"]
    },
    {
        "id": "RES-004",
        "name": "公共空間與綠地效益評估",
        "category": "UrbanPlanning",
        "description": "評估五常公園與周邊綠地之生態效益與居民使用滿意度",
        "target_data": ["綠地覆蓋率", "設施維護狀況", "居民社交互動"]
    },
    {
        "id": "RES-005",
        "name": "環境噪音與生活品質監測",
        "category": "Environment",
        "description": "分析主要幹道與巷弄之噪音分貝分佈與時段變化",
        "target_data": ["分貝熱區", "夜間干擾指數", "隔音改善需求"]
    },
    {
        "id": "RES-006",
        "name": "能源消耗與電網負載分析",
        "category": "Energy",
        "description": "推估社區夏季用電尖峰與變電箱負載熱點",
        "target_data": ["用電密度", "變電箱溫度", "節能潛力區"]
    },
    {
        "id": "RES-007",
        "name": "社區安全與治安死角掃描",
        "category": "Security",
        "description": "識別夜間照明不足區域與監視器覆蓋盲點",
        "target_data": ["照明照度", "監視死角", "夜歸安全路徑"]
    },
    {
        "id": "RES-008",
        "name": "教育資源與學童通學路徑",
        "category": "Education",
        "description": "分析學區內補習班分佈與學童上下學安全路徑",
        "target_data": ["補教熱點", "通學車流", "導護需求點"]
    },
    {
        "id": "RES-009",
        "name": "文化資產與歷史記憶保存",
        "category": "Culture",
        "description": "盤點社區內老樹、老屋與地方耆老口述歷史",
        "target_data": ["老樹位置", "歷史建物", "文化導覽點"]
    },
    {
        "id": "RES-010",
        "name": "防災韌性與疏散動線模擬",
        "category": "Resilience",
        "description": "模擬地震與水災發生時的居民疏散效率與避難點容量",
        "target_data": ["疏散路徑", "避難收容能", "窄巷阻礙點"]
    }
]

# Available Villages (Nodes) - Using all 3 for maximum redundancy
villages = [
    {"id": "五常里", "coords": [121.540, 25.065]}, 
    {"id": "五順里", "coords": [121.545, 25.068]},
    {"id": "仁忠里", "coords": [121.538, 25.062]}
]

# 20 Distinct AI Models for "Distributed Computing"
ai_models = [
    "Gemini-Pro-Vision-Node-Alpha",
    "Gemini-Pro-Reasoning-Node-Beta",
    "Gemini-Ultra-Core-Gamma",
    "Gemini-1.5-Flash-Edge",
    "Llama-3-70B-Analysis-Unit",
    "Llama-3-400B-Deep-Thinker",
    "Claude-3-Opus-Insight-Core",
    "Claude-3-Sonnet-Speed-Demon",
    "Claude-3-Haiku-Data-Stream",
    "GPT-4o-Global-Observer",
    "GPT-4-Turbo-Legacy-Archive",
    "Mistral-Large-Local-Solver",
    "Mistral-Medium-Code-Expert",
    "Falcon-180B-Open-Source-Giant",
    "Grok-1-Realtime-Monitor",
    "Databricks-DBRX-Data-Miner",
    "Command-R-Plus-Tool-User",
    "Yi-34B-Asian-Context-Specialist",
    "Qwen-72B-Multilingual-Node",
    "DeepSeek-Coder-V2-System-Architect"
]

def generate_distributed_research():
    print(f"🚀 Starting Massive Distributed Research Simulation (High Redundancy)...")
    print("🔗 Connecting to Global AI Grid...")
    
    events_export = []
    
    # We will reuse the model pool, cycling through it
    model_pool = ai_models.copy()
    random.shuffle(model_pool)
    model_idx = 0
    
    for topic in research_topics:
        # Use ALL 3 villages for Triple Verification
        selected_villages = villages 
        
        print(f"\n📋 Initiating Triple-Redundancy Research: {topic['name']}")
        
        # Enforce "Same Time, Same View" for all agents working on this topic
        # This eliminates temporal discrepancies (e.g., one agent seeing construction, another seeing finished state)
        unified_start_offset = random.randint(0, 24)
        unified_duration = random.randint(48, 168) # 2-7 days
        unified_start_time = datetime.datetime.now() + datetime.timedelta(hours=unified_start_offset)
        unified_end_time = unified_start_time + datetime.timedelta(hours=unified_duration)
        snapshot_id = f"SNAP-{unified_start_time.strftime('%Y%m%d%H')}-{topic['id']}"
        
        for i, village in enumerate(selected_villages):
            # Assign a unique AI Model from the pool
            assigned_model = model_pool[model_idx % len(model_pool)]
            model_idx += 1
            
            # Create Event using Spacetime Rules
            event_title = f"🔍 [研究執行] {topic['name']} - {village['id']}"
            
            # Jitter coordinates slightly for visualization separation ONLY
            # But logically they are observing the exact same "Place"
            base_coords = village['coords']
            jitter_lat = (random.random() - 0.5) * 0.003
            jitter_lng = (random.random() - 0.5) * 0.003
            final_coords = [base_coords[0] + jitter_lng, base_coords[1] + jitter_lat]
            
            event = st_system.create_spatiotemporal_event(
                title=event_title,
                start_time=unified_start_time,  # UNIFIED TIME
                end_time=unified_end_time,      # UNIFIED TIME
                location=f"{village['id']} - 高效能運算單元 {assigned_model}",
                village_id=village['id'],
                coordinates=final_coords,
                description=f"執行模型: {assigned_model}\n任務目標: {topic['description']}\n數據標的: {', '.join(topic['target_data'])}\n時空快照 ID: {snapshot_id}",
                metadata={
                    "type": "distributed_research_task",
                    "research_id": topic['id'],
                    "category": topic['category'],
                    "assigned_model": assigned_model,
                    "computation_status": "processing",
                    "replication_node": i + 1,
                    "snapshot_id": snapshot_id, # Key for ensuring temporal consistency
                    "data_source_view": "construction_phase_aware" # Tagging user's insight
                }
            )
            
            print(f"  ✅ Task Dispatched: {event_title} -> Model: {assigned_model}")
            events_export.append(event.to_dict())

    # Export to JSON for the Frontend (Direct Core Mapping)
    output_path = os.path.join(os.getcwd(), 'spacetime_events.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(events_export, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Spacetime Events exported to: {output_path}")
    print(f"🔥 Total Active AI Agents: {len(events_export)}")
    return events_export

if __name__ == "__main__":
    generate_distributed_research()
