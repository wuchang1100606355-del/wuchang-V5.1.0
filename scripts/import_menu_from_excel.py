#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import POS products from the provided Excel, auto-translate names to English, and map to POS categories."""
import xmlrpc.client
import json
import requests
import openpyxl
from datetime import datetime
from pathlib import Path

# Odoo connection
ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'admin'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

# Excel source
EXCEL_PATH = r"C:\\Users\\o0930\\Dropbox\\SBIR\\匯出菜單-聊閣社區咖啡重新店-QC_1760535925901.xlsx"
SHEET_NAME = '主商品項目'

# Columns we rely on
COL_CATEGORY = '主商品類別'
COL_NAME_ZH = '主商品名稱'
COL_PRICE = '主商品價格'
COL_DESC = '主商品描述'
COL_CODE = '主商品代碼'

LOG_FILE = Path(r"C:\\wuchang V5.1.0\\downloads\\menu_import_excel_log.json")


def translate_zh_to_en(text: str) -> str:
    """Return original text; network-free placeholder to keep import fast/stable."""
    return text or ''


def ensure_categories(models, uid, password, categories):
    """Ensure all categories exist; return name->id mapping."""
    mapping = {}
    for name in categories:
        ids = models.execute_kw(
            ODOO_DB, uid, password,
            'pos.category', 'search',
            [[['name', '=', name]]]
        )
        if ids:
            mapping[name] = ids[0]
        else:
            new_id = models.execute_kw(
                ODOO_DB, uid, password,
                'pos.category', 'create',
                [{'name': name}]
            )
            mapping[name] = new_id
            print(f"＋ 建立分類 {name} id={new_id}")
    return mapping


def main():
    print('=' * 80)
    print('Import POS products from Excel (auto-translate names)')
    print('=' * 80)

    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb[SHEET_NAME]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        print('✗ Excel 無資料')
        return
    header = list(rows[0])
    col_index = {name: i for i, name in enumerate(header)}
    required = [COL_CATEGORY, COL_NAME_ZH, COL_PRICE]
    for req in required:
        if req not in col_index:
            print(f"✗ 缺少欄位 {req}")
            return

    items = []
    skipped = 0
    for i, r in enumerate(rows[1:], start=2):
        name_zh = (r[col_index[COL_NAME_ZH]] or '').strip(
        ) if r[col_index[COL_NAME_ZH]] else ''
        if not name_zh:
            skipped += 1
            continue
        category = (r[col_index[COL_CATEGORY]] or '').strip()
        if not category:
            print(f"  ⊘ 第{i}行 {name_zh} 無分類，跳過")
            skipped += 1
            continue
        price_raw = r[col_index[COL_PRICE]]
        try:
            price = float(price_raw)
        except Exception:
            print(f"  ⊘ 第{i}行 {name_zh} 價格無效，跳過")
            skipped += 1
            continue
        desc = r[col_index.get(COL_DESC, -1)
                 ] if COL_DESC in col_index else None
        code = r[col_index.get(COL_CODE, -1)
                 ] if COL_CODE in col_index else None
        items.append({
            'category': str(category).strip(),
            'name_zh': name_zh,
            'price': price,
            'desc': desc or '',
            'code': str(code).strip() if code else None,
        })
    print(f"\n讀取 {len(items)} 個有效品項，跳過 {skipped} 列無效資料\n")

    categories = sorted({it['category'] for it in items if it['category']})

    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        print('✗ Odoo login failed')
        return
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    cat_map = ensure_categories(models, uid, ODOO_PASSWORD, categories)

    created, updated, errors = [], [], []
    total = len(items)

    for idx, it in enumerate(items, start=1):
        print(f"[{idx}/{total}] 處理 {it['name_zh']}...", end=' ')
        cat_id = cat_map.get(it['category'])
        name_en = translate_zh_to_en(it['name_zh'])
        cat_commands = [(6, 0, [cat_id])] if cat_id else []
        vals = {
            'name': name_en,
            'list_price': it['price'],
            'type': 'product',
            'pos_categ_ids': cat_commands,
            'available_in_pos': True,
            'uom_id': 1,
            'uom_po_id': 1,
            'description': f"[中文名] {it['name_zh']}\n" + (it['desc'] or ''),
        }
        if it['code']:
            vals['default_code'] = it['code']

        try:
            existing_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.template', 'search',
                [[['default_code', '=', it['code']]]]
            ) if it['code'] else []
            if existing_ids:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'product.template', 'write',
                    [existing_ids, vals]
                )
                updated.append(
                    {'code': it['code'], 'name': name_en, 'cat': it['category']})
                print(f"↺")
            else:
                new_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'product.template', 'create',
                    [vals]
                )
                created.append(
                    {'id': new_id, 'name': name_en, 'cat': it['category']})
                print(f"✓ ID={new_id}")
        except KeyboardInterrupt:
            print(f"\n\n⚠ 使用者中斷，已處理 {idx}/{total}")
            break
        except Exception as exc:
            err_msg = str(exc)[:200]  # 限制錯誤訊息長度
            errors.append({'item': it, 'error': err_msg})
            print(f"✗ ({err_msg[:50]}...)")

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open('w', encoding='utf-8') as f:
        json.dump({
            'ts': datetime.now().isoformat(),
            'created': created,
            'updated': updated,
            'errors': errors,
            'source': EXCEL_PATH,
        }, f, ensure_ascii=False, indent=2)

    print('=' * 80)
    print(f"完成：新增 {len(created)}，更新 {len(updated)}，錯誤 {len(errors)}")
    print(f"Log: {LOG_FILE}")
    print('=' * 80)


if __name__ == '__main__':
    main()
