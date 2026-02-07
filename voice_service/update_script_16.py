import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update monitor_liability_check to reflect the 5-point protocol more formally as requested
# User wants "political/formal meaning" (政治含义) - emphasizing "Legal Liability" and "Identification"
new_liability_check = '''    "monitor_liability_check": [
        "第四點：系統必須記錄下令者身份。請確認：您是本空間的權責人，並願意為此監控命令承擔所有法律責任嗎？",
        "為了賦權與究責，請確認您願意為此監控行為負起完全的法律責任，系統將記錄您的身份。"
    ],'''

# Regex to replace monitor_liability_check block
pattern_liability = r'"monitor_liability_check":\s*\[(.*?)\]\s*,'
content = re.sub(pattern_liability, new_liability_check.strip().replace("    ", "        "), content, flags=re.DOTALL)

# 2. Fix the logic flow in check_confirmation
# Previously:
# if "愿意" in text ... -> self.pending_command = None; return True (Wait, it ended too early!)
# It should transition to "monitoring_purpose_check" (The "Terrifying Power" check)

# Let's find the block:
# elif action_type == "monitoring_liability":
#    if ...
#       self.speak(self.get_persona_response("monitor_final_auth_wait")...)
#       self.pending_command = None  <-- THIS IS WRONG. It should be waiting for the next step.

# We need to replace:
# self.pending_command = None
# with:
# self.pending_command = (cmd_data, "monitoring_purpose_check")
# self.confirmation_timeout = time.time() + 30

# Locate the specific block for liability check success
target_block = '''elif action_type == "monitoring_liability":
                  # Step 4: Liability Check
                  if "愿意" in text or "願意" in text or "是" in text or "确认" in text or "確認" in text:
                       self.speak(self.get_persona_response("monitor_final_auth_wait"), model="gpt_sovits", persona="Little J")
                       print(f"[System] Liability Accepted by User. Requesting Brother's Final Auth.")
                       # In a real system, this would trigger an approval request to the other user
                       self.pending_command = None
                       return True'''

new_block = '''elif action_type == "monitoring_liability":
                  # Step 4: Liability Check
                  if "愿意" in text or "願意" in text or "是" in text or "确认" in text or "確認" in text:
                       self.speak(self.get_persona_response("monitor_final_auth_wait"), model="gpt_sovits", persona="Little J")
                       print(f"[System] Liability Accepted by User. Requesting Brother's Final Auth.")
                       # Transition to Step 5: Purpose/Free Will Check
                       self.pending_command = (cmd_data, "monitoring_purpose_check")
                       self.confirmation_timeout = time.time() + 60 # Give more time for this serious question
                       return True'''

# Normalize indentation for replacement
target_block_norm = re.sub(r'\s+', ' ', target_block).strip()
new_block_norm = new_block

# Since indentation varies, let's use a regex to find the block start and replace the body
# We look for: elif action_type == "monitoring_liability": ... if ... : ... self.pending_command = None ... return True
# And change self.pending_command = None to the new state.

# Actually, the file content we read earlier shows:
# self.pending_command = None
# return True
# inside the if block.

# Let's try to replace the specific lines inside that block using string replacement if unique enough.
lines = content.splitlines()
new_lines = []
in_liability_success = False

for i, line in enumerate(lines):
    if 'elif action_type == "monitoring_liability":' in line:
        new_lines.append(line)
    elif 'if "愿意" in text' in line and 'monitoring_liability' in lines[i-2]: # context check roughly
        new_lines.append(line)
        in_liability_success = True
    elif in_liability_success and 'self.speak(self.get_persona_response("monitor_final_auth_wait")' in line:
        new_lines.append(line)
    elif in_liability_success and 'self.pending_command = None' in line:
        # Found the line to change!
        indent = line[:line.find('self.pending_command')]
        new_lines.append(f'{indent}self.pending_command = (cmd_data, "monitoring_purpose_check")')
        new_lines.append(f'{indent}self.confirmation_timeout = time.time() + 60')
        in_liability_success = False # Done replacing
    else:
        new_lines.append(line)

content = "\n".join(new_lines)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
