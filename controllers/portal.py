# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class EstatePortal(http.Controller):
    
    @http.route(['/my/home'], type='http', auth="user", website=True)
    def portal_home(self, **kw):
        """住戶首頁：整合各項功能入口"""
        values = {
            'parcel_count': request.env['estate.parcel'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('state', 'in', ['arrived', 'notified'])
            ]),
            'meeting_count': request.env['estate.meeting'].search_count([
                ('state', 'in', ['scheduled', 'in_progress'])
            ]),
            'workorder_count': request.env['estate.workorder'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('state', 'not in', ['done', 'cancel'])
            ])
        }
        return request.render("wuchang_property_toolkits.portal_my_home", values)

    @http.route(['/my/parcels'], type='http', auth="user", website=True)
    def portal_my_parcels(self, **kw):
        """我的包裹"""
        parcels = request.env['estate.parcel'].search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ], order='arrival_time desc')
        return request.render("wuchang_property_toolkits.portal_my_parcels", {'parcels': parcels})

    @http.route(['/my/facilities'], type='http', auth="user", website=True)
    def portal_facilities(self, **kw):
        """公設預約頁面"""
        facilities = request.env['estate.facility'].search([])
        return request.render("wuchang_property_toolkits.portal_facilities", {'facilities': facilities})

    @http.route(['/my/facility/book'], type='http', auth="user", methods=['POST'], website=True)
    def portal_facility_book(self, **kw):
        """執行預約"""
        facility_id = int(kw.get('facility_id'))
        start_time = kw.get('start_time') # 格式: 2024-01-27 10:00:00
        end_time = kw.get('end_time')
        
        request.env['estate.facility.booking'].create({
            'facility_id': facility_id,
            'partner_id': request.env.user.partner_id.id,
            'start_time': start_time,
            'end_time': end_time
        })
        return request.redirect('/my/facilities?success=True')
