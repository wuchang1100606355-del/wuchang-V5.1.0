from odoo import api, SUPERUSER_ID
import odoo
import sys

def run():
    try:
        registry = odoo.registry(odoo.tools.config['db_name'])
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            Expense = env['wuchang.pos.expense']
            # List existing expenses
            expenses = Expense.search([], limit=5)
            for e in expenses:
                print(f"Store: {e.pos_config_id.name}, Reason: {e.reason}, Amount: {e.amount}, Date: {e.date}")
    except Exception as e:
        print(e)

if __name__ == '__main__':
    run()
