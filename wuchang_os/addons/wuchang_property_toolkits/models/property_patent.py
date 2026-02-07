from odoo import models, fields, api

class PropertyPatent(models.Model):
    _name = 'wuchang.property.patent'
    _description = 'Property System Patents'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Patent Title', required=True, tracking=True)
    patent_number = fields.Char(string='Patent Number', required=True, tracking=True)
    patent_type = fields.Selection([
        ('invention', 'Invention'),
        ('utility', 'Utility Model'),
        ('design', 'Design')
    ], string='Patent Type', default='utility')
    
    applicant = fields.Char(string='Applicant/Owner')
    application_date = fields.Date(string='Application Date')
    approval_date = fields.Date(string='Approval Date')
    
    description = fields.Text(string='Description/Abstract')
    
    # Link to the file (stored as attachment usually, but here we can just track metadata or upload)
    patent_file = fields.Binary(string='Patent Document')
    patent_filename = fields.Char(string='Filename')
    
    # Patent Image/Diagram (Important as per user request)
    patent_image = fields.Image(string='Patent Diagram', max_width=1024, max_height=1024)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired')
    ], string='Status', default='draft', tracking=True)

    def action_activate(self):
        self.state = 'active'
