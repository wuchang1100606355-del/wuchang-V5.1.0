import os

fp = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\pos_config_ext.py'

with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

if 'ValidationError' not in c:
    c = c.replace('from odoo.exceptions import AccessError', 'from odoo.exceptions import AccessError, ValidationError')

# \u4ec1\u7fa9 (Renyi)
# \u56b4\u683c\u63a7\u7ba1... (Strict Control Msg)
err = '\u56b4\u683c\u63a7\u7ba1\uff1a\u53ea\u6709\u300c\u804a\u570b\u5496\u5561\u4ec1\u7fa9\u5206\u5e97\u300d\u5373\u70ba\u57fa\u91d1\u6c60\u672c\u8eab\uff0c\u624d\u53ef\u555f\u7528\u6b64\u6a21\u5f0f\u3002'
kw = '\u4ec1\u7fa9'

old = "    def write(self, vals):\n        if any(k in vals for k in ['wuchang_store_mode']):"
new = f'''    def write(self, vals):
        if 'wuchang_store_mode' in vals and vals['wuchang_store_mode'] == 'fund':
            for config in self:
                if '{kw}' not in config.name:
                    raise ValidationError('{err}')

        if any(k in vals for k in ['wuchang_store_mode']):'''

if old in c:
    c = c.replace(old, new)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(c)
    print('OK')
else:
    print('Not found')
