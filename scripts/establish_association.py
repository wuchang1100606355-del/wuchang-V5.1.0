import odoo
from odoo import api, SUPERUSER_ID

def establish_company():
    try:
        odoo.tools.config.parse_config(['-d', 'wuchang', '--db_host=wuchang-db', '--db_user=odoo', '--db_password=odoo'])
        registry = odoo.registry('wuchang')
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # 1. Find or Create the Association Partner
            assoc_name = '新北市三重區五常社區發展協會'
            short_name = '五常社區發展協會'
            
            partner = env['res.partner'].search(['|', ('name', 'like', assoc_name), ('name', 'like', short_name)], limit=1)
            
            if partner:
                print(f'Found existing Partner: {partner.name} (ID: {partner.id})')
                # CRITICAL: Remove company linkage to allow re-assignment
                if partner.company_id:
                    print(f'Removing current company link: {partner.company_id.name}')
                    partner.write({'company_id': False})
                
                partner.write({
                    'name': assoc_name,
                    'property_management_role': 'association',
                    'is_company': True
                })
            else:
                print('Creating new Partner for Association...')
                partner = env['res.partner'].create({
                    'name': assoc_name,
                    'is_company': True,
                    'property_management_role': 'association',
                    'street': '新北市三重區五常里', 
                    'company_id': False # Ensure global
                })
                
            # 2. Check if Company exists
            company = env['res.company'].search([('name', '=', assoc_name)], limit=1)
            if not company:
                print('Creating Main Company for Association...')
                # Check for currency
                twd = env.ref('base.TWD', raise_if_not_found=False)
                currency_id = twd.id if twd else env.ref('base.USD').id
                
                company = env['res.company'].create({
                    'name': assoc_name,
                    'partner_id': partner.id,
                    'currency_id': currency_id,
                })
                print(f'Created Company: {company.name} (ID: {company.id})')
            else:
                print(f'Company already exists: {company.name} (ID: {company.id})')
            
            # Ensure Partner is linked to this Company
            if partner.company_id != company:
                partner.write({'company_id': company.id})
                print('Linked Partner to new Company.')

            # 3. Structure Analysis (Log)
            print('--- Association Company Status ---')
            print(f'Company: {company.name} (ID: {company.id})')
            print(f'Partner: {partner.name} (ID: {partner.id})')
            
            cr.commit()
            print('Association Company established successfully.')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    establish_company()

