
import odoo
from odoo import api, SUPERUSER_ID

def record_memories(env):
    Memory = env['wuchang.ai.memory']
    
    memories = [
        {
            'name': '開啟時光拓展',
            'content': '系統已開啟時光拓展模式，建立專屬資料夾與備份。'
        },
        {
            'name': '已建立回滾點',
            'content': '系統已建立回滾點，包含 wuchang_core 與 時光拓展_Core_Sister 的備份。'
        }
    ]
    
    for mem in memories:
        existing = Memory.search([('name', '=', mem['name'])], limit=1)
        if not existing:
            Memory.create(mem)
            print('Created memory: ' + mem['name'])
        else:
            print('Memory exists: ' + mem['name'])
    
    env.cr.commit()

if __name__ == '__main__':
    try:
        registry = odoo.registry('wuchang')
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            record_memories(env)
    except Exception as e:
        print('Error: ' + str(e))

