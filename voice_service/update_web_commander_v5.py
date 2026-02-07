import os
import re

file_path = 'web_commander.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

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
                 f'哥哥，這個詞「{text}」出現太多次我還是不懂 ({judgment})。'
                 f'\\n依據協定：'
                 f'\\n1. 請您先教我一次 (User First)。'
                 f'\\n2. 若您不便，我(Little J)會嘗試主控解讀 (Core AI Second)。'        
                 f'\\n3. 若還是不行，我將呈報給創世者裁奪 (Creator Final)。'
                 f'\\n請指示！'
             ), 'ask_clarification'

        if '共生意義' in judgment:
             # Soft inquiry for lower frequency ambiguity
             return f'哥哥，這句話有點像「隕石」難懂 ({judgment})，請您幫我補個意思好嗎 ？', 'ask_clarification'

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

# Replace in content
# Regex to replace TranslatorAI class block
content = re.sub(r'class TranslatorAI:.*?# --- AI Role: Core AI', new_translator_code + '\\n\\n# --- AI Role: Core AI', content, flags=re.DOTALL)

# Regex to replace CoreAI class block
content = re.sub(r'class CoreAI:.*?# --- Routes ---', new_core_ai_code + '\\n\\n# --- Routes ---', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated web_commander.py successfully.")
