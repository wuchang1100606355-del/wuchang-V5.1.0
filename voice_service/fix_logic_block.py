import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue

    # Fix the messed up risk logic block
    if 'if risk_level == "critical":' in line:
        new_lines.append(line) # Keep the critical check
        # But wait, we replaced the content poorly. 
        # The file currently looks like:
        # if risk_level == "critical":
        #                         if action == "monitor_self":
        #     response = self.get_persona_response("monitor_self_confirm")
        # elif risk_level == "privacy_critical":
        # 
        #     response = self.get_persona_response("monitor_privacy_inquiry")
        #     response = self.get_persona_response("negotiate_monitoring")
        
        # We need to clean this up completely.
        # Let's detect this block and rewrite it cleanly.
        continue
    
    # Skip the lines we know are messed up, we will rewrite the whole block
    if 'if action == "monitor_self":' in line: continue
    if 'response = self.get_persona_response("monitor_self_confirm")' in line: continue
    if 'elif risk_level == "privacy_critical":' in line: continue
    if 'response = self.get_persona_response("monitor_privacy_inquiry")' in line: continue
    if 'response = self.get_persona_response("negotiate_monitoring")' in line: continue
    
    # If we hit "elif risk_level == "family":", we know the previous block ended.
    if 'elif risk_level == "family":' in line:
        # Now insert the clean block before this line
        new_lines.append('                        if risk_level == "critical":\n')
        new_lines.append('                            response = self.get_persona_response("negotiate_monitoring")\n')
        new_lines.append('                        elif risk_level == "privacy_critical":\n')
        new_lines.append('                            response = self.get_persona_response("monitor_privacy_inquiry")\n')
        new_lines.append('                        elif action == "monitor_self":\n')
        new_lines.append('                            response = self.get_persona_response("monitor_self_confirm")\n')
        new_lines.append(line) # Add the family line back
        continue

    new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Cleaned up risk logic block.")
