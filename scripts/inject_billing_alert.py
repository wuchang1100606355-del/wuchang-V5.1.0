# -*- coding: utf-8 -*-
import sys
import xmlrpc.client

# Configuration
URL = "http://localhost:8069"
DB = "admin"
USER = "admin"
PASS = "admin"  # Default password, user might need to change if different

def inject_alert():
    print("Connecting to Odoo...")
    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
        uid = common.authenticate(DB, USER, PASS, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(URL))
        
        print("Connected. Updating system parameters...")
        
        # Set trial limits and usage
        # Usage: $35,257.26
        # Limit: $35,745.00
        
        models.execute_kw(DB, uid, PASS, 'ir.config_parameter', 'set_param', ['gcp.monthly_spend.trial', '35257.26'])
        models.execute_kw(DB, uid, PASS, 'ir.config_parameter', 'set_param', ['gcp.quota.trial.limit', '35745.00'])
        
        print("Parameters set. Refreshing quota records...")
        
        # Ensure default records exist (will create 'trial' record)
        models.execute_kw(DB, uid, PASS, 'wuchang.finance.quota', 'ensure_default_records', [])
        
        # Trigger refresh to load params into records
        quota_ids = models.execute_kw(DB, uid, PASS, 'wuchang.finance.quota', 'search', [[]])
        models.execute_kw(DB, uid, PASS, 'wuchang.finance.quota', 'action_refresh', [quota_ids])
        
        # Assign trial quota to Admin (uid)
        trial_ids = models.execute_kw(DB, uid, PASS, 'wuchang.finance.quota', 'search', [[['program', '=', 'trial']]])
        if trial_ids:
             models.execute_kw(DB, uid, PASS, 'wuchang.finance.quota', 'write', [trial_ids, {'assigned_user_id': uid}])
             print(f"Assigned Trial Quota to User ID: {uid}")

        print("Success! Quota updated.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inject_alert()
