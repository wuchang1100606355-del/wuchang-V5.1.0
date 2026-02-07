from voice_commander import VoiceCommander
import time

class TestCommander(VoiceCommander):
    def speak(self, text, model=None, persona=None):
        print(f"\n[AI Speaks ({persona or 'System'})]: {text}")

    def get_persona_response(self, key, **kwargs):
        # Force reload to get latest strings if they were modified in file but not re-imported (simulation)
        # Actually, since we import VoiceCommander, it uses the dict defined in the module.
        # We need to rely on the module having the updated dict.
        return super().get_persona_response(key, **kwargs)

def run_test():
    cmd = TestCommander()
    print("=== Testing 5-Point Monitoring Authorization Protocol ===")
    
    # 1. Initiate Monitoring of Unknown Device
    print("\n>>> User: 監控弟弟的房間")
    # Simulate run loop part manually or mock inputs
    # Since run() is a loop, we call the logic block directly.
    # verify_sovereignty will return False for "弟弟的房間"
    
    cmd_text = "監控弟弟的房間"
    is_sovereign, target_info = cmd.verify_sovereignty(cmd_text)
    print(f"[System] Sovereignty: {is_sovereign}")
    
    if not is_sovereign:
        # Should trigger "monitor_space_check_init"
        print("[System] Triggering Space Check...")
        cmd.speak(cmd.get_persona_response("monitor_space_check")[0], persona="Little J")
        cmd.pending_command = ("monitor_others", "monitor_space_check_init")
        
        # 2. User confirms "Private Space"
        print("\n>>> User: 這是私人空間")
        cmd.check_confirmation("這是私人空間")
        
        # 3. User says "Unaware" (Unknown)
        print("\n>>> User: 他不知道")
        # Logic: if "不知道" in text -> Necessity Check
        # But wait, logic in check_confirmation for "monitor_others" / "monitoring" handles this.
        # We need to see where check_confirmation went.
        # It transitioned to ("monitor_others", "monitoring") after space check.
        
        cmd.check_confirmation("他不知道")
        
        # 4. User says "Necessity is Yes"
        print("\n>>> User: 是必要的")
        cmd.check_confirmation("是必要的")
        
        # 5. User accepts Liability (The "Political Meaning")
        print("\n>>> User: 我願意承擔法律責任")
        cmd.check_confirmation("我願意承擔法律責任")
        
        # 6. User confirms Free Will (The "Terrifying Power")
        print("\n>>> User: 是的，這是我的自由意志")
        cmd.check_confirmation("是的，這是我的自由意志")

if __name__ == "__main__":
    run_test()
