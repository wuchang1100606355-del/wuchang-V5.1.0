import xmlrpc.client
import sys
import time

URL = 'http://localhost:8069'
DB_PRIMARY = 'odoo'
DB_FALLBACK = 'admin'

USERNAME = 'admin@wuchang.life'
PASSWORD = 'poiuY92926'

USERNAME_FALLBACK = 'admin'
PASSWORD_FALLBACK = 'admin'

def connect():
    print(f'Connecting to {URL}...')
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    
    # Try Primary DB / Primary Creds
    try:
        print(f'Attempting DB: {DB_PRIMARY}, User: {USERNAME}')
        uid = common.authenticate(DB_PRIMARY, USERNAME, PASSWORD, {})
        if uid:
            print(f'[SUCCESS] Connected to {DB_PRIMARY} as {USERNAME} (UID: {uid})')
            return DB_PRIMARY, uid, PASSWORD
    except Exception as e:
        print(f'[FAIL] {DB_PRIMARY}/{USERNAME}: {e}')

    # Try Primary DB / Fallback Creds
    try:
        print(f'Attempting DB: {DB_PRIMARY}, User: {USERNAME_FALLBACK}')
        uid = common.authenticate(DB_PRIMARY, USERNAME_FALLBACK, PASSWORD_FALLBACK, {})
        if uid:
            print(f'[SUCCESS] Connected to {DB_PRIMARY} as {USERNAME_FALLBACK} (UID: {uid})')
            return DB_PRIMARY, uid, PASSWORD_FALLBACK
    except Exception as e:
        print(f'[FAIL] {DB_PRIMARY}/{USERNAME_FALLBACK}: {e}')

    # Try Fallback DB / Fallback Creds
    try:
        print(f'Attempting DB: {DB_FALLBACK}, User: {USERNAME_FALLBACK}')
        uid = common.authenticate(DB_FALLBACK, USERNAME_FALLBACK, PASSWORD_FALLBACK, {})
        if uid:
            print(f'[SUCCESS] Connected to {DB_FALLBACK} as {USERNAME_FALLBACK} (UID: {uid})')
            return DB_FALLBACK, uid, PASSWORD_FALLBACK
    except Exception as e:
        print(f'[FAIL] {DB_FALLBACK}/{USERNAME_FALLBACK}: {e}')

    return None, None, None

def fix_odoo():
    db, uid, password = connect()
    if not uid:
        print('[ERROR] Could not connect to Odoo. Please check if Docker is running.')
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

    # 1. Update Module List
    print('\n[STEP 1] Updating module list...')
    try:
        # Correct call for update_list (it's a model method, no ids needed usually, but via RPC might need list of ids [])
        # If it fails, we ignore it as we likely have the module in the list already
        models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])
        print('[OK] Module list updated.')
    except Exception as e:
        print(f'[WARNING] Failed to update module list (might not be needed): {e}')

    # 2. Install Dependencies
    deps = ['base', 'web', 'mail', 'mail_bot', 'website', 'point_of_sale', 'sale', 'crm', 'project', 'stock']
    print('\n[STEP 2] Checking dependencies...')
    for dep in deps:
        try:
            state = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', [[['name', '=', dep]]], {'fields': ['state', 'name']})
            if not state:
                print(f'[WARNING] Dependency {dep} not found in module list.')
                continue
            
            if state[0]['state'] != 'installed':
                print(f'Installing {dep}...')
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [state[0]['id']])
                print(f'[OK] {dep} installed.')
            else:
                print(f'[OK] {dep} is already installed.')
        except Exception as e:
            print(f'[ERROR] Failed handling {dep}: {e}')

    # 3. Upgrade/Install wuchang_core
    print('\n[STEP 3] Upgrading wuchang_core...')
    try:
        module = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', [[['name', '=', 'wuchang_core']]], {'fields': ['state', 'id']})
        if module:
            mod_id = module[0]['id']
            state = module[0]['state']
            print(f'Found wuchang_core (ID: {mod_id}, State: {state}).')
            
            if state == 'uninstalled':
                print('Installing wuchang_core...')
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [mod_id])
                print('[OK] Install command sent (server might restart).')
            else:
                print('Upgrading wuchang_core...')
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade', [mod_id])
                print('[OK] Upgrade command sent (server might restart).')
        else:
            print('[ERROR] wuchang_core module NOT FOUND in Odoo list. Check mount paths.')
    except Exception as e:
        # Connection might be closed due to restart, which is expected
        print(f'[INFO] Operation triggered (Connection might have closed): {e}')

    # 4. Verify Field
    print('\n[STEP 4] Verifying merchant_donation_total field...')
    time.sleep(10) # Wait for restart
    
    # Reconnect if needed
    try:
        db, uid, password = connect() # Re-auth
        if uid:
            fields = models.execute_kw(db, uid, password, 'community.fund.account', 'fields_get', [], {'attributes': ['string', 'type']})
            if 'merchant_donation_total' in fields:
                print('[SUCCESS] Field merchant_donation_total FOUND in community.fund.account!')
            else:
                print('[FAILURE] Field merchant_donation_total NOT FOUND.')
                print('Available fields:', list(fields.keys()))
        else:
            print('[WARNING] Could not reconnect to verify.')
    except Exception as e:
        print(f'[WARNING] Verification failed (Server might still be restarting): {e}')

if __name__ == '__main__':
    fix_odoo()
