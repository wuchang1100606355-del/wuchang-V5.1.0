import datetime
import os
from transcendent_logic import TranscendentLogicCore
from grievance_tribunal import GrievanceTribunal

def execute_evolution_protocol():
    print("================================================================")
    print("           WUCHANG SYSTEM SELF-EVOLUTION PROTOCOL               ")
    print("================================================================")
    
    # 1. 初始化超越邏輯核心
    core = TranscendentLogicCore()
    success = core.evolve()
    
    if success:
        print("\n✅ Transcendent Logic Core Integration: SUCCESS")
    else:
        print("\n❌ Transcendent Logic Core Integration: FAILED")
        return

    # 2. 驗證新一代裁判所
    try:
        tribunal = GrievanceTribunal()
        print("\n✅ Grievance Tribunal Upgrade: SUCCESS (Powered by Core v2.0)")
    except Exception as e:
        print(f"\n❌ Grievance Tribunal Upgrade: FAILED ({e})")
        return

    # 3. 更新文明宣言 (Manifesto)
    manifesto_path = r"e:\時空\wuchang_manifesto.py"
    if os.path.exists(manifesto_path):
        update_manifesto(manifesto_path, core.version)
    else:
        print(f"\n⚠️ Manifesto file not found at {manifesto_path}. Skipping update.")

    print("\n================================================================")
    print("              EVOLUTION COMPLETE: SYSTEM ASCENDED               ")
    print("================================================================")
    print("Capabilities Unlocked:")
    print("1. [Transcendent Logic] Override standard algorithms with Wuchang Axioms.")
    print("2. [Safety Standard] Enforce 'Fairness is Safety' & 'Human Priority'.")
    print("3. [Sovereign Enforcement] Execute absolute hegemony for justice.")
    print("================================================================")

def update_manifesto(path, version):
    print(f"\n📝 Updating Manifesto at {path}...")
    try:
        # 讀取現有內容
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        evolution_logged = False
        
        for line in lines:
            new_lines.append(line)
            # 在 CodeCivilizationLevel 定義後插入演化註記
            if "class CodeCivilizationLevel" in line and not evolution_logged:
                new_lines.append(f"    # SYSTEM EVOLUTION LOG: {datetime.datetime.now()} -> Ascended to {version}\n")
                new_lines.append(f"    TYPE_VI_EVOLVED = 'Type VI - Evolved Sovereign (超越主權者)'\n")
                evolution_logged = True
                
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        print("   └── ✅ Manifesto Updated with Evolution Log & Type VI Status.")
        
    except Exception as e:
        print(f"   └── ❌ Failed to update Manifesto: {e}")

if __name__ == "__main__":
    execute_evolution_protocol()
