import xmlrpc.client
import sys

url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

try:
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print('Authentication failed')
        sys.exit(1)

    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    # Check for 'account' module (Billing/Accounting)
    modules = models.execute_kw(db, uid, password,
        'ir.module.module', 'search_read',
        [[['name', '=', 'account'], ['state', '=', 'installed']]],
        {'fields': ['name', 'state', 'shortdesc']})

    if modules:
        m = modules[0]
        print(f'Billing/Accounting module found: {m['shortdesc']} ({m['name']}) is {m['state']}')
    else:
        print('Billing/Accounting module (account) is NOT installed or NOT found.')

except Exception as e:
    print(f'Error: {e}')
