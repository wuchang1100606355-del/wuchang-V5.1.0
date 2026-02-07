import json
import os

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

def _ensure_category(env, name):
    cat = env['product.category'].sudo().search([('name','=',name)], limit=1)
    if not cat:
        cat = env['product.category'].sudo().create({'name': name})
    return cat

def main():
    if not odoo or not api:
        print(json.dumps({'ok': False, 'error': 'odoo_env_unavailable'}))
        return
    db = _db_name()
    registry = odoo.registry(db)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        cfg = env['pos.config'].sudo().search([('name','=', '聊國咖啡重新總店')], limit=1)
        if not cfg:
            print(json.dumps({'ok': False, 'error': 'pos_config_not_found'}))
            return
        comp_id = cfg.company_id.id if cfg.company_id else False
        cats = {
            '咖啡': _ensure_category(env, '咖啡'),
            '茶': _ensure_category(env, '茶'),
            '甜點': _ensure_category(env, '甜點'),
            '惜食櫃': _ensure_category(env, '惜食櫃'),
        }
        items = [
            {'name': '美式咖啡', 'price': 80, 'cat': '咖啡'},
            {'name': '拿鐵', 'price': 120, 'cat': '咖啡'},
            {'name': '阿里山烏龍', 'price': 150, 'cat': '茶'},
            {'name': '錫蘭紅茶', 'price': 90, 'cat': '茶'},
            {'name': '起司蛋糕', 'price': 90, 'cat': '甜點'},
            {'name': '手工餅乾', 'price': 80, 'cat': '甜點'},
            {'name': '今日惜食麵包', 'price': 45, 'cat': '惜食櫃'},
            {'name': '即期牛奶', 'price': 30, 'cat': '惜食櫃'},
        ]
        created = []
        for it in items:
            vals = {'name': it['name'], 'list_price': it['price'], 'active': True}
            cat = cats.get(it['cat'])
            if cat:
                vals['categ_id'] = cat.id
            if comp_id:
                vals['company_id'] = comp_id
            pt = env['product.template'].sudo().create(vals)
            try:
                if 'available_in_pos' in pt._fields:
                    pt.available_in_pos = True
                if hasattr(pt, 'website_published'):
                    pt.website_published = True
                env.cr.commit()
            except Exception:
                env.cr.rollback()
            created.append(pt.id)
        print(json.dumps({'ok': True, 'created_ids': created}))

if __name__ == '__main__':
    main()
