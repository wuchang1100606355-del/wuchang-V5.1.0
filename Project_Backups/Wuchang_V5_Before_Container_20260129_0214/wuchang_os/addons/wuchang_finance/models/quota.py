from odoo import models, fields, api


class WuchangFinanceQuota(models.Model):
    _name = 'wuchang.finance.quota'
    _description = 'Finance Credit Quota'

    name = fields.Char(required=True)
    program = fields.Selection([
        ('nonprofit', '非營利'),
        ('startup', '新創'),
        ('trial', '試用期'),
    ], required=True)
    monthly_limit = fields.Float(default=0.0)
    used_amount = fields.Float(default=0.0)
    remaining_amount = fields.Float(compute='_compute_remaining', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    billing_account = fields.Char()
    project_id = fields.Char()
    status = fields.Selection([
        ('ok', '正常'),
        ('not_configured', '未設定'),
        ('error', '錯誤'),
    ], default='not_configured')
    last_update = fields.Datetime()
    source = fields.Selection([
        ('manual', '手動'),
        ('gcp', 'GCP API'),
    ], default='manual')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    assigned_user_id = fields.Many2one('res.users', string='分配給', help="此額度指定的受益人或管理者")

    @api.depends('monthly_limit', 'used_amount')
    def _compute_remaining(self):
        for r in self:
            try:
                r.remaining_amount = max(0.0, (r.monthly_limit or 0.0) - (r.used_amount or 0.0))
            except Exception:
                r.remaining_amount = 0.0

    @api.model
    def ensure_default_records(self):
        params = self.env['ir.config_parameter'].sudo()
        cur = self.env.company.currency_id
        np = self.search([('program', '=', 'nonprofit'), ('company_id', '=', self.env.company.id)], limit=1)
        if not np:
            lim = float(params.get_param('gcp.quota.nonprofit.limit', '0') or '0')
            self.create({
                'name': '非營利額度',
                'program': 'nonprofit',
                'monthly_limit': lim,
                'currency_id': cur.id,
                'status': 'not_configured',
            })
        st = self.search([('program', '=', 'startup'), ('company_id', '=', self.env.company.id)], limit=1)
        if not st:
            lim = float(params.get_param('gcp.quota.startup.limit', '0') or '0')
            self.create({
                'name': '新創額度',
                'program': 'startup',
                'monthly_limit': lim,
                'currency_id': cur.id,
                'status': 'not_configured',
            })
        tr = self.search([('program', '=', 'trial'), ('company_id', '=', self.env.company.id)], limit=1)
        if not tr:
            lim = float(params.get_param('gcp.quota.trial.limit', '0') or '0')
            self.create({
                'name': '試用期額度',
                'program': 'trial',
                'monthly_limit': lim,
                'currency_id': cur.id,
                'status': 'not_configured',
            })

    def action_refresh(self):
        params = self.env['ir.config_parameter'].sudo()
        now = fields.Datetime.now()
        for r in self:
            try:
                if r.program == 'nonprofit':
                    used = float(params.get_param('gcp.monthly_spend.nonprofit', '0') or '0')
                    lim = float(params.get_param('gcp.quota.nonprofit.limit', str(r.monthly_limit or 0.0)) or '0')
                elif r.program == 'startup':
                    used = float(params.get_param('gcp.monthly_spend.startup', '0') or '0')
                    lim = float(params.get_param('gcp.quota.startup.limit', str(r.monthly_limit or 0.0)) or '0')
                else:
                    used = float(params.get_param('gcp.monthly_spend.trial', '0') or '0')
                    lim = float(params.get_param('gcp.quota.trial.limit', str(r.monthly_limit or 0.0)) or '0')
                r.write({
                    'used_amount': used,
                    'monthly_limit': lim,
                    'last_update': now,
                    'status': 'ok',
                    'source': 'manual',
                })
            except Exception:
                r.write({'status': 'error', 'last_update': now})

