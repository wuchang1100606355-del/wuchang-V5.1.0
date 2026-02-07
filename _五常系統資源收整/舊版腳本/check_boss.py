import sys
try:
    print('Checking configuration...')
    print('Company Name:', env.ref('base.main_company').name)
    u = env['res.users'].search([('login','=','boss@coffee.com')])
    if u:
        print(f'User Found: {u.name} ({u.login})')
        print(f'Groups Count: {len(u.groups_id)}')
        # Check specific groups
        pos_group = env.ref('point_of_sale.group_pos_manager', raise_if_not_found=False)
        if pos_group and pos_group in u.groups_id:
            print('POS Manager: Yes')
        else:
            print('POS Manager: No')
    else:
        print('User NOT Found')
except Exception as e:
    print(f'Error: {e}')

