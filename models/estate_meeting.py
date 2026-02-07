# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import json

class EstateMeeting(models.Model):
    _name = 'estate.meeting'
    _description = '五常會議系統'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='會議主題', required=True)
    meeting_type = fields.Selection([
        ('committee', '管理委員會'),
        ('owner', '區分所有權人會議'),
        ('temp', '臨時動議')
    ], string='會議類型', required=True, default='committee')
    
    start_datetime = fields.Datetime(string='開始時間', required=True)
    end_datetime = fields.Datetime(string='結束時間')
    location = fields.Char(string='地點', default='社區會議室')
    
    # 參與者
    attendee_ids = fields.Many2many('res.partner', string='出席人員')
    absent_ids = fields.Many2many('res.partner', 'meeting_absent_rel', string='缺席人員')
    
    # 議程與決議
    resolution_ids = fields.One2many('estate.meeting.resolution', 'meeting_id', string='會議決議')
    
    state = fields.Selection([
        ('draft', '草稿'),
        ('scheduled', '已排程'),
        ('in_progress', '進行中'),
        ('done', '已結束'),
        ('closed', '已歸檔')
    ], string='狀態', default='draft', tracking=True)

    def action_start_meeting(self):
        """開始會議：啟動錄音與 AI 助理"""
        self.ensure_one()
        self.state = 'in_progress'
        # TODO: 呼叫 Whisper API 開始錄音
        return True

    def action_close_meeting(self):
        """結束會議：生成會議記錄並執行決議"""
        self.ensure_one()
        self.state = 'done'
        self.end_datetime = fields.Datetime.now()
        # 自動執行所有標記為「立即執行」的決議
        for resolution in self.resolution_ids:
            if resolution.auto_execute:
                resolution.action_execute()

class EstateMeetingResolution(models.Model):
    _name = 'estate.meeting.resolution'
    _description = '會議決議 (Code as Law)'
    _inherit = ['mail.thread']

    name = fields.Char(string='決議標題', required=True)
    meeting_id = fields.Many2one('estate.meeting', string='所屬會議', ondelete='cascade')
    
    # 決議內容
    description = fields.Text(string='決議內容說明')
    vote_result = fields.Char(string='表決結果') # 例如：5票同意/0票反對
    
    # 專利核心：決議即執行
    resolution_type = fields.Selection([
        ('fee_change', '費用調整'),
        ('maintenance', '修繕工程'),
        ('rule_change', '規約變更'),
        ('legal_action', '法務行動'),
        ('general', '一般事項')
    ], string='決議類型', required=True)
    
    # 自動化參數 (JSON 格式)
    execution_params = fields.Text(string='執行參數 (JSON)', default='{}', help='例如: {"amount": 1000, "target": "all"}')
    auto_execute = fields.Boolean(string='會議結束後自動執行', default=False)
    
    state = fields.Selection([
        ('draft', '草稿'),
        ('approved', '已通過'),
        ('rejected', '未通過'),
        ('executed', '已執行'),
        ('failed', '執行失敗')
    ], string='狀態', default='draft', tracking=True)

    execution_log = fields.Text(string='執行日誌')

    def action_execute(self):
        """執行決議引擎"""
        self.ensure_one()
        if self.state != 'approved':
            raise exceptions.UserError('僅有「已通過」的決議可以執行。')

        try:
            params = json.loads(self.execution_params)
            
            if self.resolution_type == 'fee_change':
                self._execute_fee_change(params)
            elif self.resolution_type == 'maintenance':
                self._execute_maintenance(params)
            elif self.resolution_type == 'legal_action':
                self._execute_legal_action(params)
            
            self.state = 'executed'
            self.execution_log = f"執行成功於 {fields.Datetime.now()}"
        
        except Exception as e:
            self.state = 'failed'
            self.execution_log = f"執行失敗: {str(e)}"

    def _execute_fee_change(self, params):
        """執行管理費調整邏輯"""
        # 範例：調用會計模組 API
        # self.env['account.move'].update_recurring_fees(...)
        pass

    def _execute_maintenance(self, params):
        """自動生成工單"""
        self.env['estate.workorder'].create({
            'title': f"決議執行：{self.name}",
            'description': self.description,
            'source': 'iot', # 標記為系統生成
            'priority': '2'
        })

    def _execute_legal_action(self, params):
        """觸發法務公文"""
        # 範例：生成存證信函
        # self.env['estate.document'].create_legal_doc(...)
        pass
