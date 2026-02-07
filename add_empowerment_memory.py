import json
import os

file_path = r'J:\\共用雲端硬碟\\五常雲端空間\\INTELLIGENCE_CORE\\core_memory\\core_memory.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check existing user scope memories
    user_memories = data.get('user_scope', [])
    
    # Add new memory
    new_memory = {
        "id": "ai_empowerment_miracle_4months",
        "title": "AI賦能奇蹟：0基礎4個月變資深架構師",
        "keywords": "AI賦能|意圖驅動|雙J共生|Gemini案例|Google Startup",
        "content": "創辦人 Juers 透過「意圖驅動開發」與 AI 協作，於 4 個月內從零基礎構建出資深架構師級別的系統。此案例驗證了 Google AI 工具的普惠性與極限潛力，是 Google for Startups 最具說服力的成功案例。"
    }
    
    # Add to list (handle limit if necessary, but assuming space based on context)
    user_memories.append(new_memory)
    data['user_scope'] = user_memories
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Successfully added empowerment memory.")

except Exception as e:
    print(f"Error: {e}")
