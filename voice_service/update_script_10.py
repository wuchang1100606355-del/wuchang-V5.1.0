import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the monitor_privacy_inquiry list with the new version containing the preamble
old_scripts = '''    "monitor_privacy_inquiry": [
        "檢測到監控對象為他人。根據隱私原則，必須確認：被監控者是否「知情」？",
        "這涉及他人隱私空間。請問對方知道並同意被監控嗎？"
    ],'''

new_scripts = '''    "monitor_privacy_inquiry": [
        "家人您好，我們非常願意幫忙，也會盡力完成您的需求。但為了防止科技被濫用，我們必須經過一連串較為複雜的程序。首先確認：被監控者是否「知情」？",
        "我們很樂意協助，但為了保護大家的安全，必須執行嚴格的驗證程序。我們會盡力幫您。請問：對方知道並同意被監控嗎？"
    ],'''

# We need to find the old script block. Since indentation might vary or I might have edited it before...
# Let's search for "monitor_privacy_inquiry" and replace the whole list.

# Using regex to capture the list content
pattern = r'"monitor_privacy_inquiry": \[\s*".*?",\s*".*?"\s*\],'
# This regex is a bit risky if lines are split. Let's try to match structurally.
# Or simpler:
if old_scripts.strip() in content:
    content = content.replace(old_scripts.strip(), new_scripts.strip())
else:
    # Fallback to regex if exact string match fails due to whitespace
    print("Exact match failed, trying regex...")
    pattern = r'"monitor_privacy_inquiry":\s*\[(.*?)\]'
    # This might match too much if not careful with greedy matching.
    # Let's try to reconstruct what we wrote in previous turn.
    # Previous turn I wrote:
    # scripts_insert = '''    "monitor_necessity_check": [ ...
    # if "monitor_necessity_check" not in content:
    #    content = content.replace('    "monitor_privacy_inquiry": [', scripts_insert + '    "monitor_privacy_inquiry": [')
    
    # So "monitor_privacy_inquiry" is there.
    # Let's look for the key and replace the following lines until the closing bracket.
    
    lines = content.splitlines()
    new_lines = []
    skip = False
    for line in lines:
        if '"monitor_privacy_inquiry": [' in line:
            new_lines.append(new_scripts.strip())
            skip = True
        elif skip and '],' in line:
            skip = False
            # Don't append this line because new_scripts includes the closing bracket and comma
            continue 
        elif skip:
            continue
        else:
            new_lines.append(line)
    
    content = "\n".join(new_lines)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated voice_commander.py with empathetic monitoring preamble.")
