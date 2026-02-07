import json
import os


def _choose_db_name(odoo):
    try:
        db = odoo.tools.config.get('db_name')
        if isinstance(db, str) and db.strip():
            return db.strip()
    except Exception:
        pass
    return os.environ.get('POSTGRES_DB') or os.environ.get('DB_NAME') or 'postgres'


try:
    import odoo
    from odoo import api, SUPERUSER_ID
    db_name = _choose_db_name(odoo)
    reg = odoo.registry(db_name)
    with reg.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        p = env['ir.config_parameter'].sudo()
        p.set_param('wuchang.ai_mode', 'local_ollama')
        p.set_param('wuchang.ollama_model', 'llama3.1')
        p.set_param('wuchang.llm.daily_quota', '0')
        domain_lock_env = (os.environ.get(
            'DOMAIN_LOCK', '').strip().lower() in ('1', 'true', 'yes'))
        if domain_lock_env:
            p.set_param('wuchang.domain.lock', 'True')
        domain_lock = ((p.get_param('wuchang.domain.lock')
                       or '').strip().lower() in ('1', 'true', 'yes'))
        website_host = os.environ.get('WEBSITE_HOST', '').strip()
        website_clear = (os.environ.get('WEBSITE_HOST_CLEAR',
                         '').strip().lower() in ('1', 'true', 'yes'))
        if not domain_lock:
            if website_clear:
                p.set_param('website.canonical_host', '')
            elif website_host:
                p.set_param('website.canonical_host', website_host)
        agent_email = os.environ.get('AGENT_EMAIL', '') or 'admin@wuchang.life'
        agent_name = os.environ.get('AGENT_NAME', '') or '小j'
        try:
            p.set_param('wuchang.agent.enabled', 'True')
            p.set_param('wuchang.agent.name', agent_name)
            p.set_param('wuchang.agent.email', agent_email)
            Partner = env['res.partner'].sudo()
            qp = Partner.search([('email', '=', agent_email)], limit=1)
            vals = {'name': agent_name, 'email': agent_email}
            if qp:
                qp.write(vals)
            else:
                Partner.create(vals)
        except Exception:
            pass
        try:
            BranchCo = env['res.company'].sudo().search([('name', '=', '聊國咖啡仁義分店')], limit=1)
            MainCo = env['res.company'].sudo().search([('name', '=', '聊國咖啡重新總店')], limit=1)
            PosConfig = env['pos.config'].sudo()
            branch_cfg = PosConfig.search([('name', '=', '聊國咖啡仁義分店')], limit=1)
            main_cfg = PosConfig.search([('name', '=', '聊國咖啡重新總店')], limit=1)
            Method = env['pos.payment.method'].sudo()
            happy = Method.search([('name', '=', '幸福幣')], limit=1)
            if not happy and BranchCo:
                happy = Method.create({'name': '幸福幣', 'company_id': BranchCo.id})
            cash = Method.search([('name', '=', '現金')], limit=1)
            if not cash and MainCo:
                cash = Method.create({'name': '現金', 'company_id': MainCo.id or BranchCo.id})
            if branch_cfg and happy:
                branch_cfg.write({'payment_method_ids': [(4, happy.id)]})
            if main_cfg and happy:
                pass
        except Exception:
            pass
        try:
            p.set_param('branding.association', '新北市三重區五常社區發展協會（創辦人任總幹事）')
            p.set_param('branding.producer', '五常物業規劃顧問股份有限公司（新創社企閉鎖型；新型專利）')
            p.set_param('branding.coffee_org', '聊國咖啡重新總店（出資捐贈、品牌捐贈業主創辦人）；聊國咖啡仁義分店（社區產業業主協會創辦人捐贈）')
            p.set_param('branding.patent', '新型專利')
            main_phone = (os.environ.get('COFFEE_MAIN_PHONE', '') or '').strip()
            branch_phone = (os.environ.get('COFFEE_BRANCH_PHONE', '') or '').strip()
            patent_no = (os.environ.get('PATENT_NO', '') or '').strip()
            if main_phone:
                p.set_param('branding.coffee_main_phone', main_phone)
            if branch_phone:
                p.set_param('branding.coffee_branch_phone', branch_phone)
            if patent_no:
                p.set_param('branding.patent_no', patent_no)
        except Exception:
            pass
        try:
            company = env.company or env['res.company'].search([], limit=1)
            if company:
                vals = {'name': '新北市三重區五常社區發展協會'}
                company_phone = (os.environ.get('COMPANY_PHONE', '') or '').strip()
                if company_phone:
                    vals['phone'] = company_phone
                company.sudo().write(vals)
        except Exception:
            pass
        print(json.dumps({
            'ok': True,
            'db': db_name,
            'ai_mode': 'local_ollama',
            'ollama_model': 'llama3.1',
            'agent_email': p.get_param('wuchang.agent.email') or '',
            'agent_name': p.get_param('wuchang.agent.name') or '',
            'domain_lock': (p.get_param('wuchang.domain.lock') or '')
        }))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
