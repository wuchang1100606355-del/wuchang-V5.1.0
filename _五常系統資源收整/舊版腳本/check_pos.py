import odoo
from odoo import api, SUPERUSER_ID
import logging
logging.getLogger('odoo').setLevel(logging.WARNING)
try:
    odoo.tools.config.parse_config([])
    registry = odoo.registry(odoo.tools.config['db_name'] or 'admin')
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        print(f'DB: {cr.dbname}')
        pos_configs = env['pos.config'].search([])
        print(f'Total POS: {len(pos_configs)}')
        for p in pos_configs:
            print(f'POS: {p.name} (ID: {p.id})')
            if '重新' in p.name or 'Coffee' in p.name:
                print(f' -> FOUND TARGET: {p.name}')
                print(f'    Receipt Header: {p.receipt_header}')
                print(f'    Receipt Footer: {p.receipt_footer}')
except Exception as e:
    print(f'Error: {e}')

