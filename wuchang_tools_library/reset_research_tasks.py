
import json
import random

EVENTS_FILE = '../spacetime_events.json'

# Models pool
models = [
    "Gemini-Pro-Vision-Node-Alpha", 
    "Llama-3-70B-Analysis-Unit", 
    "Claude-3-Opus-Insight-Core",
    "Mistral-Large-Reasoning-Engine",
    "Grok-1-Unfiltered-Perspective"
]

base_tasks = [
    {"rid": "RES-001", "title": "人口結構調查", "topic": "Demographics"},
    {"rid": "RES-002", "title": "商家營收與交通關聯分析", "topic": "Business"},
    {"rid": "RES-003", "title": "交通違停與政策成因分析", "topic": "Traffic"},
    {"rid": "RES-004", "title": "五常公園設施狀況調查", "topic": "UrbanPlanning"},
    {"rid": "RES-005", "title": "環境噪音檢測", "topic": "Environment"},
    {"rid": "RES-006", "title": "變電箱負載與供電穩定性分析", "topic": "Energy"},
    {"rid": "RES-007", "title": "夜間照明與安全死角調查", "topic": "Security"},
    {"rid": "RES-008", "title": "通學路徑安全與結構性成因分析", "topic": "Education"},
    {"rid": "RES-009", "title": "老樹保護名冊調查", "topic": "Culture"},
    {"rid": "RES-010", "title": "避難收容所容量與物資調查", "topic": "Resilience"},
    {"rid": "RES-011", "title": "官商協商壟斷與利益輸送分析", "topic": "Politics"}
]

tasks = []

for item in base_tasks:
    # Create two reports for each research topic to enable comparison
    model_a = random.choice(models)
    model_b = random.choice([m for m in models if m != model_a])
    
    # Task A
    tasks.append({
        "event_id": f"{item['rid']}-A",
        "title": f"{item['title']} (Report A)",
        "metadata": {
            "type": "distributed_research_task",
            "status": "pending",
            "research_id": item['rid'],
            "topic": item['rid'], # Map to logic config key
            "category": item['topic'],
            "assigned_model": model_a
        }
    })
    
    # Task B
    tasks.append({
        "event_id": f"{item['rid']}-B",
        "title": f"{item['title']} (Report B)",
        "metadata": {
            "type": "distributed_research_task",
            "status": "pending",
            "research_id": item['rid'],
            "topic": item['rid'], # Map to logic config key
            "category": item['topic'],
            "assigned_model": model_b
        }
    })

with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"Reset {len(tasks)} research tasks (paired) in {EVENTS_FILE} for verification simulation.")
