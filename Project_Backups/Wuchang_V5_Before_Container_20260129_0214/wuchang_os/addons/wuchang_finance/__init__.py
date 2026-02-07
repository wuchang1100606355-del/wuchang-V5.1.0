from . import models

def post_init_hook(cr, registry):
    from odoo.api import Environment
    env = Environment(cr, 1, {})
    env['wuchang.finance.quota'].sudo().ensure_default_records()
