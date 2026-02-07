import re

fp = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
content = open(fp, 'r', encoding='utf-8').read()

pattern = 'elif action_type == "monitor_space_check_init":'
occurs = [m.start() for m in re.finditer(pattern, content)]
if len(occurs) > 1:
    start = occurs[1]
    end = content.find('return True', start)
    if end != -1:
        end = end + len('return True')
        new_content = content[:start] + content[end:]
        open(fp, 'w', encoding='utf-8').write(new_content)
