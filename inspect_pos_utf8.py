import odoo
from odoo import api, SUPERUSER_ID
import logging
import sys

# Mute logging to keep output clean
logging.getLogger('odoo').setLevel(logging.WARNING)

try:
    # Initialize Odoo
    odoo.tools.config.parse_config([])
    registry = odoo.registry(odoo.tools.config['db_name'] or 'admin')
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        print(f'Connected to Database: {cr.dbname}')
        
        # Check POS Module Status
        module_pos = env['ir.module.module'].search([('name', '=', 'point_of_sale')])
        print(f'POS Module State: {module_pos.state if module_pos else "Not Found"}')
        
        if module_pos and module_pos.state == 'installed':
            # Search for relevant POS Configs
            # Using 'ilike' for case-insensitive partial match
            # Search for '重新' (Chongsin) or 'Coffee' or 'Shop'
            target_pos = env['pos.config'].search(['|', '|', ('name', 'ilike', '重新'), ('name', 'ilike', 'Coffee'), ('name', 'ilike', 'Shop')])
            
            if target_pos:
                print(f'\nFound {len(target_pos)} Relevant POS Configs:')
                for pos in target_pos:
                    print(f'\n[POS Config ID: {pos.id}]')
                    print(f'  Name: {pos.name}')
                    print(f'  Active: {pos.active}')
                    print(f'  Receipt Header: {pos.receipt_header or "None"}')
                    print(f'  Receipt Footer: {pos.receipt_footer or "None"}')
                    # Check payment methods if possible
                    pms = pos.payment_method_ids
                    pm_names = [pm.name for pm in pms]
                    print(f'  Payment Methods: {", ".join(pm_names)}')
            else:
                print('\nNo POS configs found matching "重新", "Coffee", or "Shop".')
                
                # List ALL POS configs just in case
                all_pos = env['pos.config'].search([])
                if all_pos:
                    print(f'\nListing ALL {len(all_pos)} POS Configs:')
                    for pos in all_pos:
                        print(f'  - {pos.name} (ID: {pos.id}, Active: {pos.active})')
                else:
                    print('  No POS configurations exist yet.')
        else:
            print('POS Module is not installed. Please install "point_of_sale" first.')

except Exception as e:
    print(f'Error executing script: {e}')