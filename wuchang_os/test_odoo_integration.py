import sys
import os
import time

# Simulate Odoo environment paths
sys.path.append(r"C:\wuchang V5.1.0\wuchang_os\addons\wuchang_property_toolkits\models")

# Mock Odoo classes
class Model:
    _name = ''
    _description = ''
    _inherit = []
    def write(self, vals):
        print(f"[MOCK ODOO] Writing to DB: {vals}")

class fields:
    def Char(string='', required=False): return 'MockChar'
    def Text(string=''): return 'MockText'
    def Selection(selection, string='', default='', tracking=False): return 'MockSelection'
    def Many2one(comodel_name, string=''): return 'MockMany2one'

class api:
    pass

# Mock models module
class models:
    Model = Model

# Inject mocks into sys.modules
import types
odoo = types.ModuleType('odoo')
odoo.models = models
odoo.fields = fields
odoo.api = api
sys.modules['odoo'] = odoo

# Now import the actual file
# We need to make sure staps_delivery is found relative to the script location
# The script expects to be in .../models/
# So we will run this script from that directory or adjust the path in the script
# But the script uses __file__. Let's just run this mock script from the correct directory.

try:
    # Temporarily change dir to where the file is to ensure relative paths work
    target_dir = r"C:\wuchang V5.1.0\wuchang_os\addons\wuchang_property_toolkits\models"
    os.chdir(target_dir)
    
    # Import the module
    import property_maintenance
    
    print("\n[TEST] Instantiating PropertyMaintenance...")
    pm = property_maintenance.PropertyMaintenance()
    pm.name = "Test Maintenance Request"
    
    print("[TEST] Calling action_submit()...")
    pm.action_submit()
    
    print("[TEST] Success!")

except Exception as e:
    print(f"[TEST] Failed: {e}")
    import traceback
    traceback.print_exc()
