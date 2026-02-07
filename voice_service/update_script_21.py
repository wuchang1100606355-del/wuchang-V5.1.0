import re
fp = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
content = open(fp,'r',encoding='utf-8').read()

start_pat = '\n            elif action_type == "monitor_space_check_init":'
start_idx = content.find(start_pat)
if start_idx != -1:
    next_elif_idx = content.find('\n            elif action_type', start_idx+1)
    if next_elif_idx != -1:
        new_block = '\n            elif action_type == "monitor_space_check_init":\n                if "私密" in text:\n                    self.speak("檢測到高度敏感的私密空間。警告：此類監控需絕對必要性與最高權限。正在進入知情同意確認程序。請問被監控者是否「知情」？", model="gpt_sovits", persona="Little J")\n                    self.pending_command = ("monitor_others", "monitoring")\n                    self.confirmation_timeout = time.time() + 30\n                    return True\n                elif "私人" in text:\n                    self.speak("確認為私人空間。隱私權限啟動。請問被監控者是否「知情」？", model="gpt_sovits", persona="Little J")\n                    self.pending_command = ("monitor_others", "monitoring")\n                    self.confirmation_timeout = time.time() + 30\n                    return True\n                elif "公共" in text:\n                    self.speak("確認為公共空間。但仍需確認：相關人員是否「知情」？", model="gpt_sovits", persona="Little J")\n                    self.pending_command = ("monitor_others", "monitoring")\n                    self.confirmation_timeout = time.time() + 30\n                    return True\n                else:\n                    self.speak("無法確認空間屬性，請回答「公共」、「私人」或「私密」。")\n                    return True'
        content = content[:start_idx] + new_block + content[next_elif_idx:]
        open(fp,'w',encoding='utf-8').write(content)
