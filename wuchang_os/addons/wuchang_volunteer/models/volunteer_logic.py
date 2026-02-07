# -*- coding: utf-8 -*-
from odoo import models, fields, api
import random

class VolunteerTopologyPatrol(models.AbstractModel):
    _name = 'wuchang.volunteer.topology'
    _description = 'Topology Patrol Logic'

    @api.model
    def generate_patrol_route(self, start_point, target_area):
        """
        Generates a 'random walk' route that incidentally passes through the target area.
        This is used to check on situations without direct confrontation.
        """
        # Mock logic: Return a list of waypoints
        route = [
            f"Start: {start_point}",
            "Waypoint A: Convenience Store",
            f"Target Vicinity: {target_area} (Pass by casually)",
            "Waypoint B: Park Bench",
            "End: Community Center"
        ]
        return route

class TimeBank(models.Model):
    _name = 'wuchang.time.bank'
    _description = 'Time Bank Account'

    partner_id = fields.Many2one('res.partner', string="Volunteer", required=True)
    balance_hours = fields.Float(string="Balance (Hours)", default=0.0)
    
    def deposit_hours(self, hours):
        for record in self:
            record.balance_hours += hours
