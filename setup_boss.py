import logging
import sys

# Setup logging
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger('wuchang_setup')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

print('Starting Boss User Setup...')

if 'env' not in locals():
    print('Error: env not found.')
    sys.exit(1)

try:
    # 1. Update Company Name
    company = env.ref('base.main_company')
    company.write({'name': 'Loge Coffee (重新店)'})
    print('Company updated to Loge Coffee (重新店)')

    # 2. Create/Update Boss User
    User = env['res.users']
    existing = User.search([('login', '=', 'boss@coffee.com')])
    
    vals = {
        'name': '重新店負責人',
        'login': 'boss@coffee.com',
        'password': 'poiuY92926',
        'email': 'boss@coffee.com',
        'active': True,
        'company_id': company.id,
        'company_ids': [(4, company.id)],
    }
    
    groups_to_add = ['base.group_user', 'base.group_system']
    
    # Optional groups (if apps installed)
    optional_groups = [
        'sales_team.group_sale_manager',
        'point_of_sale.group_pos_manager',
        'stock.group_stock_manager',
        'account.group_account_manager',
    ]
    
    group_ids = []
    for xml_id in groups_to_add:
        try:
            g = env.ref(xml_id)
            group_ids.append(g.id)
        except:
            print(f'Warning: Group {xml_id} not found.')
        
    for xml_id in optional_groups:
        try:
            g = env.ref(xml_id, raise_if_not_found=False)
            if g:
                group_ids.append(g.id)
            else:
                print(f'Note: Optional group {xml_id} not found (App might not be installed).')
        except:
            pass
            
    vals['groups_id'] = [(6, 0, group_ids)]
    
    if existing:
        existing.write(vals)
        print('Updated boss@coffee.com')
    else:
        User.create(vals)
        print('Created boss@coffee.com')

    env.cr.commit()
    print('Success.')

except Exception as e:
    print(f'Error: {e}')
    env.cr.rollback()

