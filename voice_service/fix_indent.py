import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Fix the specific monitoring line
    if 'elif "監控" in cmd_text' in line:
        line = line.lstrip() # Remove all leading spaces
        line = "                " + line # Add correct 16 spaces
    # Fix the lines following it (action, risk_level, category)
    elif 'action = "monitor_child_room"' in line:
        line = line.lstrip()
        line = "                    " + line # 20 spaces
    elif 'risk_level = "critical"' in line:
        line = line.lstrip()
        line = "                    " + line
    elif 'category = "monitoring"' in line:
        line = line.lstrip()
        line = "                    " + line
    
    new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Indentation fixed.")
