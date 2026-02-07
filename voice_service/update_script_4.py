import os
file_path = r'J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Logic to inject into check_confirmation
# We look for the block handling 'family_discipline'
# The previous attempt failed because of whitespace or indentation mismatch.
# Let's locate the line: if action_type == "family_discipline":
# and replace the block following it.

old_block = '''            if action_type == "family_discipline":
                # Step 1: User Confirms they want to do it -> Ask for Router Auth       
                self.speak(self.get_persona_response("ask_router_auth"))
                self.pending_command = (cmd_data, "router_auth_received")
                self.confirmation_timeout = time.time() + 20
                return True'''

new_block = '''            if action_type == "family_discipline":
                # Double Brain Correction
                if "用油气" in text or "用油氣" in text:
                     print("[System] Auto-Correcting: '用油氣' -> '路由器' (Router)")
                
                target = "設備"
                if "手機" in text or "手机" in text:
                    target = "手機"
                elif "電腦" in text or "电脑" in text:
                    target = "電腦"

                # Acknowledge device before asking for auth
                if target != "設備":
                     self.speak(f"確認鎖定弟弟的{target}。")
                
                self.speak(self.get_persona_response("ask_router_auth"))
                self.pending_command = (cmd_data, "router_auth_received")
                self.confirmation_timeout = time.time() + 20
                return True'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Success')
else:
    print('Not found')
