import python scripts/install_odoo_modules.py

xmlrpc.client
import time

url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

def install_modules():
    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("Authentication failed")
            return

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # Modules to install
        modules_to_install = [
            'website', 
            'point_of_sale', 
            'sale_management', 
            'stock', 
            'project', 
            'crm',
            'purchase',
            'account'
        ]

        print(f"Checking modules: {', '.join(modules_to_install)}")
        
        # Check which ones are already installed
        installed_modules = models.execute_kw(db, uid, password,
            'ir.module.module', 'search_read',
            [[['name', 'in', modules_to_install], ['state', '=', 'installed']]],
            {'fields': ['name']}
        )
        installed_names = [m['name'] for m in installed_modules]
        print(f"Already installed: {installed_names}")

        to_install = [m for m in modules_to_install if m not in installed_names]
        
        if not to_install:
            print("All core modules are already installed!")
            return

        print(f"Installing missing modules: {to_install}")
        
        # Find module IDs to install
        module_ids = models.execute_kw(db, uid, password,
            'ir.module.module', 'search',
            [[['name', 'in', to_install]]]
        )
        
        if module_ids:
            # Install immediately
            models.execute_kw(db, uid, password,
                'ir.module.module', 'button_immediate_install',
                [module_ids]
            )
            print("Installation triggered. Odoo might restart.")
        else:
            print("Could not find some modules to install.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    install_modules()
