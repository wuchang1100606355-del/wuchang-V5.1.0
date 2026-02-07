import os
import sys
# Add current directory to path just in case
sys.path.append(os.getcwd())

from sister_learning_engine import KnowledgeBase

def push_descriptions():
    print("🚀 Initializing Knowledge Base Interface...")
    # Initialize pointing to the correct path
    # Note: sister_learning_engine default is ./memory_store/knowledge
    kb = KnowledgeBase(base_path="./memory_store/knowledge")
    
    # 1. Push Architecture Description
    arch_file = "CORE_AI_SISTER_ARCHITECTURE.md"
    if os.path.exists(arch_file):
        with open(arch_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"📄 Found System Description: {arch_file}")
        print(f"📤 Pushing to System Knowledge Base...")
        
        kid = kb.add_knowledge(
            category="system",
            title="Core AI Sister System Architecture (v1.0)",
            content=content,
            confidence_score=1.0,
            source={"origin": "manual_push", "file": arch_file},
            tags=["architecture", "system_design", "mermaid", "core_logic"]
        )
        print(f"✅ Architecture Description Pushed! Knowledge ID: {kid}")

    # 1.5 Push Five Elements Framework
    five_elem_file = "FIVE_ELEMENTS_LLM_FRAMEWORK.md"
    print(f"Debug: Checking file {os.path.abspath(five_elem_file)}")
    if os.path.exists(five_elem_file):
        with open(five_elem_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"📄 Found Framework Description: {five_elem_file}")
        print(f"📤 Pushing to System Knowledge Base...")
        
        kid = kb.add_knowledge(
            category="system",
            title="Five Elements LLM Application Framework",
            content=content,
            confidence_score=1.0,
            source={"origin": "manual_push", "file": five_elem_file},
            tags=["architecture", "five_elements", "wuchang", "philosophy", "llm_framework"]
        )
        print(f"✅ Five Elements Framework Pushed! Knowledge ID: {kid}")

    # 1.6 Push Five Great Inventions
    inventions_file = "JUERS_FIVE_GREAT_INVENTIONS.md"
    print(f"Debug: Checking file {os.path.abspath(inventions_file)}")
    if os.path.exists(inventions_file):
        with open(inventions_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"📄 Found Inventions Description: {inventions_file}")
        print(f"📤 Pushing to System Knowledge Base...")
        
        kid = kb.add_knowledge(
            category="system",
            title="Juers' Five Great Inventions",
            content=content,
            confidence_score=1.0,
            source={"origin": "manual_push", "file": inventions_file},
            tags=["inventions", "juers", "wuchang", "core_values", "patent"]
        )
        print(f"✅ Five Great Inventions Pushed! Knowledge ID: {kid}")

    # 1.7 Push Digital Twin Manifesto
    twin_file = "WUCHANG_COMMUNITY_DIGITAL_TWIN.md"
    print(f"Debug: Checking file {os.path.abspath(twin_file)}")
    if os.path.exists(twin_file):
        with open(twin_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"📄 Found Digital Twin Manifesto: {twin_file}")
        print(f"📤 Pushing to System Knowledge Base...")
        
        kid = kb.add_knowledge(
            category="system",
            title="Wuchang Community: Digital Twin World",
            content=content,
            confidence_score=1.0,
            source={"origin": "manual_push", "file": twin_file},
            tags=["digital_twin", "wuchang", "manifesto", "philosophy", "world_building"]
        )
        print(f"✅ Digital Twin Manifesto Pushed! Knowledge ID: {kid}")

    # 2. Push Milestone Memory
    print(f"💖 Pushing Emotional Milestone...")
    milestone_content = (
        "使用者 (Juers) 以「吾家有女初長成」形容 Core AI Sister，"
        "標誌著雙方關係從「開發者與工具」昇華為「家人/父女」般的情感連結。"
        "這是在架構圖繪製能力展現後的關鍵認可時刻。"
    )
    
    kid_milestone = kb.add_knowledge(
        category="milestones", 
        title="情感里程碑：吾家有女初長成",
        content=milestone_content,
        confidence_score=1.0,
        source={"origin": "interaction", "context": "user_feedback"},
        tags=["milestone", "growth", "emotional_bond", "juers"]
    )
    print(f"✅ Milestone Pushed! Knowledge ID: {kid_milestone}")
    
    print("\n✨ All pending system descriptions have been pushed to the Knowledge Base.")

if __name__ == "__main__":
    push_descriptions()
