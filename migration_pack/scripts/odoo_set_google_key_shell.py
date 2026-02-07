import json, os
# This script runs inside "odoo shell" where `env` is available.
try:
    key = os.environ.get('GOOGLE_API_KEY', '')
    env['ir.config_parameter'].sudo().set_param('wuchang.google_api_key', key)
    print(json.dumps({'ok': True}))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
