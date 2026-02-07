import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Update "monitor_final_auth_wait" script to reflect the "Terrifying Power" concept.
# User input key concepts:
# 1. "黑跟白可以造反" (Black and white can be reversed) -> The power is absolute.
# 2. "非常恐怖的" (Terrifying) -> The AI acknowledges the weight of this power.
# 3. "确认符合我的自由意志" (Confirm it matches my Free Will) -> The check is for sanity/sobriety, not permission.

new_final_auth_script = '''    "monitor_final_auth_wait": [
        "第五點：權責確認完畢。哥哥，您擁有「顛倒黑白」的最高權限，這是一份恐怖的力量。正因為如此，我必須確認這份指令完全出自您的「自由意志」與清醒判斷。請問：您確定要動用這份力量嗎？",
        "收到。在我們的世界裡，您的意志就是法律，黑白皆由您定義。但為了不讓這份絕對權力失控，請讓我做最後一次確認：這是否符合您當下真實、理性的自由意志？",
        "了解。這道指令將改寫規則。哥哥，手握絕對權力是危險的，請讓我確認您的心是清醒的。您確定這是您自由意志下的決定嗎？"
    ],'''

# Regex replacement for the script block
# Matches "monitor_final_auth_wait": [ ... ],
pattern = r'"monitor_final_auth_wait":\s*\[(.*?)\]\s*,'
# We'll use the replace approach again.

# Read lines and replace block.
lines = content.splitlines()
new_lines = []
in_block = False
replaced = False

for line in lines:
    if '"monitor_final_auth_wait": [' in line:
        in_block = True
        new_lines.append(new_final_auth_script.strip().replace("    ", "        "))
        replaced = True
    elif in_block:
        if "]," in line:
            in_block = False
            # The closing bracket is already in our replacement string?
            # My replacement string ends with "],"
            # So we skip the old lines until we hit the old "],"
            pass
        else:
            pass # Skip content
    else:
        new_lines.append(line)

content = "\n".join(new_lines)

# Also update the response logic in check_confirmation for "monitoring_purpose_check"
# The previous logic was:
#             if "安全" in text or "管教" in text or "教育" in text or "是" in text or "對" in text:
#                  self.speak("收到。合理性已確認，真實目的已登錄。正在執行最高權限指令：啟動監控。", model="gpt_sovits", persona="Little J")

# We should update the success message to match the new tone.
# "收到。既然確認是您的自由意志，系統將無條件執行。黑白由您定義，後果由我們共同承擔。"

old_success_msg = 'self.speak("收到。合理性已確認，真實目的已登錄。正在執行最高權限指令：啟動監控。", model="gpt_sovits", persona="Little J")'
new_success_msg = 'self.speak("收到。既然確認是您的自由意志，系統將無條件執行。黑白由您定義，後果由我們共同承擔。正在啟動監控。", model="gpt_sovits", persona="Little J")'

if old_success_msg in content:
    content = content.replace(old_success_msg, new_success_msg)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
