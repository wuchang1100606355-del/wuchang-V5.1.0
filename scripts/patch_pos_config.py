import sys
import os
import odoo
from odoo import api, SUPERUSER_ID

def run():
    try:
        # Initialize Odoo
        config_file = os.environ.get('ODOO_RC') or 'c:\\wuchang V5.1.0\\wuchang_os\\odoo.conf'
        odoo.tools.config.parse_config(['-c', config_file])
        db_name = odoo.tools.config['db_name'] or 'wuchang'
        registry = odoo.registry(db_name)
        
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # 1. Find Renyi Store
            renyi_config = env['pos.config'].search([('name', 'ilike', '仁義')], limit=1)
            if not renyi_config:
                print('Error: Renyi Store not found.')
                return

            print(f'Found Store: {renyi_config.name}')

            # 2. Prepare Data
            # Note: User mentioned 'Booking date is today', 'Occurrence date is May 1st'
            # We set 'date' to May 1st. 'create_date' is automatic.
            
            items = [
                {
                    'reason': '協會直營社區產業聊國咖啡館仁義分店拆除舊裝潢及廢棄物處理',
                    'amount': 65000.0,
                    'date': '2025-05-01 09:00:00',
                    'pos_config_id': renyi_config.id,
                    'note': '對應科目：捐款收入-聊國咖啡館重新總店'
                },
                {
                    'reason': '木工',
                    'amount': 180000.0,
                    'date': '2025-05-01 09:00:00',
                    'pos_config_id': renyi_config.id,
                    'note': '對應科目：捐款收入-聊國咖啡館重新總店'
                }
            ]
            
            # 3. Create Records
            Expense = env['wuchang.pos.expense']
            for item in items:
                # Check if already exists to prevent dupes (optional but good)
                existing = Expense.search([
                    ('reason', '=', item['reason']),
                    ('amount', '=', item['amount']),
                    ('pos_config_id', '=', item['pos_config_id'])
                ], limit=1)
                
                if existing:
                    print(f'Skipping existing: {item["reason"]}')
                else:
                    rec = Expense.create(item)
                    print(f'Created: {rec.name} - {rec.reason} ()')
            
            # Commit
            env.cr.commit()
            print('Expenses committed successfully.')

    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    run()
