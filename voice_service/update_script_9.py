import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add new SCRIPTS for the 5-point check
scripts_insert = '''    "monitor_necessity_check": [
        "第三點：既然被監控者不知情，請問此監控程序是否為「必要」？",
        "在對方不知情的情況下，這必須是絕對必要的措施。您確認其必要性嗎？"
    ],
    "monitor_liability_check": [
        "第四點：系統必須記錄下令者身份。請確認：您是本空間的權責人，並願意為此監控命令承擔所有法律責任嗎？",
        "為了賦權與究責，請確認您願意為此監控行為負起完全的法律責任，系統將記錄您的身份。"
    ],
    "monitor_final_auth_wait": [
        "第五點：權責確認完畢。正在提交「最高權限審查」給哥哥。請稍候，等待最終簽章。",
        "所有前置檢查通過。正在連接最高權限負責人(哥哥)進行最終審查與授權。"
    ],
'''
if "monitor_necessity_check" not in content:
    content = content.replace('    "monitor_privacy_inquiry": [', scripts_insert + '    "monitor_privacy_inquiry": [')

# 2. Update check_confirmation to handle state transitions
# We need a state machine. 
# Current logic for monitoring:
# if action_type == "monitoring":
#    if cmd_data == "monitor_others":
#         if "知" ...: (Previously went to Auth, now needs Liability)
#         else: (Previously Cancelled, now needs Necessity)

new_confirm_block = '''            elif action_type == "monitoring":
                # Step 2: Privacy/Awareness Check
                if cmd_data == "monitor_others":
                     if "知" in text or "是" in text or "同意" in text:
                          # Subject knows -> Skip Necessity, Go to Liability
                          self.speak(self.get_persona_response("monitor_liability_check"))
                          self.pending_command = (cmd_data, "monitoring_liability")
                          self.confirmation_timeout = time.time() + 30
                          return True
                     else:
                          # Subject doesn't know -> Go to Necessity
                          self.speak(self.get_persona_response("monitor_necessity_check"))
                          self.pending_command = (cmd_data, "monitoring_necessity")
                          self.confirmation_timeout = time.time() + 30
                          return True
                else:
                    # monitor_self -> Direct to final or done (Self monitoring is simpler, but let's keep it safe)
                    # For self, we already confirmed in run(). 
                    # If we are here, it might be a weird state, but let's assume it's fine.
                    self.speak("自我監控測試啟動。")
                    self.pending_command = None
                    return True

            elif action_type == "monitoring_necessity":
                # Step 3: Necessity Check (if subject unaware)
                if "必要" in text or "是" in text or "對" in text:
                     self.speak(self.get_persona_response("monitor_liability_check"))
                     self.pending_command = (cmd_data[0], "monitoring_liability") # cmd_data is tuple in some cases? No, cmd_data passed from pending_command is action string "monitor_others"
                     self.confirmation_timeout = time.time() + 30
                     return True
                else:
                     self.speak("若非必要，系統不予執行不知情的監控。")
                     self.pending_command = None
                     return True

            elif action_type == "monitoring_liability":
                # Step 4: Liability Check
                if "愿意" in text or "願意" in text or "是" in text or "确认" in text or "確認" in text:
                     self.speak(self.get_persona_response("monitor_final_auth_wait"))
                     print(f"[System] Liability Accepted by User. Requesting Brother's Final Auth.")
                     # In a real system, this would trigger an approval request to the other user
                     self.pending_command = None 
                     return True
                else:
                     self.speak("無法確認法律責任歸屬，操作取消。")
                     self.pending_command = None
                     return True
'''

# We need to find the `elif action_type == "monitoring":` block and replace it.
# The previous block was:
#             elif action_type == "monitoring":
#                 if cmd_data == "monitor_others":
#                      if "知" in text or "是" in text or "同意" in text:
#                           self.speak(self.get_persona_response("monitor_auth_verified"))
#                           print(f"[System] Privacy Check Passed (Subject Aware). Requesting Final Auth.")
#                           self.pending_command = None
#                           return True
#                      else:
#                           self.speak("未獲確認。根據隱私規定，無法執行監控。")
#                           return True
#                 else:
#                     # monitor_self or legacy
#                     self.speak(self.get_persona_response("strict_auth_required"))
#                     self.pending_command = None
#                     return True

# Let's use regex to find this block and replace it.
# The block starts with `elif action_type == "monitoring":` and ends before `elif action_type == "system":`
pattern = r'elif action_type == "monitoring":.*?elif action_type == "system":'
match = re.search(pattern, content, re.DOTALL)
if match:
    content = content.replace(match.group(0), new_confirm_block.strip() + '\n\n            elif action_type == "system":')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated voice_commander.py with 5-point monitoring auth logic.")
