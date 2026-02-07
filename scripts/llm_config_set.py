import os
try:
    from odoo import api, SUPERUSER_ID
    import odoo
except Exception:
    odoo = None
    api = None
    SUPERUSER_ID = 1

AI_MODE = os.environ.get('AI_MODE') or 'external_key'
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or ''
GEN_MODEL = os.environ.get('GEN_MODEL') or 'gemini-1.5-flash'
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL') or ''

if not odoo or not api:
    print('ERROR: Odoo shell environment not available')
else:
    try:
        # Prefer configured db_name; fallback to env vars
        db_name = None
        try:
            db_name = odoo.tools.config.get('db_name')
        except Exception:
            db_name = None
        if not db_name:
            db_name = os.environ.get('POSTGRES_DB') or os.environ.get('DB_NAME') or 'odoo'
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            p = env['ir.config_parameter'].sudo()
            if AI_MODE:
                p.set_param('wuchang.ai_mode', AI_MODE)
            if GEN_MODEL:
                p.set_param('wuchang.gen_model', GEN_MODEL)
            if GOOGLE_API_KEY:
                p.set_param('wuchang.google_api_key', GOOGLE_API_KEY)
            if OLLAMA_MODEL:
                p.set_param('wuchang.ollama_model', OLLAMA_MODEL)
            print('OK: llm_config_set', {'ai_mode': AI_MODE, 'gen_model': GEN_MODEL, 'key_set': bool(GOOGLE_API_KEY)})
    except Exception as e:
        print('ERROR:', str(e))
