from odoo import models, fields, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delay = fields.Float(string="Delay (days)", compute="_compute_delay", store=True)

    @api.depends("date_order", "create_date")
    def _compute_delay(self):
        for order in self:
            if order.create_date and order.date_order:
                delta = order.date_order.date() - order.create_date.date()
                order.delay = delta.days
            else:
                order.delay = 0.0
