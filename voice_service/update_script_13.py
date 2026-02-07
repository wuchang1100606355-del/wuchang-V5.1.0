import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# We want to force the "Sister" persona (Little J) for critical authorization steps.
# We will look for speak() calls inside check_confirmation and verify_sovereignty logic (if any) and add persona arguments.

# Logic: Replace `self.speak(self.get_persona_response("..."))` with `self.speak(self.get_persona_response("..."), model="gpt_sovits", persona="Little J")`
# Target keys: "monitor_necessity_check", "monitor_liability_check", "monitor_final_auth_wait", "monitoring_purpose_check" (which uses a direct string currently)

# 1. monitor_necessity_check
content = content.replace(
    'self.speak(self.get_persona_response("monitor_necessity_check"))',
    'self.speak(self.get_persona_response("monitor_necessity_check"), model="gpt_sovits", persona="Little J")'
)

# 2. monitor_liability_check (appears twice?)
content = content.replace(
    'self.speak(self.get_persona_response("monitor_liability_check"))',
    'self.speak(self.get_persona_response("monitor_liability_check"), model="gpt_sovits", persona="Little J")'
)

# 3. monitor_final_auth_wait
content = content.replace(
    'self.speak(self.get_persona_response("monitor_final_auth_wait"))',
    'self.speak(self.get_persona_response("monitor_final_auth_wait"), model="gpt_sovits", persona="Little J")'
)

# 4. Direct strings in monitoring_purpose_check (added in previous step)
# "收到。合理性已確認，真實目的已登錄。正在執行最高權限指令：啟動監控。"
# "未能確認指令的合理性與真實目的。為了避免誤判，操作中止。"

content = content.replace(
    'self.speak("收到。合理性已確認，真實目的已登錄。正在執行最高權限指令：啟動監控。")',
    'self.speak("收到。合理性已確認，真實目的已登錄。正在執行最高權限指令：啟動監控。", model="gpt_sovits", persona="Little J")'
)

content = content.replace(
    'self.speak("未能確認指令的合理性與真實目的。為了避免誤判，操作中止。")',
    'self.speak("未能確認指令的合理性與真實目的。為了避免誤判，操作中止。", model="gpt_sovits", persona="Little J")'
)

# 5. Also for the initial inquiry "monitor_privacy_inquiry"
# It's in run() loop:
# elif risk_level == "privacy_critical":
#    response = self.get_persona_response("monitor_privacy_inquiry")

# The speak call is generic: `self.speak(response)` a few lines down.
# We need to change how `speak` is called in `run` loop for these specific personas.
# Or we can bake the persona into the `speak` call logic in `run`.

# Let's find the block in `run`:
# if self.prioritize_correctness:
# ...
#    self.speak(response)

# We can change it to:
#    persona_arg = "Little J" if risk_level in ["critical", "privacy_critical", "family"] else None
#    self.speak(response, model="gpt_sovits" if persona_arg else "chattts", persona=persona_arg)

# Let's try to match the `self.speak(response)` line inside the `prioritize_correctness` block.
# This is risky with regex.
# Let's just modify the `monitor_privacy_inquiry` case directly if possible? No, it sets `response` string.

# Alternative: Modify `get_persona_response` to return a tuple? No, too invasive.

# Let's just look at the `run` loop logic.
# It looks like:
#                         else:
#                             response = self.get_persona_response("confirm_general", cmd=action)
#
#                         self.speak(response)

# We can replace `self.speak(response)` with a smarter block.
old_speak_block = '                        self.speak(response)'
new_speak_block = '''                        # Use Sister Persona for High Risk/Family interactions
                        current_persona = "Little J" if risk_level in ["critical", "privacy_critical", "family"] else None
                        current_model = "gpt_sovits" if current_persona else "chattts"
                        self.speak(response, model=current_model, persona=current_persona)'''

# We need to be careful about indentation.
# The `self.speak(response)` is inside `if self.prioritize_correctness:` which is inside `if action:`.
# Indentation seems to be 24 spaces (3 tabs) or similar.
# Let's use `content.replace` on the specific context.

# Context:
#                         else:
#                             response = self.get_persona_response("confirm_general", cmd=action)
# 
#                         self.speak(response)

context_str = '''                        else:
                            response = self.get_persona_response("confirm_general", cmd=action)

                        self.speak(response)'''

new_context_str = '''                        else:
                            response = self.get_persona_response("confirm_general", cmd=action)

                        # Use Sister Persona for High Risk/Family interactions
                        current_persona = "Little J" if risk_level in ["critical", "privacy_critical", "family"] else None
                        current_model = "gpt_sovits" if current_persona else "chattts"
                        self.speak(response, model=current_model, persona=current_persona)'''

if context_str in content:
    content = content.replace(context_str, new_context_str)
else:
    # Try with less context
    pass 

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
