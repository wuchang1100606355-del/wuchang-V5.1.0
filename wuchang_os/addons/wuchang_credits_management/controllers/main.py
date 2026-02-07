# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class CreditsManagementController(http.Controller):

    @http.route('/credits/double_j_configure', type='http', auth='user', methods=['POST'])
    def double_j_configure(self, credit_id, **kwargs):
        """雙J協作配置端點"""
        credit = request.env['wuchang.gcp.credits'].browse(int(credit_id))
        if credit.exists():
            credit.action_configure_with_double_j()
            return request.redirect('/web#id=%s&model=wuchang.gcp.credits&view_type=form' % credit_id)
        return request.not_found()
