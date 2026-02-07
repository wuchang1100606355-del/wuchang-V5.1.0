import re

file_path = 'J:\\共用雲端硬碟\\五常雲端空間\\voice_service\\voice_commander.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Review Logic before Confirmation Check
review_logic = '''
                # --- Core Sister Review (Meimei's Conscience) ---
                is_approved, reason = self.sister_memory.review_command_appropriateness(cmd_text, user_role="owner")
                if not is_approved:
                    self.speak(reason, model="gpt_sovits", persona="Little J")
                    print(f"[Core Sister] Command Blocked: {reason}")
                    continue
                elif "Override" in reason:
                     self.speak(reason, model="gpt_sovits", persona="Little J")
                # ------------------------------------------------

'''

if 'Core Sister Review' not in content:
    pattern = r'(# 0. Priority: Confirmation Check)'
    replacement = review_logic + r'\1'
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content, count=1)
        print("Added review logic.")
    else:
        print("Could not find insertion point for review logic.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
