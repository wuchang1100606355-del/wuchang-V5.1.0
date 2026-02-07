# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class GCPCredits(models.Model):
    _name = 'wuchang.gcp.credits'
    _description = 'Google Cloud Platform 抵免額管理'
    _order = 'expiry_date desc'

    name = fields.Char('抵免額名稱', required=True)
    credit_type = fields.Selection([
        ('free_trial', '免費試用抵免額'),
        ('maps_platform', 'Google Maps Platform 非營利抵免額'),
        ('nonprofit', 'Google Cloud 非營利抵免額'),
    ], string='抵免額類型', required=True)
    
    credit_id = fields.Char('抵免額 ID', help='Google Cloud 抵免額唯一識別碼')
    amount = fields.Float('金額 (USD)', required=True, digits=(16, 2))
    used_amount = fields.Float('已使用金額', digits=(16, 2), default=0.0)
    remaining_amount = fields.Float('剩餘金額', compute='_compute_remaining', store=True)
    
    monthly_amount = fields.Float('每月額度 (USD)', help='如果是每月重置的抵免額')
    is_monthly = fields.Boolean('每月重置', default=False)
    
    start_date = fields.Date('開始日期', required=True, default=fields.Date.today)
    expiry_date = fields.Date('到期日期')
    days_remaining = fields.Integer('剩餘天數', compute='_compute_days_remaining')
    
    project_id = fields.Char('專案 ID', default='my-j-483304')
    status = fields.Selection([
        ('active', '使用中'),
        ('expired', '已到期'),
        ('pending', '待審核'),
        ('exhausted', '已用完'),
    ], string='狀態', compute='_compute_status', store=True)
    
    applicable_services = fields.Text('適用服務')
    notes = fields.Text('備註')
    
    # 雙J協作相關
    little_j_task_id = fields.Many2one('wuchang.double.j.task', '小J 任務')
    jules_task_id = fields.Many2one('wuchang.double.j.task', 'Jules 任務')
    collaboration_status = fields.Selection([
        ('pending', '待處理'),
        ('little_j_processing', '小J 處理中'),
        ('jules_processing', 'Jules 處理中'),
        ('completed', '已完成'),
        ('failed', '失敗'),
    ], string='協作狀態', default='pending')
    
    usage_log_ids = fields.One2many('wuchang.credits.usage.log', 'credit_id', '使用記錄')
    
    @api.depends('amount', 'used_amount')
    def _compute_remaining(self):
        for record in self:
            record.remaining_amount = record.amount - record.used_amount
    
    @api.depends('expiry_date')
    def _compute_days_remaining(self):
        for record in self:
            if record.expiry_date:
                delta = fields.Date.from_string(record.expiry_date) - fields.Date.today()
                record.days_remaining = delta.days
            else:
                record.days_remaining = 999
    
    @api.depends('expiry_date', 'remaining_amount', 'used_amount')
    def _compute_status(self):
        today = fields.Date.today()
        for record in self:
            if record.expiry_date and fields.Date.from_string(record.expiry_date) < today:
                record.status = 'expired'
            elif record.remaining_amount <= 0:
                record.status = 'exhausted'
            elif record.credit_type == 'nonprofit' and record.status == 'pending':
                record.status = 'pending'
            else:
                record.status = 'active'
    
    def action_configure_with_double_j(self):
        """使用雙J協作機制配置抵免額應用"""
        self.ensure_one()
        
        # 建立小J任務（本地處理）
        little_j_task = self.env['wuchang.double.j.task'].create({
            'name': f'配置 {self.name} 抵免額應用 - 本地處理',
            'agent': 'little_j',
            'task_type': 'credits_configuration',
            'priority': 'high',
            'description': f'配置 {self.name} 的抵免額應用，金額: ${self.amount}',
            'status': 'assigned',
            'related_credit_id': self.id,
        })
        
        # 建立Jules任務（雲端處理）
        jules_task = self.env['wuchang.double.j.task'].create({
            'name': f'配置 {self.name} 抵免額應用 - 雲端處理',
            'agent': 'jules',
            'task_type': 'credits_configuration',
            'priority': 'high',
            'description': f'在雲端配置 {self.name} 的抵免額應用',
            'status': 'assigned',
            'related_credit_id': self.id,
        })
        
        self.write({
            'little_j_task_id': little_j_task.id,
            'jules_task_id': jules_task.id,
            'collaboration_status': 'little_j_processing',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': '雙J協作任務',
            'res_model': 'wuchang.double.j.task',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', [little_j_task.id, jules_task.id])],
        }


class CreditsUsageLog(models.Model):
    _name = 'wuchang.credits.usage.log'
    _description = '抵免額使用記錄'
    _order = 'usage_date desc'

    credit_id = fields.Many2one('wuchang.gcp.credits', '抵免額', required=True, ondelete='cascade')
    service_name = fields.Char('服務名稱', required=True)
    amount = fields.Float('使用金額 (USD)', required=True, digits=(16, 2))
    usage_date = fields.Datetime('使用時間', required=True, default=fields.Datetime.now)
    description = fields.Text('說明')
    agent = fields.Selection([
        ('little_j', '小J (本地)'),
        ('jules', 'Jules (雲端)'),
        ('system', '系統自動'),
    ], string='處理代理', default='system')
