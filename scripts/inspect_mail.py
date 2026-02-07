# Run inside "odoo shell" where `env` is available
try:
    servers = env['ir.mail_server'].sudo().search_read([], ['name','smtp_host','smtp_port','smtp_encryption','smtp_user'])
    queue = env['mail.mail'].sudo().search([], order='id desc', limit=5)
    print('SERVERS', servers)
    for m in queue:
        print('MAIL', m.id, m.subject, m.email_to, m.state, (m.failure_reason or '')[:200])
except Exception as e:
    print('ERROR', str(e))
