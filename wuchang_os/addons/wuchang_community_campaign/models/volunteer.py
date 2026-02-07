from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VolunteerTask(models.Model):
    _name = 'wuchang.volunteer.task'
    _description = '志工任務'

    name = fields.Char('任務名稱', required=True)
    description = fields.Text('任務說明')
    date_start = fields.Datetime('開始時間', default=fields.Datetime.now)
    date_end = fields.Datetime('結束時間')
    required_people = fields.Integer('需求人數', default=1)
    coins_reward = fields.Integer('獎勵幸福幣', default=50)

    is_special_squad = fields.Boolean('專勤隊任務', default=False)
    
    def action_assign_to_squad(self):
        # 專勤隊指派邏輯
        self.write({'is_special_squad': True})
        return True
    
    state = fields.Selection([
        ('draft', '草稿'),
        ('open', '招募中'),
        ('full', '額滿'),
        ('done', '已結束'),
        ('cancelled', '已取消')
    ], string='狀態', default='draft', required=True)

    volunteer_ids = fields.One2many('wuchang.volunteer.signup', 'task_id', string='報名志工')

    def action_publish(self):
        self.write({'state': 'open'})

    def action_close(self):
        self.write({'state': 'done'})
        # 發放獎勵
        for signup in self.volunteer_ids.filtered(lambda s: s.state == 'attended'):
            signup.partner_id.sudo().write({
                'whc_wallet_balance': signup.partner_id.whc_wallet_balance + self.coins_reward
            })
            # 記錄交易 (需依賴 wuchang_finance)
            self.env['wuchang.coin.transaction'].create({
                'dest_partner_id': signup.partner_id.id,
                'amount': self.coins_reward,
                'transaction_type': 'reward',
                'description': f'志工任務獎勵: {self.name}'
            })

class VolunteerSignup(models.Model):
    _name = 'wuchang.volunteer.signup'
    _description = '志工報名記錄'

    task_id = fields.Many2one('wuchang.volunteer.task', string='任務', required=True)
    partner_id = fields.Many2one('res.partner', string='志工', required=True)
    signup_date = fields.Datetime('報名時間', default=fields.Datetime.now)
    state = fields.Selection([
        ('signed_up', '已報名'),
        ('attended', '已出席'),
        ('absent', '缺席')
    ], string='狀態', default='signed_up')

    _sql_constraints = [
        ('unique_signup', 'unique(task_id, partner_id)', '您已經報名過此任務！')
    ]


