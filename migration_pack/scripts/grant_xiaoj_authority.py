import json
import os
import odoo
from odoo import api, SUPERUSER_ID

# Configure Odoo connection
odoo.tools.config['db_host'] = 'db'
odoo.tools.config['db_user'] = 'odoo'
odoo.tools.config['db_password'] = 'odoo'
odoo.tools.config['db_port'] = 5432

def _choose_db_name(odoo):
    try:
        db = odoo.tools.config.get('db_name')
        if isinstance(db, str) and db.strip():
            return db.strip()
    except Exception:
        pass
    return os.environ.get('POSTGRES_DB') or os.environ.get('DB_NAME') or 'admin'

try:
    db_name = _choose_db_name(odoo)
    reg = odoo.registry(db_name)
    with reg.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        p = env['ir.config_parameter'].sudo()
        
        # Grant Xiao J Highest Authority
        p.set_param('founder.management_disabled', 'true') # Enable Xiao J Caretaker Mode
        p.set_param('supreme.override.enabled', 'true')    # Enable Supreme Override
        p.set_param('wuchang.ai.global_suppression', '')   # Disable Suppression (Empty string is False)
        
        # Ensure Agent Identity
        p.set_param('wuchang.agent.enabled', 'True')
        p.set_param('wuchang.agent.name', '小j')
        
        # Log the action
        print(json.dumps({
            'ok': True,
            'action': 'grant_xiaoj_authority',
            'founder.management_disabled': p.get_param('founder.management_disabled'),
            'supreme.override.enabled': p.get_param('supreme.override.enabled'),
            'wuchang.ai.global_suppression': p.get_param('wuchang.ai.global_suppression'),
            'agent_name': p.get_param('wuchang.agent.name')
        }))
        
        # Create/Update Agent Partner
        try:
            agent_email = p.get_param('wuchang.agent.email') or 'admin@wuchang.life'
            Partner = env['res.partner'].sudo()
            qp = Partner.search([('email', '=', agent_email)], limit=1)
            vals = {'name': '小j', 'email': agent_email}
            if qp:
                qp.write(vals)
            else:
                Partner.create(vals)
        except Exception as e:
            print(f"Warning: Could not update partner: {e}")

except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
