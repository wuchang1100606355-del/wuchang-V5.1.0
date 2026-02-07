import json, os
import odoo
from odoo import api, SUPERUSER_ID
db = odoo.tools.config.get('db_name')
reg = odoo.registry(db)
with reg.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    key = os.environ.get('SENDGRID_API_KEY', '')
    frm = os.environ.get('SENDGRID_FROM_EMAIL', '')
    name = os.environ.get('SENDGRID_NAME', 'SendGrid')
    if not key or not frm:
        print(json.dumps({'ok': False, 'error': 'missing_env', 'need': ['SENDGRID_API_KEY','SENDGRID_FROM_EMAIL']}))
    else:
        MailServer = env['ir.mail_server'].sudo()
        existing = MailServer.search([('smtp_host','=', 'smtp.sendgrid.net')], limit=1)
        vals = {
            'name': name,
            'smtp_host': 'smtp.sendgrid.net',
            'smtp_port': 587,
            'smtp_encryption': 'starttls',
            'smtp_user': 'apikey',
            'smtp_pass': key,
            'smtp_debug': False,
            'from_filter': frm,
        }
        if existing:
            existing.write(vals)
            rec = existing
        else:
            rec = MailServer.create(vals)
        print(json.dumps({'ok': True, 'server_id': rec.id, 'from': frm}))
