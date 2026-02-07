import os
import sys

CORE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'vm_fastapi_main_new.py')
STAPS_CODE = r"""
# [STAPS INTEGRATION]
import sys
import os
staps_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wuchang_os', 'staps_delivery')
if staps_path not in sys.path:
    sys.path.append(staps_path)
try:
    from staps_kernel_service import StapsKernelService
    STAPS_SYSTEM = StapsKernelService()
    print('[STAPS] Kernel Integrated & Loaded Successfully.')
except ImportError as e:
    print(f'[STAPS] WARNING: Failed to load STAPS Kernel: {e}')
    STAPS_SYSTEM = None
"""

try:
    print(f"Patching {CORE_FILE}...")
    with open(CORE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'STAPS_SYSTEM =' not in content:
        if 'from fastapi import FastAPI' in content:
            new_content = content.replace('from fastapi import FastAPI', STAPS_CODE + '\nfrom fastapi import FastAPI')
            with open(CORE_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('Successfully patched STAPS integration.')
        else:
            print('Could not find insertion point')
    else:
        print('STAPS integration already present.')

except Exception as e:
    print(f'Error patching file: {e}')
