import xmlrpc.client
import sys

url = 'http://localhost:8069'
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')

creds = [
    ('wuchang', 'admin', 'admin'),
    ('wuchang', 'admin', 'odoo'),
    ('odoo', 'admin', 'admin'),
    ('odoo', 'admin', 'odoo'),
]

print(f'Testing connection to {url}...')

for db, user, pwd in creds:
    try:
        uid = common.authenticate(db, user, pwd, {})
        if uid:
            print(f'SUCCESS: DB={db}, User={user}, Pass={pwd} -> UID={uid}')
            try:
                models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
                has_account = models.execute_kw(db, uid, pwd, 'ir.module.module', 'search_count', [[['name', '=', 'account'], ['state', '=', 'installed']]])
                print(f'  - Account Module Installed: {has_account}')
            except Exception as e2:
                print(f'  - Check failed: {e2}')
        else:
            print(f'FAILED: DB={db}, User={user}, Pass={pwd}')
    except Exception as e:
        print(f'ERROR: DB={db} -> {e}')
