# -*- coding: utf-8 -*-
from odoo import models, fields, api
import uuid
import qrcode
import base64
from io import BytesIO

class EstateVisitor(models.Model):
    _name = 'estate.visitor'
    _description = '訪客與門禁管理'
    _inherit = ['mail.thread']

    name = fields.Char(string='訪客姓名', required=True)
    host_partner_id = fields.Many2one('res.partner', string='受訪住戶', required=True)
    visit_time = fields.Datetime(string='預計到訪時間', required=True)
    leave_time = fields.Datetime(string='預計離開時間')
    
    # 通行憑證
    access_token = fields.Char(string='通行權杖', readonly=True)
    qr_code_image = fields.Binary(string='通行 QR Code', readonly=True)
    
    # 智生活沒有的功能：零信任門禁
    access_level = fields.Selection([
        ('lobby', '僅大廳'),
        ('elevator', '大廳+電梯'),
        ('full', '全區通行')
    ], string='通行權限', default='elevator')
    
    state = fields.Selection([
        ('draft', '預登記'),
        ('approved', '已授權'),
        ('arrived', '已進入'),
        ('left', '已離開'),
        ('expired', '已過期')
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals):
        vals['access_token'] = str(uuid.uuid4())
        record = super(EstateVisitor, self).create(vals)
        record._generate_qr_code()
        return record

    def _generate_qr_code(self):
        """生成具時效性的 QR Code"""
        for record in self:
            if record.access_token:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                # QR 內容包含：Token + 時效 + 權限
                data = f"WUCHANG|{record.access_token}|{record.visit_time}"
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                record.qr_code_image = base64.b64encode(buffer.getvalue())

    def action_approve(self):
        """住戶同意並發送 QR Code"""
        self.ensure_one()
        self.state = 'approved'
        # 發送 QR Code 給訪客 (Line/Email)
        message = "您的訪客通行證已生成，請於到訪時出示 QR Code。"
        self.message_post(body=message)

    def action_scan_entry(self):
        """模擬門禁掃描進入"""
        self.ensure_one()
        self.state = 'arrived'
        # 觸發門禁控制器開門
        print(f"Door Access Granted: {self.name} -> Level {self.access_level}")
