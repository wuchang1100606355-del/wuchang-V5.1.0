from odoo import models, fields, api

class PropertyMaintenance(models.Model):
    _name = 'wuchang.property.maintenance'
    _description = 'Property Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Subject', required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1')
    
    category = fields.Selection([
        ('public', 'Public Area'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('structural', 'Structural'),
        ('other', 'Other')
    ], string='Category', required=True)
    
    location = fields.Char(string='Location/Unit')
    reporter_id = fields.Many2one('res.partner', string='Reporter')
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    
    def action_submit(self):
        self.write({'state': 'submitted'})
        
    def action_assign(self):
        self.write({'state': 'in_progress'})
        
    def action_done(self):
        self.write({'state': 'done'})
        
    def action_cancel(self):
        self.write({'state': 'cancelled'})
