import os
import re

file_path = r'wuchang_os\addons\wuchang_core\controllers\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix path variables to be OS-independent (Windows friendly)
# Replace all hardcoded /opt/wuchang/downloads/ paths with os.path.join(os.getcwd(), '...')

def replace_path(match):
    var_name = match.group(1)
    filename = match.group(2)
    return f"{var_name} = os.path.join(os.getcwd(), '{filename}')"

# Pattern to find: path = '/opt/wuchang/downloads/filename.ext'
pattern = r"(\w+)\s*=\s*'/opt/wuchang/downloads/([^']+)'"
new_content = re.sub(pattern, replace_path, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Updated main.py paths to be Windows compatible')
