# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class WuchangDocumentTemplate(models.Model):
    _name = 'wuchang.document.template'
    _description = '公文範本'
    _order = 'organization_type, document_type, name'

    name = fields.Char('範本名稱', required=True)
    document_type = fields.Selection([
        ('announcement', '公告'),
        ('notice', '通知'),
        ('resolution', '決議'),
        ('report', '報告'),
        ('authorization', '授權書'),
        ('other', '其他'),
    ], string='公文類型', required=True)
    
    # 組織類型：區分不同單位
    organization_type = fields.Selection([
        ('association', '社區發展協會'),
        ('committee', '管委會'),
        ('other', '其他'),
    ], string='組織類型', required=True, default='association', tracking=True)
    
    organization = fields.Char('組織名稱', default='新北市三重區五常社區發展協會', required=True)
    template_content = fields.Html('範本內容', required=True)
    
    description = fields.Text('範本說明')
    is_active = fields.Boolean('啟用', default=True)
    
    # 使用統計
    usage_count = fields.Integer('使用次數', default=0, readonly=True)
    last_used_date = fields.Datetime('最後使用時間', readonly=True)
    
    def action_use_template(self):
        """使用範本（增加使用次數）"""
        for record in self:
            from odoo import fields as odoo_fields
            record.write({
                'usage_count': record.usage_count + 1,
                'last_used_date': odoo_fields.Datetime.now(),
            })
    
    def render_template(self, context=None):
        """渲染範本內容"""
        self.ensure_one()
        context = context or {}
        
        # 預設值
        defaults = {
            'organization': self.organization,
            'year': datetime.now().strftime('%Y'),
            'month': datetime.now().strftime('%m'),
            'day': datetime.now().strftime('%d'),
            'sign_date': datetime.now().strftime('%Y 年 %m 月 %d 日'),
            'doc_number': self._generate_doc_number(),
        }
        
        # 合併上下文
        render_context = {**defaults, **context}
        
        # 替換範本中的變數
        content = self.template_content
        for key, value in render_context.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        return content
    
    def _generate_doc_number(self):
        """產生文件編號"""
        # 格式：組織簡稱-類型-年月日-序號
        org_abbr = 'WCH'
        type_code = {
            'announcement': 'ANN',
            'notice': 'NOT',
            'resolution': 'RES',
            'report': 'RPT',
            'authorization': 'AUT',
            'other': 'OTH',
        }.get(self.document_type, 'OTH')
        
        date_str = datetime.now().strftime('%Y%m%d')
        return f"{org_abbr}-{type_code}-{date_str}-001"
