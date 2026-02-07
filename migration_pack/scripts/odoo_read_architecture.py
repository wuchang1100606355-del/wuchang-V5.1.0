import json, os

try:
    from odoo import api, SUPERUSER_ID
    import odoo
except Exception:
    odoo = None
    api = None
    SUPERUSER_ID = 1

def _db_name():
    try:
        return odoo.tools.config.get('db_name')
    except Exception:
        return os.environ.get('POSTGRES_DB') or os.environ.get('DB_NAME') or 'odoo'

def main():
    if not odoo or not api:
        out = {'ok': False, 'error': 'odoo_env_unavailable'}
        try:
            with open('/tmp/arch.json','w') as f:
                f.write(json.dumps(out))
        except Exception:
            pass
        print(json.dumps(out))
        return
    db = _db_name()
    registry = odoo.registry(db)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        icp = env['ir.config_parameter'].sudo()
        company = env.company or env['res.company'].sudo().search([], limit=1)
        website_name = ''
        try:
            website = env['website'].sudo().search([], limit=1)
            website_name = website.name or ''
        except Exception:
            website_name = ''
        cfgs = env['pos.config'].sudo().search([])
        configs = [{'id': c.id, 'name': (c.name or ''), 'company_id': (c.company_id.id if c.company_id else None)} for c in cfgs]
        modules = env['ir.module.module'].sudo().search_read([('state','=','installed')], ['name','shortdesc','latest_version'])
        featured_store = (icp.get_param('wuchang.featured_store') or '').strip()
        vault_raw = icp.get_param('wuchang.memory.vault.json') or '{}'
        try:
            vault = json.loads(vault_raw)
        except Exception:
            vault = {}
        ui_contract = vault.get('ui.contract.delivery') or {}
        # Counts per store/company
        counts = []
        Product = env['product.template'].sudo()
        fields = Product.fields_get()
        base_dom = [('sale_ok','=',True)]
        if 'available_in_pos' in fields:
            base_dom.append(('available_in_pos','=',True))
        for c in cfgs:
            cid = c.company_id.id if c.company_id else None
            dom = list(base_dom)
            if cid:
                dom.append(('company_id','=',cid))
            total = Product.search_count(dom)
            counts.append({'store': c.name or '', 'company_id': cid, 'products': total})
        snapshot = {
            'company': {'id': company.id, 'name': company.name},
            'website': {'name': website_name},
            'pos_configs': configs,
            'modules_installed': modules,
            'featured_store': featured_store,
            'ui_contract_delivery': ui_contract,
            'product_counts': counts,
        }
        out = {'ok': True, 'snapshot': snapshot}
        try:
            with open('/tmp/arch.json','w') as f:
                f.write(json.dumps(out, ensure_ascii=False))
        except Exception:
            pass
        print(json.dumps(out, ensure_ascii=False))

if __name__ == '__main__':
    main()
