# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EstateFacility(models.Model):
    _name = 'estate.facility'
    _description = '公設管理'

    name = fields.Char(string='公設名稱', required=True)
    code = fields.Char(string='代碼')
    facility_type = fields.Selection([
        ('ktv', 'KTV'),
        ('gym', '健身房'),
        ('pool', '游泳池'),
        ('meeting', '會議室'),
        ('reading', '閱覽室')
    ], string='類型', required=True)
    
    # 費率與規則
    points_cost = fields.Integer(string='每小時扣點', default=0)
    cash_cost = fields.Float(string='每小時費用', default=0.0)
    max_capacity = fields.Integer(string='最大容納人數')
    
    # 智生活沒有的功能：硬體連動
    iot_device_id = fields.Char(string='IoT 控制器 ID') # 用於控制電源
    
    booking_ids = fields.One2many('estate.facility.booking', 'facility_id', string='預約紀錄')

class EstateFacilityBooking(models.Model):
    _name = 'estate.facility.booking'
    _description = '公設預約'
    _inherit = ['mail.thread']

    name = fields.Char(string='預約單號', default='New', readonly=True)
    facility_id = fields.Many2one('estate.facility', string='公設', required=True)
    partner_id = fields.Many2one('res.partner', string='預約住戶', required=True)
    
    start_time = fields.Datetime(string='開始時間', required=True)
    end_time = fields.Datetime(string='結束時間', required=True)
    duration = fields.Float(string='時數', compute='_compute_duration', store=True)
    
    state = fields.Selection([
        ('draft', '草稿'),
        ('confirmed', '已預約'),
        ('checked_in', '使用中'),
        ('done', '已結束'),
        ('cancel', '已取消')
    ], default='draft', tracking=True)
    
    # 費用計算
    total_cost = fields.Float(string='總費用', compute='_compute_cost', store=True)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = delta.total_seconds() / 3600.0
            else:
                record.duration = 0.0

    @api.depends('duration', 'facility_id')
    def _compute_cost(self):
        for record in self:
            record.total_cost = record.duration * record.facility_id.cash_cost

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('estate.booking') or 'New'
        return super(EstateFacilityBooking, self).create(vals)

    def action_check_in(self):
        """住戶報到：啟動電源"""
        self.ensure_one()
        self.state = 'checked_in'
        # 觸發 IoT 開關
        if self.facility_id.iot_device_id:
            self._trigger_iot_power(self.facility_id.iot_device_id, 'ON')

    def action_check_out(self):
        """結束使用：切斷電源"""
        self.ensure_one()
        self.state = 'done'
        if self.facility_id.iot_device_id:
            self._trigger_iot_power(self.facility_id.iot_device_id, 'OFF')

    def _trigger_iot_power(self, device_id, action):
        """模擬 IoT 控制訊號"""
        # 實際實作會呼叫 MQTT 或 HTTP API
        print(f"IoT Command: Device {device_id} -> Power {action}")
