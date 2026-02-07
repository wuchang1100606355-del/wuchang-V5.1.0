import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add new SCRIPTS
scripts_insert = '''    "monitor_self_confirm": [
        "了解，確認為使用者本人空間測試。無需額外授權。監控啟動。",
        "收到，針對您個人設備與空間的監控測試。權限驗證通過。"
    ],
    "monitor_privacy_inquiry": [
        "檢測到監控對象為他人。根據隱私原則，必須確認：被監控者是否「知情」？",
        "這涉及他人隱私空間。請問對方知道並同意被監控嗎？"
    ],
    "monitor_auth_verified": [
        "收到確認。既然對方知情且您擁有權限，系統將記錄此授權。但為了安全，仍將請求哥哥進行最終簽章。",
        "知情同意確認。正在連接最高權限負責人以進行最終核准。"
    ],
'''
# Insert after existing monitor scripts
if "monitor_self_confirm" not in content:
    content = content.replace('    "negotiate_monitoring": [', scripts_insert + '    "negotiate_monitoring": [')

# 2. Update logic in run() to differentiate Self vs Others
# Find the monitoring block we added previously
old_monitoring_block = '''                elif "監控" in cmd_text or "監視" in cmd_text or ("看" in cmd_text and ("房間" in cmd_text or "小孩" in cmd_text)):
                    action = "monitor_child_room"
                    risk_level = "critical"
                    category = "monitoring"
'''

new_monitoring_block = '''                elif "監控" in cmd_text or "監視" in cmd_text or ("看" in cmd_text and ("房間" in cmd_text or "小孩" in cmd_text)):
                    if "自己" in cmd_text or "我的" in cmd_text or "測試" in cmd_text:
                        action = "monitor_self"
                        risk_level = "medium"
                        category = "monitoring"
                    else:
                        action = "monitor_others"
                        risk_level = "privacy_critical"
                        category = "monitoring"
'''

# Replace the block (using a broader match to be safe, or just regex)
# Since we know the exact string we added, we can try to replace it.
# However, indentation might be tricky. Let's use regex.

pattern = r'elif "監控" in cmd_text.*?category = "monitoring"'
match = re.search(pattern, content, re.DOTALL)
if match:
    content = content.replace(match.group(0), new_monitoring_block.strip())

# 3. Update logic for risk_level handling
# We need to handle "privacy_critical"
risk_logic_insert = '''                        elif risk_level == "privacy_critical":
                            response = self.get_persona_response("monitor_privacy_inquiry")
'''
if 'elif risk_level == "privacy_critical":' not in content:
    content = content.replace('if risk_level == "critical":', 'if risk_level == "critical":\n                        elif risk_level == "privacy_critical":\n                            response = self.get_persona_response("monitor_privacy_inquiry")')

# Also handle "monitor_self" which is medium risk, but we might want specific script
# Actually, medium risk uses "confirm_medium_risk".
# Let's override specific action for self monitoring in the loop
specific_response_logic = '''                        if action == "monitor_self":
                            response = self.get_persona_response("monitor_self_confirm")
                        elif risk_level == "privacy_critical":
'''
content = content.replace('elif risk_level == "privacy_critical":', specific_response_logic)


# 4. Update check_confirmation for monitor_others
# We need to handle the "Yes" to privacy inquiry
confirm_logic_insert = '''            elif action_type == "monitoring":
                if cmd_data == "monitor_others":
                     if "知" in text or "是" in text or "同意" in text:
                          self.speak(self.get_persona_response("monitor_auth_verified"))
                          print(f"[System] Privacy Check Passed (Subject Aware). Requesting Final Auth.")
                          self.pending_command = None
                          return True
                     else:
                          self.speak("未獲確認。根據隱私規定，無法執行監控。")
                          return True
                else:
                    # monitor_self or legacy
                    self.speak(self.get_persona_response("strict_auth_required"))
                    self.pending_command = None
                    return True
'''

# Replace the previous monitoring confirmation block
old_confirm_block = '''            elif action_type == "monitoring":
                self.speak(self.get_persona_response("strict_auth_required"))
                print(f"[System] Monitoring Request: {cmd_data} -> Forwarded to High-Level Auth (Brother)")
                self.pending_command = None
                return True
'''
# Using replace
content = content.replace(old_confirm_block.strip(), confirm_logic_insert.strip())

# Fix indentation for the new block in check_confirmation
# The replace might mess up indentation if not careful.
# Let's write first then fix indentation with another script if needed.
# But python's replace is exact string.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated voice_commander.py with split monitoring logic.")
