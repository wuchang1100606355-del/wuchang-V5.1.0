import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add new SCRIPTS
scripts_insert = '''    "negotiate_monitoring": [
        "警告：AI無法完全辨識影像內容是否合規，且涉及高度隱私。此操作需要啟動「最高級別授權程序」。您確定要繼續嗎？",
        "監控功能涉及隱私與AI識別限制，可能產生誤判。為了安全，我們必須執行更嚴格的授權驗證。請問是否執行？"
    ],
    "strict_auth_required": [
        "收到確認。鑑於此項操作的敏感性，系統已鎖定。正在請求「最高權限負責人 (哥哥)」進行人工審核與授權。這是為了確保正確且安全的使用。",
        "了解。由於AI無法判斷影像合規性，為了避免錯誤，已將此請求轉發給哥哥進行「雙重驗證」。請等待授權通過。"
    ],
'''
# Find a place to insert in SCRIPTS (e.g., after confirm_general)
if "negotiate_monitoring" not in content:
    content = content.replace('    "confirm_general": [', scripts_insert + '    "confirm_general": [')

# 2. Add monitoring logic in run()
monitoring_logic = '''                elif "監控" in cmd_text or "監視" in cmd_text or ("看" in cmd_text and ("房間" in cmd_text or "小孩" in cmd_text)):
                    action = "monitor_child_room"
                    risk_level = "critical"
                    category = "monitoring"
'''

if "monitor_child_room" not in content:
    # Insert before "elif "正常" in cmd_text:"
    content = content.replace('elif "正常" in cmd_text:', monitoring_logic + '                elif "正常" in cmd_text:')

# 3. Handle critical risk in run()
critical_risk_logic = '''                        elif risk_level == "critical":
                            response = self.get_persona_response("negotiate_monitoring")
'''
if "elif risk_level == \"critical\":" not in content:
    # Insert before "elif risk_level == "family":"
    content = content.replace('if risk_level == "family":', 'if risk_level == "critical":\n                            response = self.get_persona_response("negotiate_monitoring")\n                        elif risk_level == "family":')

# 4. Handle monitoring in check_confirmation()
monitoring_confirm_logic = '''            elif action_type == "monitoring":
                self.speak(self.get_persona_response("strict_auth_required"))
                print(f"[System] Monitoring Request: {cmd_data} -> Forwarded to High-Level Auth (Brother)")
                self.pending_command = None
                return True
'''
if "elif action_type == \"monitoring\":" not in content:
    # Insert before "elif action_type == \"system\":"
    content = content.replace('elif action_type == "system":', monitoring_confirm_logic + '            elif action_type == "system":')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated voice_commander.py with monitoring auth logic.")
