import json, os
try:
    import odoo
    from odoo import api, SUPERUSER_ID
    dbname = odoo.tools.config.get('db_name')
    registry = odoo.registry(dbname)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        key = os.environ.get('GOOGLE_API_KEY', '')
        env['ir.config_parameter'].sudo().set_param('wuchang.google_api_key', key)
        print(json.dumps({'ok': True}))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
