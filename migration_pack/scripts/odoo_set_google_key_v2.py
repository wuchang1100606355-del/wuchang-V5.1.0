import sys
import json
import odoo
from odoo import api, SUPERUSER_ID

def set_key(key_value):
    try:
        # 嘗試從設定檔獲取資料庫名稱，如果沒有則預設為 'admin'
        dbname = odoo.tools.config.get('db_name') or 'admin'
        
        # 建立 Registry 連線
        registry = odoo.registry(dbname)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # 設定參數
            env['ir.config_parameter'].sudo().set_param('google.api_key_gemini', key_value)
            
            # 驗證設定
            stored_key = env['ir.config_parameter'].sudo().get_param('google.api_key_gemini')
            
            if stored_key == key_value:
                print(json.dumps({'ok': True, 'message': 'Key set successfully', 'db': dbname}))
            else:
                print(json.dumps({'ok': False, 'error': 'Verification failed'}))
                
    except Exception as e:
        print(json.dumps({'ok': False, 'error': str(e)}))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_key(sys.argv[1])
    else:
        print(json.dumps({'ok': False, 'error': 'No key provided'}))
