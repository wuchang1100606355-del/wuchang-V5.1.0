import re
fp = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
content = open(fp,'r',encoding='utf-8').read()

# add secondary recognizer in __init__
content = content.replace("self.recognizer = sr.Recognizer()","self.recognizer = sr.Recognizer()\n          self.recognizer_alt = sr.Recognizer()")

# enhance listen with dual ASR
listen_pattern = r"def listen\(self\):[\s\S]*?return None"  
m = re.search(listen_pattern, content)
if m:
    block = m.group(0)
    new_block = block.replace(
        "text = self.recognizer.recognize_google(audio, language=\"zh-TW\")\n\n                  print(f\"[You (Voice)]: {text}\")\n                  return text",
        "text1 = self.recognizer.recognize_google(audio, language=\"zh-TW\")\n                  text2 = None\n                  try:\n                      text2 = self.recognizer_alt.recognize_google(audio, language=\"zh-CN\")\n                  except Exception:\n                      text2 = text1\n                  if text1 != text2:\n                      self.speak(f\"我收到兩種不同辨識結果：{text1} / {text2}。請以自然語言確認您真正的意思。\")\n                  print(f\"[You (Voice)]: {text1}\")\n                  return text1"
    )
    content = content.replace(block, new_block)

open(fp,'w',encoding='utf-8').write(content)
