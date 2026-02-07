import logging
from odoo import api, SUPERUSER_ID

def run_probe(env):
    report = {}
    
    # 0. Terminal#886-1011 Check
    term_886 = env['pos.config'].search([('name', 'ilike', '886-1011')])
    report['terminal_886_1011_status'] = {
        'found_in_pos_config': bool(term_886),
        'pos_config_name': term_886.name if term_886 else None,
        'active': term_886.active if term_886 else None
    }
    if not term_886:
        term_partner = env['res.partner'].search([('name', 'ilike', '886-1011')])
        report['terminal_886_1011_status']['found_in_partner'] = bool(term_partner)
        report['terminal_886_1011_status']['partner_name'] = term_partner.name if term_partner else None

    # 1. Module Status & Dependencies
    module = env['ir.module.module'].search([('name', '=', 'wuchang_core')])
    report['wuchang_core_status'] = module.state if module else 'not_found'

    deps = ['base', 'web', 'point_of_sale', 'website', 'hr', 'project', 'maintenance']
    dep_status = {}
    for dep in deps:
        m = env['ir.module.module'].search([('name', '=', dep)])
        dep_status[dep] = m.state if m else 'missing'
    report['dependencies'] = dep_status

    # 2. Jurisdiction
    jurisdiction_keywords = ['五順', '五常', '仁忠']
    all_partners = env['res.partner'].search([])
    wuchang_partners = 0
    non_wuchang_partners = 0
    active_non_wuchang = 0

    for p in all_partners:
        address = str(p.street or '') + str(p.city or '') + str(p.state_id.name or '')
        is_jurisdiction = any(k in address for k in jurisdiction_keywords)
        if is_jurisdiction:
            wuchang_partners += 1
        else:
            non_wuchang_partners += 1
            if p.active:
                active_non_wuchang += 1

    report['wuchang_partners_count'] = wuchang_partners
    report['non_wuchang_partners_count'] = non_wuchang_partners
    report['active_non_wuchang_risk'] = active_non_wuchang

    # 3. Model & Field Verification
    model_issues = []
    if 'wuchang.property.community' in env:
        if 'committee_partner_id' not in env['wuchang.property.community']._fields:
            model_issues.append('Missing field: committee_partner_id in wuchang.property.community')
    else:
        model_issues.append('Model missing: wuchang.property.community')

    if 'spatial_ref' not in env['res.partner']._fields:
        model_issues.append('Missing field: spatial_ref in res.partner (Spatiotemporal Index)')

    report['model_issues'] = model_issues

    # 4. Core Sister Integration
    sister_user = env['res.users'].search([('login', '=', 'core_sister_service')], limit=1)
    report['core_sister_user_exists'] = bool(sister_user)

    return report

print('--- PROBE RESULTS START ---')
try:
    results = run_probe(env)
    print(results)
except Exception as e:
    print(f'Probe failed: {e}')
print('--- PROBE RESULTS END ---')
