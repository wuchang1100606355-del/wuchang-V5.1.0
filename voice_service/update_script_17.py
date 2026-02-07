import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add the logic for handling "monitoring_purpose_check" state in check_confirmation
# This was missing in previous steps, we only added the transition to it.

# We need to find where to insert:
# elif action_type == "monitoring_purpose_check":
#    ...

# Best place is after the "monitoring_liability" block.
# Look for: elif action_type == "monitoring_liability": ... (block ends) ... return True

insert_point_str = '''                       self.pending_command = None
                       return True

              elif action_type == "system":'''

# Wait, we just modified the file to change self.pending_command = None to self.pending_command = (cmd_data, "monitoring_purpose_check")
# So we should look for that new signature.

insert_point_str_new = '''                       self.pending_command = (cmd_data, "monitoring_purpose_check")
                       self.confirmation_timeout = time.time() + 60
                       return True'''

new_purpose_check_block = '''
              elif action_type == "monitoring_purpose_check":
                  # Step 5: True Purpose & Rationality Check (The "Terrifying Power" Confirmation)
                  if "安全" in text or "管教" in text or "教育" in text or "是" in text or "對" in text or "意志" in text or "自由" in text:
                       self.speak("收到。既然確認是您的自由意志，系統將無條件執行。黑白由您定義，後果由我們共同承擔。正在啟動監控。", model="gpt_sovits", persona="Little J")
                       print(f"[System] Highest Authority Intent Verified. Executing {cmd_data}...")
                       self.pending_command = None
                       return True
                  else:
                       self.speak("未能確認指令的合理性與真實目的。為了避免誤判，操作中止。", model="gpt_sovits", persona="Little J")
                       self.pending_command = None
                       return True'''

# Normalize spaces for matching
# The file content has indented lines.
# Let's try to find the insertion point by index.

idx = content.find('self.pending_command = (cmd_data, "monitoring_purpose_check")')
if idx != -1:
    # Find the next 'return True'
    return_idx = content.find('return True', idx)
    if return_idx != -1:
        # Insert after this 'return True'
        insertion_index = return_idx + len('return True')
        
        new_content = content[:insertion_index] + new_purpose_check_block + content[insertion_index:]
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
