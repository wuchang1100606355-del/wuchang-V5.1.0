import os
import re

# List of files to check and fix
files_to_fix = [
    r'wuchang_os\addons\wuchang_core\controllers\main.py',
    r'wuchang_os\addons\wuchang_core\models\jf_gateway.py',
    r'wuchang_os\addons\wuchang_core\scripts\knowledge_sync_agent.py',
    r'wuchang_os\addons\wuchang_design_system\controllers\web_login_home.py',
    r'wuchang_os\addons\wuchang_design_system\controllers\web_login.py',
    r'wuchang_os\addons\wuchang_property_toolkits\controllers\property_site.py'
]

# Pattern to find: path = '/opt/wuchang/downloads/...' or similar
# We want to catch single quotes around /opt/wuchang...
pattern = r"'/opt/wuchang/([^']+)'"

def replace_path(match):
    relative_path = match.group(1)
    # Convert forward slashes to OS separator if needed, though python handles / well on windows mostly, 
    # but os.path.join is safest.
    # We replace the entire string literal '/opt/wuchang/...' with an os.path.join call
    # Note: We need to ensure 'os' is imported in the file.
    
    # Simple strategy: replace '/opt/wuchang/downloads/foo.json' with os.path.join(os.getcwd(), 'foo.json')
    # But wait, structure might be different. 
    # Let's assume we map /opt/wuchang/downloads/ -> os.getcwd() for now as per previous fix.
    
    if relative_path.startswith('downloads/'):
        filename = relative_path.replace('downloads/', '')
        return f"os.path.join(os.getcwd(), '{filename}')"
    else:
        # Fallback for other paths under /opt/wuchang
        return f"os.path.join(os.getcwd(), '{relative_path}')"

for file_path in files_to_fix:
    full_path = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(full_path):
        print(f"Skipping {file_path} (not found)")
        continue
        
    print(f"Processing {file_path}...")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if os is imported
    if 'import os' not in content:
        content = 'import os\n' + content
        
    new_content = re.sub(pattern, replace_path, content)
    
    if content != new_content:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Fixed paths in {file_path}")
    else:
        print(f"  No changes needed for {file_path}")

print('Global path fix complete.')
