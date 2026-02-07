import json
try:
    import odoo
    from odoo import api, SUPERUSER_ID

    dbname = odoo.tools.config.get('db_name')
    registry = odoo.registry(dbname)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        p = env['ir.config_parameter'].sudo()

        # Required for cloud fallback
        p.set_param('wuchang.cloud_approved', 'true')

        # Project and location for Vertex AI
        # Replace with your actual project/location later if needed
        p.set_param('wuchang.google.project_id', 'my-j-483304')
        p.set_param('wuchang.google.location', 'us-central1')

        # Keep default local-first, but set a sensible cloud model
        if not (p.get_param('wuchang.ai_mode') or '').strip():
            p.set_param('wuchang.ai_mode', 'local_ollama')
        p.set_param('wuchang.gen_model', 'gemini-1.5-flash')

        out = {
            'ok': True,
            'cloud_approved': True,
            'project_id': p.get_param('wuchang.google.project_id'),
            'location': p.get_param('wuchang.google.location'),
            'ai_mode': p.get_param('wuchang.ai_mode'),
            'gen_model': p.get_param('wuchang.gen_model'),
        }
        print(json.dumps(out))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
