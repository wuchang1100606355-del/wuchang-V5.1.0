import os
from odoo import models, fields, api
import json

class AiGuard(models.Model):
    _inherit = 'wuchang.ai.hallucination.monitor'

    system_structure_index = fields.Text(string='System Structure Index', help='JSON map of all models and key fields.')
    last_index_time = fields.Datetime(string='Last Index Time')

    def action_build_system_index(self):
        """
        Scans ir.model to build a map of the system and stores it in system_structure_index.
        This serves as the 'Body Memory' map.
        """
        ir_models = self.env['ir.model'].search([])
        index_data = {}
        
        for model in ir_models:
            index_data[model.model] = {
                'name': model.name,
                'transient': model.transient,
                'modules': model.modules,
            }
        
        self.write({
            'system_structure_index': json.dumps(index_data, indent=2, ensure_ascii=False),
            'last_index_time': fields.Datetime.now()
        })
        return True

