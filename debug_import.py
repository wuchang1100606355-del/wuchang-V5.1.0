
import sys
import logging
import os

# Add addons path
sys.path.append('/var/lib/odoo/.local/share/Odoo/addons/17.0')
sys.path.append('/mnt/extra-addons') # Assuming where wuchang_core is mounted

logging.basicConfig(level=logging.INFO)

try:
    print('Attempting to import wuchang_core...')
    # Mock odoo import mechanism if needed, or just import as package if in path
    # But inside Odoo container, we should use odoo.addons
    import odoo.addons.wuchang_core
    print('Import successful!')
except ImportError as e:
    print(f'ImportError: {e}')
except Exception as e:
    print(f'Exception: {e}')
    import traceback
    traceback.print_exc()

