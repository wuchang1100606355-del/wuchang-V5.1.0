
import xmlrpc.client
import sys
import os

# Configuration
URL = 'http://localhost:8069'
DB = 'odoo'
USERNAME = 'admin'
PASSWORD = 'admin'

def main():
    print('--------------------------------------------------')
    print('Wuchang OS: Data Access Verification (Fixed)')
    print('--------------------------------------------------')
    print('Connecting to', URL, '...')

    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
        version = common.version()
        print('System Online. Version:', version.get('server_version'))

        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        if uid:
            print('Authentication Successful. UID:', uid)
            
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(URL))
            
            # Fetch Users
            print('\n[DATA] Fetching recent users...')
            users = models.execute_kw(DB, uid, PASSWORD, 'res.users', 'search_read', [[]], {'limit': 5, 'fields': ['name', 'login', 'email']})
            for u in users:
                print(' - {} ({})'.format(u['name'], u.get('login')))

            # Fetch Partners
            print('\n[DATA] Fetching partners...')
            partners = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'search_read', [[]], {'limit': 5, 'fields': ['name', 'email']})
            for p in partners:
                print(' - {} <{}>'.format(p['name'], p.get('email') or 'No Email'))

            print('\n--------------------------------------------------')
            print('Environment Verified. Data Access OK.')
            print('--------------------------------------------------')
            
        else:
            print('Authentication Failed. Please check credentials.')

    except Exception as e:
        print('Connection Error:', e)
        print('Ensure Docker container is running: docker ps')

if __name__ == '__main__':
    main()

