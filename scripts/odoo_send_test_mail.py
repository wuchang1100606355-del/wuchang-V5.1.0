import json, os
import odoo
from odoo import api, SUPERUSER_ID
db = odoo.tools.config.get('db_name')
reg = odoo.registry(db)
with reg.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    to = os.environ.get('TO_EMAIL','')
    frm = os.environ.get('SENDGRID_FROM_EMAIL','')
    if not to or not frm:
        print(json.dumps({'ok': False, 'error': 'missing_to_or_from'}))
    else:
        Mail = env['mail.mail'].sudo()
        body = "<div>這是一封雲端郵件測試。若你收到此信，表示 SendGrid 設定成功。</div>"
        rec = Mail.create({'subject': '雲端郵件測試', 'body_html': body, 'email_to': to, 'email_from': frm})
        sent = False
        try:
            rec.send()
            sent = True
        except Exception:
            sent = False
        print(json.dumps({'ok': True, 'queued': (not sent), 'email': to}))
