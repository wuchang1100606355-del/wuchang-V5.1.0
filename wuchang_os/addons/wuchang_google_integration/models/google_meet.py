# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class WuchangGoogleMeet(models.Model):
    _name = 'wuchang.google.meet'
    _description = 'Google Meet 會議整合'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('會議名稱', required=True, tracking=True)
    calendar_event_id = fields.Many2one('calendar.event', 'Odoo 會議', ondelete='cascade')
    google_meet_link = fields.Char('Google Meet 連結', readonly=True, tracking=True)
    google_calendar_id = fields.Char('Google Calendar ID', readonly=True)
    google_event_id = fields.Char('Google Event ID', readonly=True)
    
    # 會議時間
    start_datetime = fields.Datetime('開始時間', required=True, tracking=True)
    end_datetime = fields.Datetime('結束時間', required=True, tracking=True)
    
    # 參與者
    partner_ids = fields.Many2many('res.partner', string='參與者', tracking=True)
    organizer_id = fields.Many2one('res.users', '會議主持人', default=lambda self: self.env.user, required=True)
    
    # 會議狀態
    state = fields.Selection([
        ('draft', '草稿'),
        ('scheduled', '已排程'),
        ('in_progress', '進行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ], string='狀態', default='draft', tracking=True)
    
    # Google Meet 設定
    auto_join_enabled = fields.Boolean('自動加入 Meet', default=True)
    recording_enabled = fields.Boolean('啟用錄影', default=False)
    recording_url = fields.Char('錄影連結', readonly=True)
    
    # 其他資訊
    description = fields.Text('會議描述')
    notes = fields.Text('會議記錄')
    
    @api.model
    def create(self, vals):
        """創建 Google Meet 會議"""
        record = super(WuchangGoogleMeet, self).create(vals)
        if record.auto_join_enabled:
            record.action_create_google_meet()
        return record
    
    def action_create_google_meet(self):
        """建立 Google Meet 連結"""
        for record in self:
            try:
                # TODO: 實作 Google Calendar API 呼叫
                # 這裡需要整合 Google Calendar API 來建立 Google Meet 連結
                
                # 暫時產生一個範例連結
                # 實際實作時應該呼叫 Google Calendar API
                meet_link = f"https://meet.google.com/{self._generate_meet_code()}"
                
                record.write({
                    'google_meet_link': meet_link,
                    'state': 'scheduled',
                })
                
                # 建立對應的 Odoo 日曆事件
                calendar_event = self.env['calendar.event'].create({
                    'name': record.name,
                    'start': record.start_datetime,
                    'stop': record.end_datetime,
                    'description': record.description or '',
                    'partner_ids': [(6, 0, record.partner_ids.ids)],
                    'user_id': record.organizer_id.id,
                })
                
                record.write({'calendar_event_id': calendar_event.id})
                
                _logger.info(f"Google Meet 會議已建立: {record.name}")
                
            except Exception as e:
                _logger.error(f"建立 Google Meet 會議失敗: {str(e)}")
                raise UserError(f"建立 Google Meet 會議失敗: {str(e)}")
    
    def _generate_meet_code(self):
        """產生 Google Meet 會議代碼（範例實作）"""
        import random
        import string
        # 實際應該由 Google Calendar API 回傳
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    
    def action_start_meeting(self):
        """開始會議"""
        for record in self:
            record.write({'state': 'in_progress'})
    
    def action_complete_meeting(self):
        """完成會議"""
        for record in self:
            record.write({'state': 'completed'})
            # TODO: 取得錄影連結（如果有啟用錄影）
    
    def action_cancel_meeting(self):
        """取消會議"""
        for record in self:
            record.write({'state': 'cancelled'})
            # TODO: 取消 Google Calendar 事件
    
    def action_open_google_meet(self):
        """開啟 Google Meet 連結"""
        self.ensure_one()
        if not self.google_meet_link:
            raise UserError('尚未建立 Google Meet 連結')
        return {
            'type': 'ir.actions.act_url',
            'url': self.google_meet_link,
            'target': 'new',
        }


# 擴展 calendar.event 模型以支援 Google Meet
class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    google_meet_id = fields.Many2one('wuchang.google.meet', 'Google Meet 會議', ondelete='set null')
    google_meet_link = fields.Char(related='google_meet_id.google_meet_link', string='Google Meet 連結', readonly=True)
    
    def action_create_google_meet(self):
        """從日曆事件建立 Google Meet 會議"""
        for event in self:
            meet = self.env['wuchang.google.meet'].create({
                'name': event.name,
                'calendar_event_id': event.id,
                'start_datetime': event.start,
                'end_datetime': event.stop,
                'description': event.description,
                'partner_ids': [(6, 0, event.partner_ids.ids)],
                'organizer_id': event.user_id.id,
            })
            event.write({'google_meet_id': meet.id})
            meet.action_create_google_meet()
            return meet
