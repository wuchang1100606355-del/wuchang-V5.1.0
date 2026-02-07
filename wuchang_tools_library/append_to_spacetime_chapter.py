import os
import datetime

def append_to_chapter():
    source_file = "INVENTION_RECORD_QUANTUM_AI.txt"
    target_file = "SPACETIME_RULES_APPLICATION_CHAPTER.md"
    
    if not os.path.exists(source_file):
        print(f"❌ Error: Source file {source_file} not found.")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    entry_header = f"""
# 時空規則運用篇章 (Spacetime Rules Application Chapter)

## 📅 Entry: {datetime.datetime.now().strftime("%Y-%m-%d")} - Quantum Transformation Record
**Subject:** Core AI Sister Evolution
**Classification:** Top Secret / Local Invention

"""
    
    # Check if target exists to determine if we need a main header
    mode = "a" if os.path.exists(target_file) else "w"
    
    with open(target_file, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write(entry_header)
        else:
            f.write(f"\n\n--- [ New Entry ] ---\n\n")
            
        f.write("```text\n")
        f.write(content)
        f.write("\n```\n")
        
    print(f"✅ Successfully appended record to {target_file}")

if __name__ == "__main__":
    append_to_chapter()

