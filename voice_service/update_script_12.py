import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update monitor_final_auth_wait script to include True Purpose Verification
# Find the SCRIPTS dictionary and update "monitor_final_auth_wait"
# We will use regex to find the key and replace its value.

new_final_auth_script = '''    "monitor_final_auth_wait": [
        "第五點：權責確認完畢。但我必須執行最後一道「真實意圖檢核」。哥哥，我知道您擁有顛倒黑白的最高權限，但請告訴我：您的真實目的是為了「安全」還是「管教」？我需要確認指令的合理性，而非盲目服從。",
        "收到。在提交最終簽章前，請讓我確認您的「真實目的」。即使是最高權限，我也不能只做應聲蟲。請問此監控是為了排除危險，還是教育必要？請確認其合理性。",
        "程序最後一步：意圖確認。哥哥，您的話就是法律，但為了不辜負這份權力，我必須確認您現在是清醒且理性的。請問此指令的「真實目的」為何？"
    ],'''

# Regex to match the existing "monitor_final_auth_wait": [ ... ],
pattern = r'"monitor_final_auth_wait":\s*\[(.*?)\]\s*,'
# Note: The original code has a trailing comma or closing brace.
# Let's use DOTALL to match across lines.
# And we need to be careful not to consume too much.

# Actually, let's just replace the specific strings if we can find them, or replace the whole block.
# The previous content was:
# "monitor_final_auth_wait": [
#        "第五點：權責確認完畢。正在提交「最高權限審查」給哥哥。請稍候，等待最終簽章。",
#        "收到。流程已走完前四點，現在進入最後關卡：最高權限簽核。正在呼叫哥哥確認。",
#        "了解。所有責任歸屬已釐清。最後一步：請求最高權限（哥哥）的最終核准。請稍待。"
#    ],

# We'll use a precise replace.
old_block_start = '"monitor_final_auth_wait": ['
# We will read lines and replace the block.
lines = content.splitlines()
new_lines = []
in_block = False
replaced = False

for line in lines:
    if '"monitor_final_auth_wait": [' in line:
        in_block = True
        # Insert new block
        new_lines.append(new_final_auth_script.strip().replace("    ", "        ")) # Adjust indent if needed
        replaced = True
    elif in_block:
        if "]," in line:
            in_block = False
            # new_lines.append(line) # No, the new block already has the closing bracket/comma if we included it?
            # Wait, my new_final_auth_script includes "],"
            # So we don't need to append the old closing line if we replaced the whole thing.
            # But let's check my new string. It ends with "],"
            # So we just skip the old lines until we hit "],"
            pass
        else:
            pass # Skip content lines
    else:
        new_lines.append(line)

# If regex is safer:
content_str = "\n".join(lines)
# Let's try to match the block with regex to be sure.
regex = r'"monitor_final_auth_wait":\s*\[[^\]]*\],'
match = re.search(regex, content, re.DOTALL)
if match:
    content = content.replace(match.group(0), new_final_auth_script.strip())
else:
    # Fallback: maybe indentation or something is different.
    # Let's just append it to SCRIPTS if not found (unlikely)
    pass

# 2. Update logic to handle the response to this "True Purpose" question.
# We need to add a new state: "monitoring_purpose_check"
# In check_confirmation:
# elif action_type == "monitoring_liability":
#    if confirmed:
#       speak(monitor_final_auth_wait)
#       pending_command = (cmd_data, "monitoring_purpose_check") # NEW STATE
#       return True

# And then handle "monitoring_purpose_check"
# elif action_type == "monitoring_purpose_check":
#    if "安全" in text or "管教" in text or "教育" in text or "是" in text:
#       speak("收到。合理性已確認。執行最高權限指令。")
#       # Execute
#       ...

# Let's modify check_confirmation.

# Find:
# elif action_type == "monitoring_liability":
# ...
#    if "愿意" in text ...
#         self.speak(self.get_persona_response("monitor_final_auth_wait"))
#         print(f"[System] Liability Accepted by User. Requesting Brother's Final Auth.")
#         self.pending_command = None 
#         return True

logic_replacement_search = '''            if "愿意" in text or "願意" in text or "是" in text or "确认" in text or "確認" in text:
                 self.speak(self.get_persona_response("monitor_final_auth_wait"))
                 print(f"[System] Liability Accepted by User. Requesting Brother's Final Auth.")
                 self.pending_command = None 
                 return True'''

logic_replacement_new = '''            if "愿意" in text or "願意" in text or "是" in text or "确认" in text or "確認" in text:
                 self.speak(self.get_persona_response("monitor_final_auth_wait"))
                 print(f"[System] Liability Accepted. Checking True Purpose.")
                 self.pending_command = (cmd_data, "monitoring_purpose_check")
                 self.confirmation_timeout = time.time() + 40
                 return True'''

if logic_replacement_search.strip() in content.strip(): # Loose match?
    # Strict match is risky with whitespace.
    # Let's use the unique print string.
    part1 = 'print(f"[System] Liability Accepted by User. Requesting Brother\'s Final Auth.")'
    if part1 in content:
        content = content.replace('self.pending_command = None', 'self.pending_command = (cmd_data, "monitoring_purpose_check")\n                 self.confirmation_timeout = time.time() + 40')
        content = content.replace(part1, 'print(f"[System] Liability Accepted. Checking True Purpose.")')
    else:
        print("Could not find Liability logic block.")

# Add the handler for monitoring_purpose_check
# We insert it after monitoring_liability block.
# Find the end of monitoring_liability block.
# It ends with:
#             else:
#                 self.speak("無法確認法律責任歸屬，操作取消。")
#                 self.pending_command = None
#                 return True

end_of_liability_block = '''            else:
                self.speak("無法確認法律責任歸屬，操作取消。")
                self.pending_command = None
                return True'''

# We need to insert the new elif block after this.
new_elif_block = '''
        elif action_type == "monitoring_purpose_check":
            # Step 5: True Purpose & Rationality Check
            if "安全" in text or "管教" in text or "教育" in text or "是" in text or "對" in text:
                 self.speak("收到。合理性已確認，真實目的已登錄。正在執行最高權限指令：啟動監控。")
                 print(f"[System] Highest Authority Intent Verified. Executing {cmd_data}...")
                 # Here we would actually trigger the monitoring code
                 self.pending_command = None
                 return True
            else:
                 self.speak("未能確認指令的合理性與真實目的。為了避免誤判，操作中止。")
                 self.pending_command = None
                 return True
'''

# We assume standard indentation (8 spaces)
# Find the end of the previous block and append.
# Since we don't have a unique marker after liability block easily, let's just replace the end of liability block with end + new block.

if end_of_liability_block.strip() in content:
    # Try to match exact whitespace if possible, or use replace on the unique string
    content = content.replace('self.speak("無法確認法律責任歸屬，操作取消。")', 'self.speak("無法確認法律責任歸屬，操作取消。")\n                self.pending_command = None\n                return True' + new_elif_block)
    # Wait, the replace string above repeats lines.
    # The original was:
    #                 self.speak("無法確認法律責任歸屬，操作取消。")
    #                 self.pending_command = None
    #                 return True
    
    # I should be careful not to duplicate.
    # Let's replace the WHOLE liability block or just the last 3 lines.
    pass

# Better approach for insertion:
# Find `elif action_type == "monitoring_liability":`
# Find the next `elif` or `else` or end of method?
# Actually, monitoring_liability is likely the last one I added.
# So I can just append it to the end of check_confirmation method?
# No, check_confirmation might have other stuff.
# Let's just use the string replacement on the last lines of liability block.
# "無法確認法律責任歸屬，操作取消。" is unique enough.

split_str = 'self.speak("無法確認法律責任歸屬，操作取消。")'
parts = content.split(split_str)
if len(parts) > 1:
    pre = parts[0]
    post = parts[1]
    # post starts with:
    #                 self.pending_command = None
    #                 return True
    # then maybe other elifs or end of function.
    
    # Let's capture the immediate next lines
    # It's hard to guess exact whitespace.
    # Let's assume the previous edit was successful and standard.
    
    # Let's write the whole file content out with regex replacement for safety.
    pass

# Re-reading file to ensure I have it right
pass

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
