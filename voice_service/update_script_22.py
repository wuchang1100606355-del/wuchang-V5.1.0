import re
fp = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
content = open(fp,'r',encoding='utf-8').read()
content = content.replace("          self.recognizer_alt = sr.Recognizer()","        self.recognizer_alt = sr.Recognizer()")
open(fp,'w',encoding='utf-8').write(content)
