import re

file_path = 'J:\\共用雲端硬碟\\五常雲端空間\\voice_service\\web_commander.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Import
if 'from core_sister_memory import CoreSisterMemory' not in content:
    content = 'from core_sister_memory import CoreSisterMemory\n' + content
    print("Added import.")

# 2. Add Init in CoreAI or TranslatorAI
# Let's add it to CoreAI as it executes commands
if 'self.sister_memory = CoreSisterMemory()' not in content:
    pattern = r'(class CoreAI:.*?def execute\(self, command\):)'
    replacement = r'''class CoreAI:
    def __init__(self):
        self.sister_memory = CoreSisterMemory()

    def execute(self, command):'''
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print("Added CoreSisterMemory init to CoreAI.")

# 3. Add Review Logic in CoreAI.execute
# We want to replace the simple return with a review check
review_logic = '''
        # --- Core Sister Review (Meimei's Conscience) ---
        is_approved, reason = self.sister_memory.review_command_appropriateness(command, user_role="owner")
        if not is_approved:
            return f"[Sister Blocked] {reason}"
        elif "Override" in reason:
             # Log and continue
             pass
        # ------------------------------------------------
'''
if 'Core Sister Review' not in content:
    pattern = r'(def execute\(self, command\):)'
    replacement = r'\1' + review_logic
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print("Added review logic to CoreAI.")

# 4. Modify TranslatorAI to reference Humanity/Sister Concept
# Replace "Universal Value Treaty" with "Core Sister Conscience" in comments or strings if appropriate
# Or simply add a comment about the new architecture
architecture_comment = '''
# ==========================================
# HUMAN-MACHINE HYBRID ARCHITECTURE
# ------------------------------------------
# Human Layer: User Endpoint + CoreSisterMemory (Conscience/Warmth)
# Machine Layer: CoreAI Execution + Odoo Backend (Efficiency/Logging)
# ==========================================
'''
if 'HUMAN-MACHINE HYBRID ARCHITECTURE' not in content:
    content = architecture_comment + content
    print("Added Architecture Header.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
