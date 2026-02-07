# 無程式碼 Odoo 咖啡店一鍵重建腳本（資料自動匯入版）
# 功能：
# 1. 以 Odoo 內建資料（商品、顧客、訂單）自動重建咖啡店 POS/管理環境
# 2. 不需寫程式，僅需執行本腳本即可完成菜單、會員、訂單、POS、報表等全流程
# 3. 產生操作紀錄與簡易報告

import xmlrpc.client
import json
from datetime import datetime

# Odoo 伺服器連線資訊（請依實際環境調整）
url = 'http://localhost:8069'
db = 'odoo_db'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

report = {
    'timestamp': datetime.now().isoformat(),
    'steps': [],
    'created_products': [],
    'created_customers': [],
    'created_orders': [],
    'summary': ''
}

# 1. 建立商品（菜單）
report['steps'].append('建立咖啡店菜單商品')
products = [
    {'name': '美式咖啡', 'list_price': 80},
    {'name': '拿鐵', 'list_price': 100},
    {'name': '卡布奇諾', 'list_price': 110},
    {'name': '手沖單品', 'list_price': 150},
    {'name': '司康', 'list_price': 60},
    {'name': '起司蛋糕', 'list_price': 90}
]
for p in products:
    pid = models.execute_kw(db, uid, password, 'product.product', 'create', [{
        'name': p['name'],
        'list_price': p['list_price'],
        'type': 'consu',
        'sale_ok': True,
        'purchase_ok': False
    }])
    report['created_products'].append({'id': pid, **p})

# 2. 建立顧客（會員）
report['steps'].append('建立咖啡店會員')
customers = [
    {'name': '王小明', 'phone': '0912345678'},
    {'name': '林美麗', 'phone': '0922333444'},
    {'name': '陳志強', 'phone': '0933222111'}
]
for c in customers:
    cid = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
        'name': c['name'],
        'phone': c['phone'],
        'customer_rank': 1
    }])
    report['created_customers'].append({'id': cid, **c})

# 3. 建立訂單（POS 訂單範例）
report['steps'].append('建立咖啡店訂單')
order = {
    'partner_id': report['created_customers'][0]['id'],
    'lines': [
        (0, 0, {'product_id': report['created_products'][0]['id'], 'qty': 2, 'price_unit': 80}),
        (0, 0, {'product_id': report['created_products'][1]['id'], 'qty': 1, 'price_unit': 100})
    ]
}
order_id = models.execute_kw(db, uid, password, 'pos.order', 'create', [{
    'partner_id': order['partner_id'],
    'lines': order['lines'],
    'amount_paid': 260,
    'amount_total': 260,
    'state': 'paid'
}])
report['created_orders'].append({'id': order_id, 'customer': report['created_customers'][0]['name'], 'items': ['美式咖啡x2', '拿鐵x1']})

# 4. 產生操作紀錄
report['summary'] = '已自動重建咖啡店菜單、會員、訂單，POS 環境可直接使用。'
with open('odoo_no_code_cafe_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print('[小J] 無程式碼 Odoo 咖啡店一鍵重建完成，操作紀錄已產生 odoo_no_code_cafe_report.json')
