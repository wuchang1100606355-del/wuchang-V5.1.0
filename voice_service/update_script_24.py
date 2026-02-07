import re

file_path = 'J:\\共用雲端硬碟\\五常雲端空間\\voice_service\\voice_commander.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Import
if 'from core_sister_memory import CoreSisterMemory' not in content:
    content = 'from core_sister_memory import CoreSisterMemory\n' + content
    print("Added import.")

# 2. Add Init
if 'self.sister_memory = CoreSisterMemory()' not in content:
    pattern = r'(class VoiceCommander.*?:.*?def __init__\(self.*?\):.*?)(        self\.recognizer = sr\.Recognizer\(\))'
    replacement = r'\1        self.sister_memory = CoreSisterMemory()\n\2'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print("Added init.")

# 3. Add Review Logic in Run Loop
# We look for 'if cmd_text:' inside 'def run(self):'
# And insert the review check immediately after.
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
    # Find 'if cmd_text:' followed by newline and indentation
    # Be careful not to match other 'if cmd_text:' if any (there is usually one main one in run)
    # The main one is usually inside 'while True:'
    pattern = r'(cmd_text = self\.listen\(\)\s+if cmd_text:)'
    replacement = r'\1' + review_logic
    
    # Check if match exists
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content, count=1)
        print("Added review logic.")
    else:
        print("Could not find insertion point for review logic.")

# 4. Add Logging to Purpose Check Success
# Find the block where we say "收到。既然確認是您的自由意志..."
# And add logging there.
log_logic = '''
                 self.sister_memory.log_audit_event("Juers", "Owner Channel", "HIGH_RISK_EXECUTION", "AUTHORIZED", f"Executed: {self.pending_command} - Reason: {text}")
'''
if 'self.sister_memory.log_audit_event' not in content:
    pattern = r'(self\.speak\("收到。既然確認是您的自由意志.*?)(print\(f"\[System\] Highest Authority Intent Verified)'
    replacement = r'\1' + log_logic + r'\2'
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("Added logging logic.")
    else:
        print("Could not find insertion point for logging logic.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
