# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EstateWorkorder(models.Model):
    _name = 'estate.workorder'
    _description = '報修工單'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='工單編號', default='New', readonly=True)
    title = fields.Char(string='主旨', required=True)
    description = fields.Text(string='問題描述')
    
    # 報修來源
    partner_id = fields.Many2one('res.partner', string='報修人')
    unit_number = fields.Char(related='partner_id.unit_number', string='戶號')
    
    # 智生活沒有的功能：自動化來源
    source = fields.Selection([
        ('resident', '住戶報修'),
        ('staff', '物業巡檢'),
        ('iot', 'IoT 自動告警') # 例如：水泵異常自動發單
    ], string='來源', default='resident', required=True)

    # 處理進度
    priority = fields.Selection([
        ('0', '低'),
        ('1', '中'),
        ('2', '高'),
        ('3', '緊急')
    ], string='優先級', default='1')
    
    state = fields.Selection([
        ('draft', '草稿'),
        ('assigned', '已派工'),
        ('in_progress', '維修中'),
        ('done', '已完工'),
        ('cancel', '已取消')
    ], string='狀態', default='draft', tracking=True)
    
    # 派工資訊
    assigned_to = fields.Many2one('res.partner', string='維修廠商/人員')
    scheduled_date = fields.Datetime(string='預計維修時間')
    
    # 完工驗收
    completion_date = fields.Datetime(string='完工時間')
    cost = fields.Float(string='維修費用')
    before_photo = fields.Binary(string='維修前照片')
    after_photo = fields.Binary(string='維修後照片')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('estate.workorder') or 'New'
        return super(EstateWorkorder, self).create(vals)

    def action_assign(self):
        """派工"""
        self.ensure_one()
        self.state = 'assigned'
        # 發送通知給廠商

    def action_start(self):
        """開始維修"""
        self.ensure_one()
        self.state = 'in_progress'

    def action_done(self):
        """完工"""
        self.ensure_one()
        self.state = 'done'
        self.completion_date = fields.Datetime.now()
        # 通知住戶評分
