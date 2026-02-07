import os
import hashlib
import base64

pwd = 'odoo'
salt_bytes = os.urandom(16)
dk = hashlib.pbkdf2_hmac('sha512', pwd.encode(), salt_bytes, 60000)
salt_b64 = base64.b64encode(salt_bytes).decode()
digest_b64 = base64.b64encode(dk).decode()
print(f'$pbkdf2-sha512$60000${salt_b64}${digest_b64}')
