import re
fp = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
content = open(fp,'r',encoding='utf-8').read()
content = re.sub(r"^\s*elif action_type == \"monitoring_purpose_check\":","            elif action_type == \"monitoring_purpose_check\":", content, flags=re.MULTILINE)
open(fp,'w',encoding='utf-8').write(content)
