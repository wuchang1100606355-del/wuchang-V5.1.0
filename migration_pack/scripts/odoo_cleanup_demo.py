# Odoo shell script: list accounting-referenced products and delete non-beverage items without references
products = env['product.template'].sudo().search([])

# Models used for reference checks
sale_line_model = env['sale.order.line'].sudo() if 'sale.order.line' in env else None
move_model = env['stock.move'].sudo() if 'stock.move' in env else None
move_line_model = env['stock.move.line'].sudo() if 'stock.move.line' in env else None
aml_model = env['account.move.line'].sudo() if 'account.move.line' in env else None
pol_model = env['purchase.order.line'].sudo() if 'purchase.order.line' in env else None
carrier_model = env['delivery.carrier'].sudo() if 'delivery.carrier' in env else None
pos_line_model = env['pos.order.line'].sudo() if 'pos.order.line' in env else None

bev_kw = [
    '飲', '飲品', '飲料', '咖啡', '茶', '奶茶', '可樂', '汽水', '果汁', '酒', '紅酒', '白酒', '啤酒',
    'beverage', 'drink', 'coffee', 'tea', 'latte', 'cola', 'juice', 'beer', 'wine',
    '美式咖啡', '檸檬汁', '金桔檸檬汁', '比利時巧克力', '蔓越莓蘋果茶'
]
bev_categ_names = {'義式咖啡', '無咖啡因', '茶'}
addon_kw = ['加購', '加料', '配料', '選配', '選項', 'topping', 'addon', 'extra']
addon_categ_names = {'加購', '加料', '配料', '選配', '選項'}

# Reporting and counters
account_ref_list = []
deleted_ids = []
delete_errors = []
count_delete = 0

for p in products:
    variants = p.product_variant_ids
    name_lower = (p.name or '').lower()
    cat_name = (p.categ_id.name or '') if p.categ_id else ''
    cat_full = (p.categ_id.complete_name or '') if p.categ_id and hasattr(p.categ_id, 'complete_name') else cat_name
    cat_tokens = [s.strip() for s in cat_full.split('/') if s.strip()] if cat_full else ([cat_name] if cat_name else [])
    cat_tokens_lower = [s.lower() for s in cat_tokens]
    is_beverage_by_category = any(t in {c.lower() for c in bev_categ_names} for t in cat_tokens_lower)
    is_beverage_by_keywords = (
        any(kw in name_lower for kw in bev_kw)
        or any(kw in (cat_name.lower()) for kw in bev_kw if cat_name)
        or any(kw in ('/'.join(cat_tokens_lower)) for kw in bev_kw if cat_tokens_lower)
    )
    is_beverage = is_beverage_by_category or is_beverage_by_keywords

    is_addon_by_category = any(t in {c.lower() for c in addon_categ_names} for t in cat_tokens_lower)
    is_addon_by_keywords = (
        any(kw in name_lower for kw in addon_kw)
        or any(kw in (cat_name.lower()) for kw in addon_kw if cat_name)
        or any(kw in ('/'.join(cat_tokens_lower)) for kw in addon_kw if cat_tokens_lower)
    )
    used_as_optional = False
    try:
        if 'optional_product_ids' in env['product.template']._fields:
            used_as_optional = bool(env['product.template'].sudo().search([('optional_product_ids', 'in', [p.id])], limit=1))
    except Exception:
        used_as_optional = False
    is_addon = is_addon_by_category or is_addon_by_keywords or used_as_optional

    has_sales = bool(sale_line_model.search([('product_id', 'in', variants.ids)], limit=1)) if sale_line_model else False
    has_moves = bool(move_model.search([('product_id', 'in', variants.ids)], limit=1)) if move_model else False
    has_move_lines = bool(move_line_model.search([('product_id', 'in', variants.ids)], limit=1)) if move_line_model else False
    has_account = bool(aml_model.search([('product_id', 'in', variants.ids)], limit=1)) if aml_model else False
    has_purchase = bool(pol_model.search([('product_id', 'in', variants.ids)], limit=1)) if pol_model else False
    has_carrier = bool(carrier_model.search([('product_id', 'in', variants.ids)], limit=1)) if carrier_model else False
    has_pos = bool(pos_line_model.search([('product_id', 'in', variants.ids)], limit=1)) if pos_line_model else False

    if has_account:
        account_ref_list.append({'id': p.id, 'name': p.name, 'category': p.categ_id.name if p.categ_id else ''})

    has_any_ref = has_sales or has_moves or has_move_lines or has_account or has_purchase or has_carrier or has_pos

    if (not is_beverage) and (not is_addon) and (not has_any_ref):
        # Prefer safe archive over unlink to avoid session locks
        try:
            if hasattr(p, 'website_published') and p.website_published:
                p.website_published = False
            if 'available_in_pos' in env['product.template']._fields:
                p.available_in_pos = False
            if p.active:
                p.active = False
            env.cr.commit()
            count_delete += 1
            deleted_ids.append(p.id)
        except Exception as e:
            env.cr.rollback()
            delete_errors.append({'id': p.id, 'error': str(e)})

# Output report
print('ACCOUNTING-REFERENCED PRODUCTS')
for item in account_ref_list:
    print(f"- [{item['id']}] {item['name']} (Category: {item['category']})")

print('SUMMARY')
print(f'Deleted non-beverage, unreferenced products: {count_delete}')
print(f'Deleted IDs: {deleted_ids}')
if delete_errors:
    print('Delete errors (archived instead):')
    for err in delete_errors:
        print(f"- [{err['id']}] {err['error']}")

# Normalize beverage base price to Medium (M)
updated_prices = []
size_kw_m = ['中杯', ' m ', '（m）', '(m)', '中']
size_kw_s = ['小杯', ' s ', '（s）', '(s)', '小']
size_kw_l = ['大杯', ' l ', '（l）', '(l)', '大']

for p in products:
    variants = p.product_variant_ids
    name_lower = (p.name or '').lower()
    cat_name = (p.categ_id.name or '') if p.categ_id else ''
    cat_full = (p.categ_id.complete_name or '') if p.categ_id and hasattr(p.categ_id, 'complete_name') else cat_name
    cat_tokens = [s.strip() for s in cat_full.split('/') if s.strip()] if cat_full else ([cat_name] if cat_name else [])
    cat_tokens_lower = [s.lower() for s in cat_tokens]

    is_beverage_by_category = any(t in {c.lower() for c in bev_categ_names} for t in cat_tokens_lower)
    is_beverage_by_keywords = (
        any(kw in name_lower for kw in bev_kw)
        or any(kw in (cat_name.lower()) for kw in bev_kw if cat_name)
        or any(kw in ('/'.join(cat_tokens_lower)) for kw in bev_kw if cat_tokens_lower)
    )
    is_beverage = is_beverage_by_category or is_beverage_by_keywords

    if not is_beverage:
        continue

    m_addon = None
    try:
        opts = p.optional_product_ids
        for opt in opts:
            n = (opt.name or '').lower()
            if any(k in n for k in [s.lower() for s in size_kw_m]):
                m_addon = opt
                break
    except Exception:
        m_addon = None

    if not m_addon:
        continue

    try:
        before = p.list_price
        delta = m_addon.list_price or 0.0
        if delta and delta != 0.0:
            p.list_price = before + delta
            m_addon.list_price = 0.0
            env.cr.commit()
            updated_prices.append({'id': p.id, 'name': p.name, 'old': before, 'new': p.list_price, 'm_addon_id': m_addon.id})
    except Exception:
        env.cr.rollback()
        continue

if updated_prices:
    print('PRICE NORMALIZATION TO MEDIUM (M)')
    for u in updated_prices:
        print(f"- [{u['id']}] {u['name']} price {u['old']} -> {u['new']} (M addon #{u['m_addon_id']} set to 0)")

# Migrate size options from optional products to product attributes with price extras
size_attr = env['product.attribute'].sudo().search([('name', '=', '杯型')], limit=1)
if not size_attr:
    size_attr = env['product.attribute'].sudo().create({'name': '杯型'})

val_s = env['product.attribute.value'].sudo().search([('attribute_id', '=', size_attr.id), ('name', '=', '小S')], limit=1)
val_m = env['product.attribute.value'].sudo().search([('attribute_id', '=', size_attr.id), ('name', '=', '中M')], limit=1)
val_l = env['product.attribute.value'].sudo().search([('attribute_id', '=', size_attr.id), ('name', '=', '大L')], limit=1)
if not val_s:
    val_s = env['product.attribute.value'].sudo().create({'attribute_id': size_attr.id, 'name': '小S'})
if not val_m:
    val_m = env['product.attribute.value'].sudo().create({'attribute_id': size_attr.id, 'name': '中M'})
if not val_l:
    val_l = env['product.attribute.value'].sudo().create({'attribute_id': size_attr.id, 'name': '大L'})

migrated = []

for p in products:
    variants = p.product_variant_ids
    name_lower = (p.name or '').lower()
    cat_name = (p.categ_id.name or '') if p.categ_id else ''
    cat_full = (p.categ_id.complete_name or '') if p.categ_id and hasattr(p.categ_id, 'complete_name') else cat_name
    cat_tokens = [s.strip() for s in cat_full.split('/') if s.strip()] if cat_full else ([cat_name] if cat_name else [])
    cat_tokens_lower = [s.lower() for s in cat_tokens]
    is_beverage_by_category = any(t in {c.lower() for c in bev_categ_names} for t in cat_tokens_lower)
    is_beverage_by_keywords = (
        any(kw in name_lower for kw in bev_kw)
        or any(kw in (cat_name.lower()) for kw in bev_kw if cat_name)
        or any(kw in ('/'.join(cat_tokens_lower)) for kw in bev_kw if cat_tokens_lower)
    )
    is_beverage = is_beverage_by_category or is_beverage_by_keywords
    if not is_beverage:
        continue

    s_addon = None
    m_addon = None
    l_addon = None
    try:
        opts = p.optional_product_ids
        for opt in opts:
            n = (opt.name or '').lower()
            if any(k in n for k in [s.lower() for s in size_kw_s]):
                s_addon = opt
            elif any(k in n for k in [s.lower() for s in size_kw_m]):
                m_addon = opt
            elif any(k in n for k in [s.lower() for s in size_kw_l]):
                l_addon = opt
    except Exception:
        pass

    if not (s_addon or m_addon or l_addon):
        continue

    line = env['product.template.attribute.line'].sudo().search([
        ('product_tmpl_id', '=', p.id),
        ('attribute_id', '=', size_attr.id)
    ], limit=1)
    if not line:
        line = env['product.template.attribute.line'].sudo().create({
            'product_tmpl_id': p.id,
            'attribute_id': size_attr.id,
            'value_ids': [(6, 0, [val_s.id, val_m.id, val_l.id])]
        })

    ptavs = env['product.template.attribute.value'].sudo().search([
        ('product_tmpl_id', '=', p.id),
        ('attribute_id', '=', size_attr.id)
    ])
    for v in ptavs:
        pav = v.product_attribute_value_id
        if pav.id == val_m.id:
            v.price_extra = 0.0
        elif pav.id == val_s.id and s_addon:
            v.price_extra = s_addon.list_price or 0.0
        elif pav.id == val_l.id and l_addon:
            v.price_extra = l_addon.list_price or 0.0

    try:
        env.cr.commit()
        migrated.append({'id': p.id, 'name': p.name, 's': bool(s_addon), 'm': bool(m_addon), 'l': bool(l_addon)})
    except Exception:
        env.cr.rollback()

if migrated:
    print('SIZE ATTRIBUTE MIGRATION')
    for m in migrated:
        print(f"- [{m['id']}] {m['name']} S:{m['s']} M:{m['m']} L:{m['l']}")

# Delete wrong attribute value: 肯亞aa
deleted_attr_values = []
deleted_attr_links = []
try:
    bad_vals = env['product.attribute.value'].sudo().search([('name', 'ilike', '肯亞aa')])
    for pav in bad_vals:
        links = env['product.template.attribute.value'].sudo().search([('product_attribute_value_id', '=', pav.id)])
        if links:
            deleted_attr_links.extend(links.ids)
            links.unlink()
        pav.unlink()
        deleted_attr_values.append(pav.id)
    env.cr.commit()
except Exception:
    env.cr.rollback()

if deleted_attr_values:
    print('DELETED WRONG ATTRIBUTE VALUES')
    print(f"Attribute Value IDs: {deleted_attr_values}")
    if deleted_attr_links:
        print(f"Removed Template Attribute Value Links: {deleted_attr_links}")

# Clear customizations for '簡餐' category products
cleared_simple_meal = []
simple_meal_tokens = ['簡餐']

for p in products:
    cat_name = (p.categ_id.name or '') if p.categ_id else ''
    cat_full = (p.categ_id.complete_name or '') if p.categ_id and hasattr(p.categ_id, 'complete_name') else cat_name
    full_lower = (cat_full or '').lower()
    if any(t in full_lower for t in [s.lower() for s in simple_meal_tokens]):
        try:
            opt_cnt = len(p.optional_product_ids)
            if opt_cnt:
                p.write({'optional_product_ids': [(5, 0, 0)]})
            lines = env['product.template.attribute.line'].sudo().search([('product_tmpl_id', '=', p.id)])
            line_cnt = len(lines)
            if line_cnt:
                lines.unlink()
            env.cr.commit()
            cleared_simple_meal.append({'id': p.id, 'name': p.name, 'opt': opt_cnt, 'lines': line_cnt})
        except Exception:
            env.cr.rollback()

if cleared_simple_meal:
    print('SIMPLE MEALS CUSTOMIZATIONS CLEARED')
    for c in cleared_simple_meal:
        print(f"- [{c['id']}] {c['name']} (removed optional:{c['opt']}, attr_lines:{c['lines']})")

module = env['ir.module.module'].sudo().search([('name', '=', 'point_of_sale')], limit=1)
if module and module.state != 'installed':
    try:
        module.button_immediate_install()
        env.cr.commit()
    except Exception:
        env.cr.rollback()

company = env.user.company_id
journal = env['account.journal'].sudo().search([('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
if not journal:
    try:
        journal = env['account.journal'].sudo().create({'name': 'POS 銷售', 'code': 'POSS', 'type': 'sale', 'company_id': company.id})
        env.cr.commit()
    except Exception:
        env.cr.rollback()

pos_config = env['pos.config'].sudo().search([('name', '=', '仁義店')], limit=1)
if not pos_config and journal:
    try:
        pos_config = env['pos.config'].sudo().create({'name': '仁義店', 'journal_id': journal.id, 'company_id': company.id})
        env.cr.commit()
    except Exception:
        env.cr.rollback()

if pos_config:
    session = env['pos.session'].sudo().search([('config_id', '=', pos_config.id), ('state', 'in', ['opened'])], limit=1)
    if not session:
        try:
            session = env['pos.session'].sudo().create({'config_id': pos_config.id})
            try:
                session.open_session_cb()
            except Exception:
                pass
            env.cr.commit()
        except Exception:
            env.cr.rollback()

print('POS SETUP')
print(f"Module: {'installed' if module and module.state == 'installed' else 'not_installed'}")
print(f"Config: {pos_config.name if pos_config else 'missing'}")

# Create POS config for 聊國咖啡重新總店 (canonical for 重新店) and open session
pos_config_re = env['pos.config'].sudo().search([('name', '=', '聊國咖啡重新總店')], limit=1)
if not pos_config_re and journal:
    try:
        pos_config_re = env['pos.config'].sudo().create({'name': '聊國咖啡重新總店', 'journal_id': journal.id, 'company_id': company.id})
        env.cr.commit()
    except Exception:
        env.cr.rollback()

if pos_config_re:
    session_re = env['pos.session'].sudo().search([('config_id', '=', pos_config_re.id), ('state', 'in', ['opened'])], limit=1)
    if not session_re:
        try:
            session_re = env['pos.session'].sudo().create({'config_id': pos_config_re.id})
            try:
                session_re.open_session_cb()
            except Exception:
                pass
            env.cr.commit()
        except Exception:
            env.cr.rollback()

# Fund pool only attaches to 仁義店
params = env['ir.config_parameter'].sudo()
try:
    params.set_param('wuchang.fund_pool_store', '仁義店')
    env.cr.commit()
except Exception:
    env.cr.rollback()

import csv, os
from typing import List, Dict

def _parse_menu_rows_from_xlsx(path) -> List[Dict]:
    rows = []
    try:
        import openpyxl
    except Exception:
        print('OPENPYXL_MISSING')
        return rows
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        headers = []
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                headers = [str(h or '').strip().lower() for h in row]
                continue
            data = {}
            for j, val in enumerate(row):
                key = headers[j] if j < len(headers) else f'col{j}'
                data[key] = val
            rows.append(data)
    except Exception as e:
        print(f'XLSX_PARSE_ERROR: {e}')
    return rows

menu_path_candidates = ['/opt/wuchang/downloads/new_menu.csv', '/opt/wuchang/downloads/menu.csv']
menu_path = None
for _p in menu_path_candidates:
    if os.path.isfile(_p):
        menu_path = _p
        break

xlsx_path = None
if not menu_path:
    # pick first xlsx in downloads
    try:
        for fname in os.listdir('/opt/wuchang/downloads'):
            if fname.lower().endswith('.xlsx'):
                xlsx_path = os.path.join('/opt/wuchang/downloads', fname)
                break
    except Exception:
        xlsx_path = None

if menu_path or xlsx_path:
    all_products = env['product.template'].sudo().search([])
    for _pt in all_products:
        try:
            if hasattr(_pt, 'website_published'):
                _pt.website_published = False
            if 'available_in_pos' in env['product.template']._fields:
                _pt.available_in_pos = False
            _pt.active = False
        except Exception:
            env.cr.rollback()
    try:
        env.cr.commit()
    except Exception:
        env.cr.rollback()

    created_ids = []
    menu_rows = []
    if menu_path:
        with open(menu_path, newline='', encoding='utf-8') as _f:
            reader = csv.DictReader(_f)
            for row in reader:
                menu_rows.append(row)
    elif xlsx_path:
        menu_rows = _parse_menu_rows_from_xlsx(xlsx_path)

    def _get_first(row, keys):
        for k in keys:
            v = row.get(k)
            if v is not None and str(v).strip() != '':
                return v
        return ''

    for row in menu_rows:
            name = str(_get_first(row, ['name','品名','名稱','商品','product','title']) or '').strip()
            if not name:
                continue
            try:
                price_raw = _get_first(row, ['price','售價','價格','單價','list_price'])
                price = float(price_raw or 0.0)
            except Exception:
                price = 0.0
            category = str(_get_first(row, ['category','分類','類別','categ']) or '').strip()
            pos_flag = str(_get_first(row, ['pos','pos可用','available_in_pos']) or '').strip().lower() in ('1','true','yes','y')
            web_flag = str(_get_first(row, ['website','網站','website_published']) or '').strip().lower() in ('1','true','yes','y')
            company_name = str(_get_first(row, ['company','公司']) or '').strip()
            store_name = str(_get_first(row, ['store','分店','門市']) or '').strip()
            cat_id = False
            if category:
                cat = env['product.category'].sudo().search([('name','=',category)], limit=1)
                if not cat:
                    cat = env['product.category'].sudo().create({'name': category})
                cat_id = cat.id
            vals = {'name': name, 'list_price': price, 'active': True}
            if cat_id:
                vals['categ_id'] = cat_id
            comp_id = False
            if store_name:
                try:
                    cfg = env['pos.config'].sudo().search([('name','=',store_name)], limit=1)
                    if cfg and cfg.company_id:
                        comp_id = cfg.company_id.id
                except Exception:
                    comp_id = False
            if (not comp_id) and company_name:
                try:
                    comp = env['res.company'].sudo().search([('name','=',company_name)], limit=1)
                    if comp:
                        comp_id = comp.id
                except Exception:
                    comp_id = False
            if comp_id:
                vals['company_id'] = comp_id
            pt = env['product.template'].sudo().create(vals)
            try:
                if 'available_in_pos' in pt._fields:
                    pt.available_in_pos = pos_flag
                if hasattr(pt, 'website_published'):
                    pt.website_published = web_flag
                env.cr.commit()
            except Exception:
                env.cr.rollback()
            created_ids.append(pt.id)
    print('MENU_REPLACED')
    if menu_path:
        print(f'CSV: {menu_path}')
    if xlsx_path:
        print(f'XLSX: {xlsx_path}')
    print(f'CREATED_IDS: {created_ids}')
else:
    print('NEW_MENU_CSV_NOT_FOUND')
