import xmlrpc.client
import json
import time

class WuchangOdooAdapter:
    def __init__(self, url="http://localhost:8069", db="wuchang", username="admin", password="admin"):
        """
        Initialize Odoo Adapter.
        Default credentials are often admin/admin in dev environments.
        If config differs, they should be passed in.
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        self.common = None
        self.connected = False

    def connect(self):
        """Establish connection to Odoo."""
        try:
            print(f"🔌 Connecting to Odoo at {self.url}...")
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            
            if self.uid:
                print(f"✅ Odoo Authentication Successful! UID: {self.uid}")
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                self.connected = True
                return True
            else:
                print("❌ Odoo Authentication Failed.")
                return False
        except Exception as e:
            print(f"❌ Odoo Connection Error: {e}")
            return False

    def execute(self, model, method, *args, **kwargs):
        """Execute a method on an Odoo model."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            return self.models.execute_kw(self.db, self.uid, self.password, model, method, args, kwargs)
        except Exception as e:
            print(f"❌ Odoo Execution Error ({model}.{method}): {e}")
            return None

    def search_read(self, model, domain=None, fields=None, limit=10):
        """Search and read records."""
        domain = domain or []
        fields = fields or []
        return self.execute(model, 'search_read', domain, {'fields': fields, 'limit': limit})

    def create_record(self, model, values):
        """Create a new record."""
        return self.execute(model, 'create', [values])

    def update_record(self, model, record_id, values):
        """Update an existing record."""
        return self.execute(model, 'write', [[record_id], values])

    def log_system_event(self, title, description, level="info"):
        """Log a system event to Odoo (e.g., in a custom log model or discuss)."""
        # For now, let's try to post to 'mail.message' or a suitable place.
        # Or creating a Note.
        print(f"📝 Logging to Odoo: {title} - {description}")
        
        # Example: Create a note in 'note.note' if installed, or just log to stdout for now if model unsure.
        # Let's try 'mail.message' linked to a generic channel if possible, or just 'discuss.channel'.
        # Safer bet for "Software generating Software" context: Create a Task in a "System Evolution" project.
        
        # Check if 'project.project' exists for "Wuchang Evolution"
        project = self.search_read('project.project', [['name', '=', 'Wuchang Evolution']], ['id'])
        project_id = project[0]['id'] if project else None
        
        if not project_id:
            # Create Project if not exists (Auto-generation!)
            print("✨ Creating 'Wuchang Evolution' Project in Odoo...")
            project_id = self.create_record('project.project', {'name': 'Wuchang Evolution'})
        
        if project_id:
            self.create_record('project.task', {
                'project_id': project_id,
                'name': title,
                'description': description,
                'priority': '1' if level == 'high' else '0'
            })
            print("✅ Task created in Odoo.")

    def list_dbs(self):
        """List available databases."""
        try:
            db_proxy = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/db')
            return db_proxy.list()
        except Exception as e:
            print(f"❌ Failed to list databases: {e}")
            return []

if __name__ == "__main__":
    # Test connection
    adapter = WuchangOdooAdapter()
    dbs = adapter.list_dbs()
    print(f"📂 Available Databases: {dbs}")
    
    if dbs:
        adapter.db = dbs[0] # Try the first one
        print(f"🔄 Trying to connect to DB: {adapter.db}")
        adapter.connect()
