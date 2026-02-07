import json
try:
    import odoo
    from odoo import api, SUPERUSER_ID
    dbname = odoo.tools.config.get('db_name')
    registry = odoo.registry(dbname)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        p = env['ir.config_parameter'].sudo()
        p.set_param('wuchang.ai_mode', 'external_key')
        p.set_param('wuchang.gen_model', 'gemini-1.5-flash')
        p.set_param('wuchang.org.policy_ready', '1')
        out = {
            'ok': True,
            'ai_mode': 'external_key',
            'gen_model': 'gemini-1.5-flash',
            'policy_ready': True
        }
        print(json.dumps(out))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
