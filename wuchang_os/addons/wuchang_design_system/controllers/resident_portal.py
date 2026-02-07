# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ResidentPortal(http.Controller):

    @http.route('/resident/home', type='http', auth='user', website=True)
    def resident_home(self, **kwargs):
        """住戶專屬入口網首頁"""
        user = request.env.user
        partner = user.partner_id
        
        # 嘗試查找關聯的戶別 (目前依賴名稱匹配，未來建議在 property.unit 增加 partner_id 關聯)
        unit = request.env['wuchang.property.unit'].sudo().search([
            ('owner_name', '=', partner.name)
        ], limit=1)
        
        # 獲取最新公告
        announcements = request.env['community.bulletin'].sudo().search([
            ('active', '=', True)
        ], limit=5, order='date_published desc')
        
        # 獲取待處理事項 (模擬數據，未來接真實模型)
        # 例如：未領包裹、待繳管理費
        notifications = []
        if unit:
            # TODO: 查詢包裹
            pass
            
        values = {
            'user': user,
            'partner': partner,
            'unit': unit,
            'announcements': announcements,
            'notifications': notifications,
        }
        return request.render('wuchang_design_system.resident_portal_home', values)

    @http.route('/resident/wallet', type='http', auth='user', website=True)
    def resident_wallet(self, **kwargs):
        """住戶錢包與會計小幫手"""
        user = request.env.user
        
        # 查詢發票紀錄
        invoices = request.env['wuchang.personal.invoice'].search([
            ('user_id', '=', user.id)
        ], order='date desc', limit=20)
        
        # 簡單統計本月支出
        # 實際應用應使用 SQL group by 或 read_group
        total_expense = sum(inv.amount for inv in invoices)
        
        values = {
            'user': user,
            'invoices': invoices,
            'total_expense': total_expense,
        }
        return request.render('wuchang_design_system.resident_wallet_page', values)

    @http.route(['/map-3d-viewer'], type='http', auth="public", website=True)
    def map_3d_viewer(self, **kw):
        """Serve the 3D Map Viewer HTML file"""
        import os
        # Path to the file we created in wuchang-V5.1.0
        # Note: In a real addon, this should be in static/src or similar, but we follow the user's structure
        # We need to find where wuchang-V5.1.0 is relative to this file
        # This file: addons/wuchang_design_system/controllers/resident_portal.py
        # Root: c:\wuchang V5.1.0\
        # Map file: c:\wuchang V5.1.0\wuchang-V5.1.0\map_3d_viewer.html
        
        # Calculating path... this is tricky in Odoo execution context.
        # But we can try absolute path or relative from current file.
        # current file dir: .../controllers
        # .../addons/wuchang_design_system/controllers
        # .../wuchang_os/addons/...
        # .../wuchang V5.1.0/wuchang_os/addons/...
        
        # Let's try to locate it safely
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        map_path = os.path.join(base_path, 'wuchang-V5.1.0', 'map_3d_viewer.html')
        
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "3D Map Viewer not found at expected path: " + map_path

