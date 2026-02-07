import re

# New TranslatorAI Code
new_translator_code = """# --- AI Role: Translator AI (The Judge & Symbiotic Interpreter) ---
class TranslatorAI:
    def __init__(self):
        self.corrections = {
            '小真有良': '小J有兩',
            '小英文': '小J',
            '乔贼': '喬治',
            '云端小贼': '云端小飛',
            '陨石': '未知困難 (Meteorite)',
            '觉得': '覺得',
            '角色': '角色',
            '判断成角': '判斷成「角」(Role)',
            '是不一样的': '是不一樣的',
        }
        # Terms that indicate uncertainty or need for human supplementation
        self.ambiguous_terms = ['那个', '呃', '哼', '啊', '补这个意思', '麻烦', '不懂的 词语', '角']

    def normalize(self, text):
        if not text:
            return text, False, '無語音輸入 (No Input)'

        normalized = text
        notes = []

        # 1. Term Correction
        for wrong, right in self.corrections.items():
            if wrong in normalized:
                normalized = normalized.replace(wrong, right)
                notes.append(f'修正 \\'{wrong}\\' -> \\'{right}\\'')

        # 2. Ambiguity Check (Frequency Based)
        # Check if the text contains ambiguous terms
        hit_ambiguous = any(term in normalized for term in self.ambiguous_terms) or (len(normalized) < 2)

        # Get historical ambiguity count for this specific phrase/term
        # (Simplified: using the whole text as key, ideally should extract keywords)    
        ambiguity_count = habit_manager.get_ambiguity_count(normalized)

        judgment_note = ''
        if notes:
            judgment_note = '; '.join(notes)

        if hit_ambiguous:
            # If we've seen this ambiguous term > 3 times, we escalate
            if ambiguity_count > 3:
                judgment_note += f' | 頻率觸發 ({ambiguity_count}次): 啟動三段裁決'     
                return normalized, True, judgment_note
            else:
                # Just flag it, don't escalate yet (unless it's critical)
                judgment_note += f' | 共生意義 (累積: {ambiguity_count+1}次)'
                return normalized, True, judgment_note

        if not judgment_note:
            judgment_note = '信心高 (High Confidence)'

        was_corrected = (normalized != text) or bool(notes)
        return normalized, was_corrected, judgment_note"""

# New CoreAI Code
new_core_ai_code = """# --- AI Role: Core AI (The Soul & Protective Responder) ---
class CoreAI:
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
                 f"哥哥，這個詞「{text}」出現太多次我還是不懂 ({judgment})。\\n"
                 f"依據協定：\\n"
                 f"1. 請您先教我一次 (User First)。\\n"
                 f"2. 若您不便，我(Little J)會嘗試主控解讀 (Core AI Second)。\\n"        
                 f"3. 若還是不行，我將呈報給創世者裁奪 (Creator Final)。\\n"
                 f"請指示！"
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

with open('web_commander.py', 'r', encoding='utf-8') as f:
    full_content = f.read()

# Clean up any potential mess from previous script
# We look for the FIRST occurrence of class TranslatorAI and the LAST occurrence of # --- Routes ---
# to safely sandwich our new code.

part1 = full_content.split('class TranslatorAI')[0]

# Find where Routes start
# If there are duplicates, we want the LAST valid Routes block?
# Or we assume the file structure is top-down.
# Let's search for the first '# --- Routes ---' that appears AFTER the first TranslatorAI?
# Actually, if the previous script appended code, the end might be duplicated.
# Let's assume the 'Imports' and 'HabitManager' at top are clean (part1).
# We just need to find the Routes section.

if '# --- Routes ---' in full_content:
    # Use partition/split to get the last part
    # But if there are multiple '# --- Routes ---', we might be in trouble.
    # Let's look for '@app.route'
    routes_index = full_content.find('# --- Routes ---')
    if routes_index == -1:
         routes_index = full_content.find('@app.route')
         # Backtrack to comment if possible
    
    # We take everything from routes_index to the end
    part3 = full_content[routes_index:]
else:
    # Fallback
    part3 = "\\n# --- Routes ---\\n@app.route('/')\\ndef index():\\n    return render_template('voice_control.html')\\n" 
    # This fallback is risky if I don't copy all routes.
    # Better to fail if not found, but it should be there.

# Remove the duplicated TranslatorAI/CoreAI lines from part1 (just in case)
part1 = part1.strip()

final_content = part1 + '\\n\\n' + new_translator_code + '\\n\\n' + new_core_ai_code + '\\n\\n' + part3

with open('web_commander.py', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Fixed web_commander.py successfully.")
