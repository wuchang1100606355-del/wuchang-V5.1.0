import csv
import os
import odoo
from odoo import api, SUPERUSER_ID

LEDGER_PATH = r'c:\wuchang V5.1.0\migration_pack\renyi_construction_ledger.csv'

def run():
    try:
        # Initialize Odoo
        config_file = os.environ.get('ODOO_RC') or 'c:\\wuchang V5.1.0\\wuchang_os\\odoo.conf'
        odoo.tools.config.parse_config(['-c', config_file])
        db_name = odoo.tools.config['db_name'] or 'wuchang'
        registry = odoo.registry(db_name)
        
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Find Renyi Store
            renyi_config = env['pos.config'].search([('name', 'ilike', '仁義')], limit=1)
            if not renyi_config:
                print('Error: Renyi Store not found.')
                return
            
            print(f'Target Store: {renyi_config.name}')
            Expense = env['wuchang.pos.expense']

            if not os.path.exists(LEDGER_PATH):
                print(f'Ledger file not found: {LEDGER_PATH}')
                return

            with open(LEDGER_PATH, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                count_updated = 0
                count_new = 0
                
                for row in reader:
                    reason = row.get('reason', '').strip()
                    amount_str = row.get('amount', '0').strip()
                    date_str = row.get('date', '').strip()
                    note = row.get('note', '').strip()
                    
                    if not reason or not amount_str:
                        continue
                        
                    try:
                        amount = float(amount_str)
                    except ValueError:
                        print(f'Invalid amount for {reason}: {amount_str}')
                        continue
                        
                    # Find existing record to update
                    domain = [
                        ('reason', '=', reason),
                        ('amount', '=', amount),
                        ('pos_config_id', '=', renyi_config.id)
                    ]
                    
                    existing = Expense.search(domain, limit=1)
                    
                    if existing:
                        existing.write({'note': note})
                        print(f'Updated Note for: {reason}')
                        count_updated += 1
                    else:
                        vals = {
                            'reason': reason,
                            'amount': amount,
                            'pos_config_id': renyi_config.id,
                            'note': note,
                        }
                        if date_str:
                            vals['date'] = date_str
                            
                        Expense.create(vals)
                        print(f'Created New: {reason}')
                        count_new += 1
            
            env.cr.commit()
            print(f'Process Complete. Updated: {count_updated}, New: {count_new}')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run()
