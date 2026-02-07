import xmlrpc.client
url = 'http://localhost:8069'
try:
    db = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/db')
    print(f'Available Databases: {db.list()}')
except Exception as e:
    print(f'Error listing DBs: {e}')
