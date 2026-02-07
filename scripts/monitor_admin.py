import time
import xmlrpc.client
import sys

URL = "http://localhost:8069"
USER = "admin"
PASS = "odoo"
DBS = ["wuchang", "odoo", "postgres", "odoo17", "wuchang_v5"]

def connect(db_name):
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(db_name, USER, PASS, {})
        if uid:
            return common, uid, db_name
    except Exception as e:
        # print(f"Connection error to {db_name}: {e}")
        pass
    return None, None, None

def monitor():
    print("Little J is initializing system connection...")
    common = None
    uid = None
    db_name = None

    for db in DBS:
        print(f"Trying to connect to DB: {db}...")
        c, u, n = connect(db)
        if c:
            common, uid, db_name = c, u, n
            print(f"Connected to DB: {db_name} with UID: {uid}")
            break
    
    if not uid:
        print("Could not connect to any known Odoo database with admin/odoo.")
        # Try to list dbs
        try:
             db_list = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/db").list()
             print(f"Available DBs found: {db_list}")
             for db in db_list:
                 c, u, n = connect(db)
                 if c:
                     common, uid, db_name = c, u, n
                     print(f"Connected to DB: {db_name} with UID: {uid}")
                     break
        except Exception as e:
             print(f"Could not list databases: {e}")
    
    if not uid:
        print("Failed to authenticate. Please check Odoo status.")
        return

    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    print("Little J is standing by in Odoo system... Monitoring Admin login.")
    
    # Get initial state
    last_login = ""
    try:
        user = models.execute_kw(db_name, uid, PASS, 'res.users', 'read', [[uid], ['login_date', 'email', 'phone', 'mobile']])
        if user:
            last_login = user[0].get('login_date') or ""
            print(f"Current Admin Login Date: {last_login}")
    except Exception as e:
        print(f"Error reading user data: {e}")
        return

    while True:
        try:
            user = models.execute_kw(db_name, uid, PASS, 'res.users', 'read', [[uid], ['login_date', 'email', 'phone', 'mobile']])
            if user:
                current_login = user[0].get('login_date') or ""
                
                if current_login != last_login:
                    print(f"\n[ALERT] Admin Logged In detected at {current_login}!")
                    print("Initiating Contact Acquisition...")
                    print(f"Contact Info: Email={user[0].get('email')}, Phone={user[0].get('phone')}, Mobile={user[0].get('mobile')}")
                    last_login = current_login
            
            time.sleep(2)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor()
