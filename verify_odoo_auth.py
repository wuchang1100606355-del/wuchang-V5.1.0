import xmlrpc.client
url = 'http://localhost:8069'
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
dbs = ['wuchang', 'odoo', 'odoo_db', 'admin', 'db']
username = 'odoo'
password = 'odoo'

for db in dbs:
    try:
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f'SUCCESS: Authenticated on DB: {db} with UID: {uid}')
        else:
            print(f'FAILED: Could not authenticate on DB: {db}')
    except Exception as e:
        print(f'ERROR on DB {db}: {e}')
