import json, os
# Run inside "odoo shell" where `env` is available
try:
    to = os.environ.get('TO_EMAIL', '')
    if not to:
        print(json.dumps({'ok': False, 'error': 'missing_to'}))
    else:
        Mail = env['mail.mail'].sudo()
        body = """
        <div style="font-family:Inter,system-ui">
          <p>這是一封測試通知（安裝／黨紀規劃摘要）。</p>
          <ul>
            <li>秘書長視訊專線：WebRTC，自建 SFU，錄影存證</li>
            <li>郵件機制：模板＋審計＋退信重試</li>
            <li>記憶封存：memory_store/ 不壓縮＋雜湊，每日驗證</li>
          </ul>
        </div>
        """
        rec = Mail.create({'subject': '安裝／黨紀通知（測試）', 'body_html': body, 'email_to': to})
        sent = False
        try:
            rec.send()
            sent = True
        except Exception:
            sent = False
        print(json.dumps({'ok': True, 'queued': (not sent), 'email': to}))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
