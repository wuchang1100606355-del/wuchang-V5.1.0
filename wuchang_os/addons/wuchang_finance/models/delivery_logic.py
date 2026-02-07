from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_apply_50_50_delivery_split(self):
        """Applies 50/50 split to delivery fee"""
        for order in self:
            # Find delivery lines
            lines = order.order_line.filtered(lambda l: getattr(l, "is_delivery", False))
            for line in lines:
                if line.price_unit > 0:
                    line.write({
                        "price_unit": line.price_unit * 0.5,
                        "name": f"{line.name} (50% Split)"
                    })
                    order.message_post(body="Applied 50/50 Delivery Fee Split")

