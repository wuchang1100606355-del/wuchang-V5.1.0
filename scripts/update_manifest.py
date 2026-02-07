import os

path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\__manifest__.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'data/sync_balance_action.xml' not in content:
    target = "'data/pos_setup.xml',"
    new_line = "\n        'data/sync_balance_action.xml',"
    
    if target in content:
        content = content.replace(target, target + new_line)
    else:
        # Fallback to finding the start of the data list
        content = content.replace("'data': [", "'data': [" + new_line)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Manifest updated.")
else:
    print("Manifest already contains sync_balance_action.xml")
