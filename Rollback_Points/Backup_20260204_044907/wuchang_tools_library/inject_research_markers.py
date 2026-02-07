
import json
import os

MEMORY_FILE = 'verified_research_memory.json'
EVENTS_FILE = 'spacetime_events.json'

def inject_knowledge_nodes():
    print("💉 Injecting Verified Knowledge Nodes into Spacetime Map...")
    
    if not os.path.exists(MEMORY_FILE):
        print("❌ No verified memory found.")
        return

    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        memories = json.load(f)
        
    if not os.path.exists(EVENTS_FILE):
        print("❌ No events file found.")
        return
        
    with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
        events = json.load(f)
        
    # Filter out existing knowledge nodes to avoid duplicates
    events = [e for e in events if e.get('metadata', {}).get('type') != 'knowledge_node']
    
    new_nodes = 0
    for mem in memories:
        # Create a "Knowledge Node" event
        node = {
            "event_id": f"know_node_{mem['research_id']}",
            "title": f"🏆 [知識] {mem['category']} - 已驗證",
            "description": f"**共識結論**: {mem['consensus_result']}\n\n貢獻模型: {', '.join(mem['contributing_models'])}",
            "start_time": mem['verified_at'],
            "end_time": "2099-12-31T23:59:59", # Eternal
            "timezone": "Asia/Taipei",
            "location": "Wuchang Knowledge Base",
            "village_id": "Core",
            # Default coordinates (can be refined based on category)
            "coordinates": [121.541, 25.066], 
            "space_type": "virtual",
            "status": "active",
            "metadata": {
                "type": "knowledge_node",
                "research_id": mem['research_id'],
                "category": mem['category'],
                "consensus_result": mem['consensus_result']
            }
        }
        
        # Adjust coordinates based on category for better visualization
        if "Energy" in mem['category']:
            node['coordinates'] = [121.540, 25.065] # Near substation
        elif "Traffic" in mem['category']:
            node['coordinates'] = [121.542, 25.067] # Near main road
        elif "Business" in mem['category']:
            node['coordinates'] = [121.541, 25.066] # Commercial area
        elif "Education" in mem['category']:
            node['coordinates'] = [121.539, 25.064] # Near school
            
        events.append(node)
        new_nodes += 1
        
    with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Injected {new_nodes} Knowledge Nodes into {EVENTS_FILE}.")

if __name__ == "__main__":
    inject_knowledge_nodes()
