import logging
import sys

# Setup logging to stdout
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger('wuchang_setup')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

print('Starting Wuchang Shop Configuration...')

if 'env' not in locals():
    print('Error: env not found. Run this script via odoo shell.')
    sys.exit(1)

# 1. Company Setup
try:
    company = env.ref('base.main_company')
    company.write({
        'name': 'Wuchang Community Digital System',
        'street': 'No. 123, Wuchang St.',
        'email': 'info@wuchang.life',
        'phone': '+886 975 734 69',
        'website': 'https://wuchang.life',
    })
    print('Company info updated: Wuchang Community Digital System')
except Exception as e:
    print(f'Error updating company: {e}')

# 2. Google Workspace / General Settings
try:
    param = env['ir.config_parameter'].sudo()
    param.set_param('mail.catchall.domain', 'wuchang.life')
    print('System parameter mail.catchall.domain set to wuchang.life')
except Exception as e:
    print(f'Error updating settings: {e}')

# 3. Update Admin Credentials
try:
    admin_user = env.ref('base.user_admin')
    # Update regardless of current state to ensure it matches request
    admin_user.write({
        'login': 'admin@wuchang.life',
        'password': 'poiuY92926',
        'email': 'admin@wuchang.life',
        'name': 'Wuchang Admin'
    })
    print('Admin user updated to admin@wuchang.life')
except Exception as e:
    print(f'Error updating admin user: {e}')

env.cr.commit()
print('Configuration committed successfully.')



