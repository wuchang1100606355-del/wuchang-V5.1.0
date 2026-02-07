# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class DoubleJTask(models.Model):
    _name = 'wuchang.double.j.task'
    _description = '雙J協作任務'
    _order = 'priority desc, create_date desc'

    name = fields.Char('任務名稱', required=True)
    agent = fields.Selection([
        ('little_j', '小J (本地)'),
        ('jules', 'Jules (雲端)'),
    ], string='負責代理', required=True)
    
    task_type = fields.Selection([
        ('credits_configuration', '抵免額配置'),
        ('cloud_deployment', '雲端部署'),
        ('llm_upgrade', 'LLM 升級'),
        ('system_maintenance', '系統維護'),
        ('other', '其他'),
    ], string='任務類型', required=True)
    
    priority = fields.Selection([
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '緊急'),
    ], string='優先級', default='medium', required=True)
    
    status = fields.Selection([
        ('pending', '待處理'),
        ('assigned', '已分配'),
        ('in_progress', '進行中'),
        ('completed', '已完成'),
        ('failed', '失敗'),
        ('cancelled', '已取消'),
    ], string='狀態', default='pending')
    
    description = fields.Text('任務描述')
    related_credit_id = fields.Many2one('wuchang.gcp.credits', '相關抵免額')
    
    assigned_date = fields.Datetime('分配時間')
    start_date = fields.Datetime('開始時間')
    completed_date = fields.Datetime('完成時間')
    deadline = fields.Datetime('截止時間')
    
    result = fields.Text('執行結果')
    error_message = fields.Text('錯誤訊息')
    
    collaborator_task_id = fields.Many2one('wuchang.double.j.task', '協作任務', 
                                          help='另一個代理的相關任務')
    
    @api.model
    def create(self, vals):
        if vals.get('status') == 'assigned' and not vals.get('assigned_date'):
            vals['assigned_date'] = fields.Datetime.now()
        return super().create(vals)
    
    def action_start(self):
        """開始執行任務"""
        self.write({
            'status': 'in_progress',
            'start_date': fields.Datetime.now(),
        })
    
    def action_complete(self, result=None):
        """完成任務"""
        self.write({
            'status': 'completed',
            'completed_date': fields.Datetime.now(),
            'result': result or '',
        })
    
    def action_fail(self, error_message=None):
        """任務失敗"""
        self.write({
            'status': 'failed',
            'error_message': error_message or '',
        })
