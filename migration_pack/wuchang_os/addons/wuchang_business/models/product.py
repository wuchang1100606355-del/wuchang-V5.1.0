# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WuchangProduct(models.Model):
    _inherit = 'product.template'

    wuchang_story = fields.Text(string="五常故事", help="產品背後的社區故事或製作工藝")
    is_wuchang_signature = fields.Boolean(string="五常招牌", default=False)
