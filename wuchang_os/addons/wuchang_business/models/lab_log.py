# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WuchangLabLog(models.Model):
    _name = 'wuchang.lab.log'
    _description = '五常實驗室研發日誌'
    _order = 'discovery_date desc'

    name = fields.Char(string="研發代號", required=True)
    discovery_date = fields.Date(
        string="突破日期", default=fields.Date.context_today)

    # 人腦的創意 (Human Creativity)
    problem_statement = fields.Text(string="創意原點 (Human Constraint)",
                                    help="人類提出的核心創意或嚴苛限制條件")

    # 電腦的算力 (Computer Computing Power)
    ai_solution = fields.Text(string="算力破解 (AI Solution)",
                              help="AI 透過全球運算與資料庫檢索找到的科學解答")

    scientific_basis = fields.Text(string="科學原理 (Scientific Basis)",
                                   help="支撐該解決方案的物理或化學原理")

    related_product_id = fields.Many2one('product.template', string="應用產品")
