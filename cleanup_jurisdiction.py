import logging
from odoo import api, SUPERUSER_ID

def run_cleanup(env):
    jurisdiction_keywords = ['五順', '五常', '仁忠']
    keep_ids = [env.ref('base.main_partner').id]
    
    partners = env['res.partner'].search([('id', 'not in', keep_ids)])
    
    deleted_count = 0
    archived_count = 0
    
    print(f'Starting cleanup for {len(partners)} partners...')
    
    for p in partners:
        address = str(p.street or '') + str(p.city or '') + str(p.state_id.name or '')
        is_jurisdiction = any(k in address for k in jurisdiction_keywords)
        
        if is_jurisdiction:
            continue
            
        if p.user_ids:
            continue
            
        p_name = p.name
        try:
            with env.cr.savepoint():
                p.unlink()
                deleted_count += 1
        except Exception as e:
            try:
                with env.cr.savepoint():
                    if p.active:
                        p.write({'active': False})
                        archived_count += 1
            except Exception as e2:
                print(f"Failed to handle {p_name}: {e2}")

    print(f'Cleanup Result: Deleted {deleted_count}, Archived {archived_count}')
    env.cr.commit()

print('--- CLEANUP START ---')
try:
    run_cleanup(env)
except Exception as e:
    print(f'Cleanup failed: {e}')
print('--- CLEANUP END ---')
