# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class WuchangGoogleDriveFile(models.Model):
    _name = 'wuchang.google.drive.file'
    _description = 'Google Drive 檔案整合'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('檔案名稱', required=True, tracking=True)
    google_file_id = fields.Char('Google Drive 檔案 ID', required=True, readonly=True)
    google_file_url = fields.Char('Google Drive 連結', compute='_compute_file_url', store=True)
    
    # 檔案類型
    file_type = fields.Selection([
        ('document', '文件'),
        ('spreadsheet', '試算表'),
        ('presentation', '簡報'),
        ('folder', '資料夾'),
        ('other', '其他'),
    ], string='檔案類型', required=True, tracking=True)
    
    # 檔案資訊
    mime_type = fields.Char('MIME 類型', readonly=True)
    file_size = fields.Integer('檔案大小 (bytes)', readonly=True)
    
    # 權限管理
    shared_with = fields.Many2many('res.partner', string='共用對象')
    permission_level = fields.Selection([
        ('viewer', '檢視者'),
        ('commenter', '評論者'),
        ('editor', '編輯者'),
        ('owner', '擁有者'),
    ], string='權限等級', default='viewer', tracking=True)
    
    # 同步狀態
    sync_state = fields.Selection([
        ('synced', '已同步'),
        ('pending', '待同步'),
        ('error', '同步錯誤'),
    ], string='同步狀態', default='pending', tracking=True)
    last_sync_date = fields.Datetime('最後同步時間', readonly=True)
    
    # 版本控制
    version = fields.Char('版本', readonly=True)
    
    # 建立者和建立時間
    create_uid = fields.Many2one('res.users', '建立者', readonly=True)
    create_date = fields.Datetime('建立時間', readonly=True)
    
    @api.depends('google_file_id')
    def _compute_file_url(self):
        for record in self:
            if record.google_file_id:
                if record.file_type == 'folder':
                    record.google_file_url = f"https://drive.google.com/drive/folders/{record.google_file_id}"
                else:
                    record.google_file_url = f"https://drive.google.com/file/d/{record.google_file_id}/view"
            else:
                record.google_file_url = False
    
    def action_sync_from_google_drive(self):
        """從 Google Drive 同步檔案資訊"""
        for record in self:
            try:
                # TODO: 實作 Google Drive API 呼叫
                # 同步檔案資訊（名稱、大小、版本等）
                
                record.write({
                    'sync_state': 'synced',
                    'last_sync_date': fields.Datetime.now(),
                })
                
                _logger.info(f"檔案已同步: {record.name}")
                
            except Exception as e:
                _logger.error(f"同步檔案失敗: {str(e)}")
                record.write({'sync_state': 'error'})
                raise UserError(f"同步檔案失敗: {str(e)}")
    
    def action_open_google_drive(self):
        """開啟 Google Drive 連結"""
        self.ensure_one()
        if not self.google_file_url:
            raise UserError('尚未建立 Google Drive 連結')
        return {
            'type': 'ir.actions.act_url',
            'url': self.google_file_url,
            'target': 'new',
        }
    
    def action_share_file(self):
        """共用檔案"""
        self.ensure_one()
        # TODO: 實作檔案共用功能
        return {
            'type': 'ir.actions.act_window',
            'name': '共用檔案',
            'res_model': 'wuchang.google.drive.file',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'default_google_file_id': self.google_file_id},
        }
