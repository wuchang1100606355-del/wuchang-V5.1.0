import logging
import sys

# Setup logging
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger('wuchang_org_setup')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

print('Starting Wuchang Organization Setup (Part 3 - Debug)...')

if 'env' not in locals():
    print('Error: env not found.')
    sys.exit(1)

try:
    ResCompany = env['res.company']
    ResUsers = env['res.users']
    
    # Debug HR Module
    mod_hr = env['ir.module.module'].search([('name', '=', 'hr')], limit=1)
    if mod_hr:
        logger.info(f'HR Module Status: {mod_hr.state}')
    else:
        logger.error('HR Module record not found!')

    # Check HR Department
    if 'hr.department' in env:
        HrDepartment = env['hr.department']
    else:
        logger.warning('hr.department not in env keys. Trying to fetch from registry...')
        try:
            HrDepartment = env.registry['hr.department'] # Access model directly from registry?
            # env['hr.department'] should work if loaded.
        except KeyError:
             logger.error('hr.department truly missing.')
             HrDepartment = None

    # 1. Retrieve Companies
    main_company = env.ref('base.main_company')
    main_company.write({
        'name': '新北市三重區五常社區協會',
    })
    
    # 2. Create Departments
    if HrDepartment:
        def create_dept(name, parent_id=False, company_id=main_company.id):
            dept = env['hr.department'].search([('name', '=', name), ('company_id', '=', company_id)], limit=1)
            if not dept:
                dept = env['hr.department'].create({
                    'name': name,
                    'company_id': company_id,
                    'parent_id': parent_id
                })
                logger.info(f'Created Department: {name}')
            else:
                if parent_id and dept.parent_id.id != parent_id:
                    dept.write({'parent_id': parent_id})
                    logger.info(f'Updated Department Parent: {name}')
            return dept

        # Level 1
        dept_secretariat = create_dept('秘書處')
        dept_service = create_dept('服務組')
        dept_general = create_dept('庶務組')
        dept_activity = create_dept('活動組')

        # Level 2
        dept_ancestral = create_dept('祖訓組', parent_id=dept_secretariat.id)
        dept_special = create_dept('專勤隊', parent_id=dept_service.id)
        dept_finance = create_dept('財務', parent_id=dept_general.id)
        dept_wishing = create_dept('許願樹', parent_id=dept_activity.id)
    else:
        logger.error('Skipping Departments due to missing Model.')

    # 3. Verify User Access
    property_company = ResCompany.search([('name', '=', '五常物業規劃顧問股份有限公司')], limit=1)
    coffee_company = ResCompany.search([('name', '=', '上品聊國咖啡烘培館')], limit=1)
    
    little_j = ResUsers.search([('login', '=', 'little_j@wuchang.life')], limit=1)
    if little_j:
        little_j.write({
             'company_ids': [(6, 0, [main_company.id, property_company.id, coffee_company.id])]
        })
        logger.info(f'Verified User Access: {little_j.name}')

    env.cr.commit()
    print('Wuchang Organization Setup Part 3 Completed.')

except Exception as e:
    print(f'Error: {e}')
    # env.cr.rollback() 
    # sys.exit(1)

