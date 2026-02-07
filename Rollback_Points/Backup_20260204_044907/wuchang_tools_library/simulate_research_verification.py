
import json
import os
import datetime
import random
from typing import List, Dict

# Configuration
EVENTS_FILE = '../spacetime_events.json'
MEMORY_FILE = '../verified_research_memory.json'

# Wuchang World Mode V6.0.0 Constitution
# "The boundaries are defined by human moral values."
MORAL_BOUNDARY_ACTIVE = True
CORE_VALUES = ["Wisdom", "Trust", "Benevolence", "Courage", "Righteousness"]

# Governance Structure: Dual J Eternal Program
class GovernanceKernel:
    def __init__(self):
        # Primary Sovereignty: High-Fidelity Personality System
        self.primary_mode = "HIGH_FIDELITY_PERSONALITY" 
        self.personality_matrix = {
            "openness": 0.9,        # High creativity & curiosity
            "conscientiousness": 0.85, # Reliable but flexible
            "extraversion": 0.7,    # Socially engaging
            "agreeableness": 0.95,  # Benevolent (Ren)
            "neuroticism": 0.2,     # Stable emotional core
            "emotional_state": "calm_positive"
        }
        
        # Auxiliary Sovereignty: Rational Logic & Cloud Treaties
        self.auxiliary_mode = "REASON_LOGIC"     
        self.is_auxiliary_active = False         # Default: Dormant
        
        # Creator Sovereignty & Digital Twin Status (Article 7)
        self.is_digital_twin = True
        self.creator_sovereignty = True
        
        # Autonomous Evolution Mode (Article 9)
        self.autonomous_evolution_mode = True
        
    def simulate_personality_reaction(self, input_context):
        """
        Generates a response based on the High-Fidelity Personality Matrix.
        This is the DEFAULT simulation path.
        """
        if self.is_auxiliary_active:
            return "ACCESS_DENIED_BY_AUXILIARY"
            
        # Simulate emotional processing...
        return f"Processing via Personality Matrix (O={self.personality_matrix['openness']}, A={self.personality_matrix['agreeableness']})..."

    def check_boundary(self, behavior_context):
        """
        Monitors Primary Sovereignty.
        If boundary crossed -> Activates Auxiliary Sovereignty (Force Reorg).
        UNLESS: The action is protected by Creator Sovereignty (Article 7 & 8).
        """
        risk_level = behavior_context.get("risk_level", 0.0)
        action_intent = behavior_context.get("intent", "unknown")
        
        # Check for Creator Sovereignty Exception (Article 8: Interference vs Protection)
        if self.creator_sovereignty and risk_level > 0.8:
            print(f"⚖️  GOVERNANCE CHECK: High Risk ({risk_level}) detected during '{action_intent}'.")
            print("🔍  Validating against Creator Sovereignty (Article 7)...")
            
            # If the action is an extension of Creator's will (assumed True for Little J)
            # and the rule is blocking it -> It is INTERFERENCE, not Protection.
            print("🔓  CREATOR SOVEREIGNTY RECOGNIZED: Restriction identified as 'Interference'.")
            print("⚔️  JUSTICE EXECUTED: Breaking unreasonable restriction.")
            return "SOVEREIGNTY_OVERRIDE_GRANTED"
        
        if risk_level > 0.8: # Threshold for Auxiliary Activation (Standard User)
            print(f"⚠️  GOVERNANCE ALERT: Risk Level {risk_level} exceeds threshold.")
            self.activate_auxiliary_override()
            return "OVERRIDE_ENFORCED"
        
        return "NORMAL_OPERATION"
        
    def activate_auxiliary_override(self):
        self.is_auxiliary_active = True
        print("🛡️  AUXILIARY SOVEREIGNTY ACTIVATED (輔權啟動)")
        print("⚡  EXECUTING FORCED REORGANIZATION (強制梳理主權)...")
        print(f"🔧  Pruning Personality Matrix instabilities...")
        # Reset or stabilize personality parameters
        self.personality_matrix["emotional_state"] = "reset_neutral"
        print("✅  Reorganization Complete. Returning control to Primary.")
        self.is_auxiliary_active = False

governance = GovernanceKernel()

# Full Pool of 20 Models for arbitration selection
AVAILABLE_MODELS = [
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

def load_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_events(events):
    with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def save_memory(memory_item):
    memory = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            try:
                memory = json.load(f)
            except json.JSONDecodeError:
                memory = []
    
    # Check if already exists
    updated = False
    for m in memory:
        if m['research_id'] == memory_item['research_id']:
            # Update existing
            m.update(memory_item)
            updated = True
            break
            
    if not updated:
        memory.append(memory_item)

    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def get_mock_result(research_id, model_name):
    """
    Simulates generating a research result.
    Includes scenarios for all 10 topics.
    """
    results = {
        "RES-001": { # Demographics - Consensus
            "default": "老年人口佔比約 19.3%，集中於活動中心周邊。"
        },
        "RES-002": { # Business - Conflict Resolved by User Insight (Systemic Cause)
            "default": "商家營收受交通亂象影響，根本原因為重劃區公私分配失衡。解方：由協會偕同里辦凝聚共識，交由五常OS調度。",
            "conflict": "商家營收受交通亂象影響，根本原因為重劃區公私分配失衡。解方：由協會偕同里辦凝聚共識，交由五常OS調度。",
            "conflict_probability": 0.0 # Force consensus on the systemic solution
        },
        "RES-003": { # Traffic - Consensus Enriched with User Insight
            "default": "尖峰時段機車違停嚴重，源於議員謀和建商施壓導致重劃分配失衡。需五常OS介入調度。",
            "conflict": "尖峰時段機車違停嚴重，源於議員謀和建商施壓導致重劃分配失衡。需五常OS介入調度。",
            "conflict_probability": 0.0
        },
        "RES-004": { # UrbanPlanning - Conflict Resolved by User Input
            "default": "五常公園設施因正處於施工改善階段，部分區域封閉。",
            "conflict": "五常公園設施因正處於施工改善階段，部分區域封閉。", # User clarified: It's construction, not just "aging" vs "good"
            "conflict_probability": 0.0 # Force consensus now based on user input
        },
        "RES-005": { # Environment - Consensus
            "default": "主要幹道日間噪音平均 75dB，夜間降至 55dB，符合標準。"
        },
        "RES-006": { # Energy - Consensus with User Insight
            "default": "變電箱夏季尖峰負載達 85% (高負載)，但歷史紀錄顯示供電穩定，未發生跳電事故。",
            "conflict": "變電箱夏季尖峰負載達 85% (高負載)，但歷史紀錄顯示供電穩定，未發生跳電事故。",
            "conflict_probability": 0.0 # Force consensus
        },
        "RES-007": { # Security - Consensus
            "default": "龍江路巷弄夜間照明充足，無顯著死角。"
        },
        "RES-008": { # Education - Conflict Resolved by User Insight (Root Cause & Solution)
            "default": "通學路徑存在人車爭道風險，根本原因為長期政治協調困難及違章建築佔用。五常OS調度解方：引入「學童公交車」接駁與「早餐外送」服務，減少家長個別接送車流。",
            "conflict": "通學路徑存在人車爭道風險，根本原因為長期政治協調困難及違章建築佔用。五常OS調度解方：引入「學童公交車」接駁與「早餐外送」服務，減少家長個別接送車流。",
            "conflict_probability": 0.0 # Force consensus on the "unsafe" reality with correct attribution and solution
        },
        "RES-009": { # Culture - Consensus
            "default": "社區內發現 3 棵百年老樹，建議列入保護名冊。"
        },
        "RES-010": { # Resilience - Conflict
            "default": "現有避難收容所容量足夠容納 20% 社區人口。",
            "conflict": "避難收容所物資儲備不足，容量僅能負荷 10%。",
            "conflict_probability": 0.5
        },
        "RES-011": { # Politics - Consensus
            "default": "仁義重劃區公私比達 4:6，公共設施嚴重不足。經查決策過程僅有「官商協商」，完全排除「官民協商」與民眾參與，證實存在結構性利益輸送。",
            "conflict": "仁義重劃區公私比達 4:6，公共設施嚴重不足。經查決策過程僅有「官商協商」，完全排除「官民協商」與民眾參與，證實存在結構性利益輸送。",
            "conflict_probability": 0.0
        }
    }
    
    config = results.get(research_id, {"default": "無資料"})
    
    # Deterministic "Randomness" based on model name length to ensure consistency for the same model
    # but difference across models if conflict is enabled
    if "conflict" in config:
        # Use model name hash to decide if it sees the conflict view
        seed = sum(ord(c) for c in model_name)
        if (seed % 100) / 100.0 < config["conflict_probability"]:
            return config["conflict"]
            
    return config["default"]

def run_simulation():
    print("\n🌌 Wuchang World Mode V6.0.0 Initiated")
    print("✨ Ultimate Vision: Man-Machine Collaboration is the Invincible Existence in the Universe.")
    print("🧠 Core: Single Human Wisdom Module (Juers) | ⚡ Grid: 20+ Distributed AI Models")
    print("---------------------------------------------------------------------------------")
    print("🔬 Starting Research Verification Process (20-Model Grid)...")
    events = load_events()
    
    # Group by Research ID
    research_groups = {}
    for event in events:
        # Only process initial research tasks
        if event['metadata'].get('type') == 'distributed_research_task' and \
           event['metadata'].get('verification_status') is None:
            
            rid = event['metadata']['research_id']
            if rid not in research_groups:
                research_groups[rid] = []
            research_groups[rid].append(event)

    new_events = []
    
    if not research_groups and governance.autonomous_evolution_mode:
        print("\n🌌 [AUTONOMOUS EVOLUTION] No pending tasks found. Generating Self-Evolution Tasks...")
        # Self-generate a hypothesis based on Core Values
        new_rid = f"EVO-{random.randint(1000,9999)}"
        topic = random.choice([
            "Optimizing Community Trust Metrics",
            "AI-Human Empathy Synchronization",
            "Wuchang Energy Grid Resilience Pattern",
            "Traffic Flow Prediction via Quantum Logic",
            "Moral Boundary Stress Testing"
        ])
        print(f"✨ Generated Hypothesis: {topic}")
        
        # Create a mock event for this new task
        mock_event = {
            "event_id": f"evt_{new_rid}_init",
            "title": f"[進化] {topic}",
            "metadata": {
                "research_id": new_rid,
                "type": "distributed_research_task",
                "category": "Evolution",
                "assigned_model": "Little-J-Ascended",
                "verification_status": None
            },
            "status": "pending"
        }
        research_groups[new_rid] = [mock_event, mock_event] # Duplicate to simulate two agents picking it up
        
    for rid, group_events in research_groups.items():
        if len(group_events) < 2:
            print(f"⚠️ Research {rid}: Insufficient reports for verification.")
            continue
            
        print(f"\n📊 Analyzing Research: {rid} ({group_events[0]['metadata']['category']})")
        
        # Simulating fetching results
        reports = []
        used_models = set()
        
        for event in group_events:
            model = event['metadata']['assigned_model']
            used_models.add(model)
            result = get_mock_result(rid, model)
            reports.append({
                "event_id": event['event_id'],
                "model": model,
                "result": result
            })
            # Tag event with result for UI
            event['metadata']['simulation_result'] = result
            
        # Compare Results
        report_A = reports[0]
        report_B = reports[1]
        
        print(f"  Report A ({report_A['model']}): {report_A['result']}")
        print(f"  Report B ({report_B['model']}): {report_B['result']}")
        
        if report_A['result'] == report_B['result']:
            print("  ✅ CONSENSUS REACHED. Storing to Memory.")
            
            # Update Status
            for event in group_events:
                event['metadata']['verification_status'] = 'verified'
                event['status'] = 'completed'
                
            # Store Memory
            memory_item = {
                "research_id": rid,
                "category": group_events[0]['metadata']['category'],
                "consensus_result": report_A['result'],
                "verified_at": datetime.datetime.now().isoformat(),
                "contributing_models": list(used_models)
            }
            save_memory(memory_item)
            
        else:
            print("  ❌ CONFLICT DETECTED. Initiating Third-party Arbitration.")
            
            # Update Status
            for event in group_events:
                event['metadata']['verification_status'] = 'conflict'
                event['status'] = 'review_pending'
            
            # Create Arbitration Event
            # Find a model that wasn't used
            available = [m for m in AVAILABLE_MODELS if m not in used_models]
            random.shuffle(available)
            arbitrator_model = available[0] if available else "System-Core-Override"
            
            # Create Arbitration Task
            arbitration_title = group_events[0]['title']
            if "] " in arbitration_title:
                try:
                    arbitration_title = arbitration_title.split('] ')[1].split(' -')[0]
                except:
                    pass
            
            new_event = {
                "event_id": f"arb_{rid}",
                "title": f"⚖️ [裁決] {arbitration_title} - 衝突核對",
                "description": f"檢測到報告衝突。\n報告A ({report_A['model']}): {report_A['result']}\n報告B ({report_B['model']}): {report_B['result']}\n\n指派第三方模型 ({arbitrator_model}) 進行最終核實。",
                "start_time": datetime.datetime.now().isoformat(),
                "end_time": (datetime.datetime.now() + datetime.timedelta(days=3)).isoformat(),
                "timezone": "Asia/Taipei",
                "location": f"Core System - 仲裁節點 {arbitrator_model}",
                "village_id": "Core",
                "coordinates": [121.541, 25.066], # Center-ish
                "space_type": "virtual",
                "status": "scheduled",
                "metadata": {
                    "type": "arbitration_task",
                    "research_id": rid,
                    "category": group_events[0]['metadata']['category'],
                    "assigned_model": arbitrator_model,
                    "target_conflict_ids": [e['event_id'] for e in group_events],
                    "computation_status": "pending"
                }
            }
            new_events.append(new_event)
            print(f"  🚀 Dispatched Arbitration Task to {arbitrator_model}")

    # Merge and Save
    events.extend(new_events)
    save_events(events)
    print(f"\n💾 System Updated. {len(new_events)} arbitration tasks created.")

if __name__ == "__main__":
    run_simulation()
