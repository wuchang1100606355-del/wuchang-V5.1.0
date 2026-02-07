import xmlrpc.client
import sys

URL = 'http://localhost:8069'
DB_PRIMARY = 'odoo'
USERNAME = 'admin@wuchang.life'
PASSWORD = 'poiuY92926'

USERNAME_FALLBACK = 'admin'
PASSWORD_FALLBACK = 'admin'

def connect():
    print(f"DEBUG: Connecting to XMLRPC common at {URL}/xmlrpc/2/common")
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        print("DEBUG: ServerProxy created. Authenticating...")
    except Exception as e:
        print(f"ERROR: ServerProxy creation failed: {e}")
        return None, None, None

    try:
        print(f"DEBUG: Attempting auth with {DB_PRIMARY} / {USERNAME}")
        uid = common.authenticate(DB_PRIMARY, USERNAME, PASSWORD, {})
        print(f"DEBUG: Auth result: {uid}")
        if uid: return DB_PRIMARY, uid, PASSWORD
    except Exception as e:
        print(f"ERROR: Auth 1 failed: {e}")
    
    try:
        print(f"DEBUG: Attempting auth with {DB_PRIMARY} / {USERNAME_FALLBACK}")
        uid = common.authenticate(DB_PRIMARY, USERNAME_FALLBACK, PASSWORD_FALLBACK, {})
        print(f"DEBUG: Auth result: {uid}")
        if uid: return DB_PRIMARY, uid, PASSWORD_FALLBACK
    except Exception as e:
        print(f"ERROR: Auth 2 failed: {e}")
    
    return None, None, None

def register_vendor(email):
    print(f"Connecting to Odoo at {URL}...")
    db, uid, password = connect()
    if not uid:
        print("Could not connect to Odoo (Auth failed)")
        return

    print(f"Connected to DB: {db}, UID: {uid}")
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    print(f"Searching for partner {email}...")
    try:
        existing = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['email', '=', email]]], {'fields': ['id', 'name']})
        
        if existing:
            pid = existing[0]['id']
            print(f"Partner exists: {existing[0]['name']} (ID: {pid}). Updating to Vendor (supplier_rank=1)...")
            models.execute_kw(db, uid, password, 'res.partner', 'write', [[pid], {'supplier_rank': 1}])
            print("Update complete.")
        else:
            print(f"Creating new Vendor partner for {email}...")
            pid = models.execute_kw(db, uid, password, 'res.partner', 'create', [{'name': email, 'email': email, 'supplier_rank': 1}])
            print(f"Created Partner ID: {pid}")
    except Exception as e:
        print(f"ERROR during execution: {e}")

if __name__ == '__main__':
    register_vendor('wuchang1100606355@gmail.com')
