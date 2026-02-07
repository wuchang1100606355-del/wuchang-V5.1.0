import os
file_path = r'J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old = 'if "斷網" in cmd_text or "切斷" in cmd_text or "切断" in cmd_text or ("弟弟" in cmd_text and "睡" in cmd_text):'
new = 'if "斷網" in cmd_text or "切斷" in cmd_text or "切断" in cmd_text or ("关掉" in cmd_text and ("网" in cmd_text or "網" in cmd_text)) or ("弟弟" in cmd_text and "睡" in cmd_text):'

if old in content:
    content = content.replace(old, new)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Success')
else:
    print('Not found')
