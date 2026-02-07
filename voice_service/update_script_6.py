import os
import re

file_path = r'J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Using a simpler string replacement for the key line to locate the block
search_line = 'if action_type == "family_discipline":'
if search_line in content:
    # Find the index
    idx = content.find(search_line)
    
    # We want to insert the new logic RIGHT AFTER this line
    # But we need to handle the original indentation
    
    # Let's construct the new block content with proper indentation (16 spaces based on context)
    new_logic = '''
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
'''
    # We insert it after the search line
    # We need to find the newline after search_line
    newline_idx = content.find('\n', idx)
    
    new_content = content[:newline_idx] + new_logic + content[newline_idx:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Success')
else:
    print('Not found')
