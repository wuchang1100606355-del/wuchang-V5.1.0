# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import datetime

class EstateDocument(models.Model):
    _name = 'estate.document'
    _description = '五常公文與法務系統'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='主旨', required=True)
    doc_number = fields.Char(string='發文字號', readonly=True, copy=False, default='尚未編碼')
    
    doc_type = fields.Selection([
        ('announcement', '內部公告'),
        ('official_letter', '對外公函'),
        ('legal_attest', '存證信函'),
        ('court_order', '支付命令'),
        ('petition', '陳情書')
    ], string='公文類型', required=True)
    
    # 受文者
    recipient_partner_id = fields.Many2one('res.partner', string='受文者 (個人/單位)')
    recipient_text = fields.Char(string='受文者 (自訂)', help="若受文者不在系統中可手動輸入")
    
    # 內容生成
    template_id = fields.Many2one('estate.document.template', string='套用模板')
    body_html = fields.Html(string='公文內容')
    
    # 流程狀態
    state = fields.Selection([
        ('draft', '草稿'),
        ('review', '主委審核中'),
        ('approved', '已核准'),
        ('sent', '已發送/交寄'),
        ('delivered', '已送達/回執'),
        ('closed', '結案')
    ], string='狀態', default='draft', tracking=True)
    
    # 證據與附件
    attachment_ids = fields.Many2many('ir.attachment', string='附件')
    delivery_proof = fields.Binary(string='送達回執/掛號單', attachment=True)
    
    # 關聯
    source_resolution_id = fields.Many2one('estate.meeting.resolution', string='來源決議')

    @api.onchange('template_id')
    def _onchange_template(self):
        """套用模板內容"""
        if self.template_id:
            self.body_html = self.template_id.content_html

    def action_generate_number(self):
        """生成發文字號 (如：113常勝字第001號)"""
        self.ensure_one()
        year = datetime.date.today().year - 1911 # 民國年
        seq = self.env['ir.sequence'].next_by_code('estate.document') or '000'
        self.doc_number = f"{year}常勝字第{seq}號"

    def action_submit(self):
        """提交審核"""
        self.ensure_one()
        self.state = 'review'
        # 通知主委審核
    
    def action_approve(self):
        """主委核准並生成 PDF"""
        self.ensure_one()
        if self.doc_number == '尚未編碼':
            self.action_generate_number()
        self.state = 'approved'
        # TODO: 呼叫報表引擎生成 PDF
    
    def action_send_post(self):
        """串接郵局 API 或標記已寄出"""
        self.ensure_one()
        self.state = 'sent'

class EstateDocumentTemplate(models.Model):
    _name = 'estate.document.template'
    _description = '公文模板庫'

    name = fields.Char(string='模板名稱', required=True)
    doc_type = fields.Selection([
        ('announcement', '內部公告'),
        ('official_letter', '對外公函'),
        ('legal_attest', '存證信函'),
        ('court_order', '支付命令')
    ], string='適用類型')
    
    content_html = fields.Html(string='模板內容 (支援 Jinja2)', help="可使用 {{ object.partner_id.name }} 等變數")
    active = fields.Boolean(default=True)
