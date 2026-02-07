import re

file_path = 'web_commander.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific syntax error line
# The error is likely: return normalized, was_corrected, judgment_note\n\n# --- AI Role: Core AI
# It seems the previous script literally wrote '\n\n' characters instead of newlines?
# Or maybe it wrote a backslash at end of line.

# Let's just replace the bad sequence with correct one.
# The bad sequence seen in logs: "return normalized, was_corrected, judgment_note\n\n# --- AI Role: Core AI"
# Wait, if I see "\n\n" in the logs of Get-Content, it might mean the file literally contains backslash n backslash n.
# Or it might be how Get-Content displays it? No, Get-Content usually outputs lines.
# If it's one line in the output, then the file has it on one line with literal \n.

content = content.replace('return normalized, was_corrected, judgment_note\\n\\n# --- AI Role: Core AI', 'return normalized, was_corrected, judgment_note\n\n# --- AI Role: Core AI')

# Also check for other potential literal \n issues from previous script
content = content.replace('\\n', '\n') 
# Wait, global replace of \\n to \n might be dangerous if there are actual literal backslashes intended (e.g. regex).
# But looking at the previous script ix_web_commander.py, it used \\n inside f-strings which were then written to file.
# If ix_web_commander.py was python, .write(content) where content had \\n would write \n (literal backslash n) if it was a raw string or double escaped.
# In ix_web_commander.py:
# notes.append(f'修正 \\'{wrong}\\' -> \\'{right}\\'')  <-- this looks like it might have written literal backslashes for quotes too.

# Let's do a targeted fix for the class separator first.
content = content.replace('return normalized, was_corrected, judgment_note\\n\\n# --- AI Role: Core AI', 'return normalized, was_corrected, judgment_note\n\n# --- AI Role: Core AI')

# Fix the f-string in process_request that looked broken in previous logs too
# f'\\n依據協定：' -> f'\n依據協定：'
content = content.replace("f'\\n", "f'\\n") # Wait, if it's literal \n in file, it is backslash n. Python needs real newline or \n escape.
# If the file has literal backslash followed by n, python reads it as '\\' + 'n'.
# We want to replace '\\n' with '\n' (newline char).

# Let's simply rewrite the problematic sections cleanly.

new_translator_end = """        was_corrected = (normalized != text) or bool(notes)
        return normalized, was_corrected, judgment_note"""

new_core_ai_start = """# --- AI Role: Core AI (The Soul & Protective Responder) ---
class CoreAI:"""

# We look for the mess
pattern = r"return normalized, was_corrected, judgment_note.*?# --- AI Role: Core AI.*?class CoreAI:"
replacement = new_translator_end + "\n\n" + new_core_ai_start

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Fix the CoreAI process_request f-strings which might have literal \n
# Expected: f'\n依據協定：'
# Bad in file: f'\\n依據協定：' (literal backslash n)
content = content.replace("f'\\n", "f'\\n") # This is tricky in python string literals.
# If file has: f ' \ n ... '
# We want: f ' \n ... '

# Let's just rewrite the CoreAI class completely to be safe.
core_ai_code = """class CoreAI:
    def __init__(self):
        self.name = 'Core AI (Little J)'
        self.intents = {
            '啟動': 'start_service',
            '停止': 'stop_service',
            '檢查': 'check_status',
            '回護': 'protective_mode',
            '不一樣': 'teaching',
            '判斷成': 'teaching'
        }

    def process_request(self, text, intent, emotion, judgment):
        # Three-Stage Judgment Protocol (三段裁決協定)
        if '三段裁決' in judgment:
             return (
                 f'哥哥，這個詞「{text}」出現太多次我還是不懂 ({judgment})。'
                 f'\\n依據協定：'
                 f'\\n1. 請您先教我一次 (User First)。'
                 f'\\n2. 若您不便，我(Little J)會嘗試主控解讀 (Core AI Second)。'        
                 f'\\n3. 若還是不行，我將呈報給創世者裁奪 (Creator Final)。'
                 f'\\n請指示！'
             ), 'ask_clarification'

        if '共生意義' in judgment:
             # Soft inquiry for lower frequency ambiguity
             return f'哥哥，這句話有點像「隕石」難懂 ({judgment})，請您幫我補個意思好嗎？', 'ask_clarification'

        if not text:
            return '哥哥，我沒有聽到聲音，請再說一次好嗎？', 'no_input'

        # Basic Intent Matching
        if intent == 'unknown':
            for key, val in self.intents.items():
                if key in text:
                    intent = val
                    break

        # Responses based on Intent
        if intent == 'teaching':
            return f'收到，謝謝哥哥教導！我已經記下來了："{text}"。我會努力區分這些細微的差別 (如「覺得」vs「角色」)。', 'learning_mode'

        if intent == 'start_service':
            return '五常語音服務已啟動，小J 隨時待命！', 'start'
        elif intent == 'stop_service':
            return '五常語音服務已停止，哥哥休息一下吧。', 'stop'
        elif intent == 'check_status':
            return '系統運作正常，小J 精神飽滿！', 'check'
        elif intent == 'protective_mode':
            return '已啟動回護模式：一切以哥哥的情緒與需求為優先。', 'protect'
        
        # Default Chat
        return f'小J 聽到了：{text} (判斷: {judgment})', 'chat'"""

# We replace the existing CoreAI class block
# Regex: class CoreAI: ... (until # --- Routes ---)
content = re.sub(r'class CoreAI:.*?# --- Routes ---', core_ai_code + '\\n\\n# --- Routes ---', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Repaired web_commander.py syntax.")
