from odoo import models, fields, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delay = fields.Float(string="Delay (days)", compute="_compute_delay", store=True)

    weight = fields.Float(string="Total Weight", compute="_compute_weight", store=True)

    volume = fields.Float(string="Total Volume", compute="_compute_volume", store=True)

    @api.depends("date_order", "create_date")
    def _compute_delay(self):
        for order in self:
            if order.create_date and order.date_order:
                delta = order.date_order.date() - order.create_date.date()
                order.delay = delta.days
            else:
                order.delay = 0.0

    @api.depends("order_line.product_id", "order_line.product_uom_qty")
    def _compute_volume(self):
        for order in self:
            total_volume = 0.0
            for line in order.order_line:
                if line.product_id and line.product_id.volume:
                    # Kerro rivin tuotteen tilavuus määrällä
                    total_volume += line.product_id.volume * line.product_uom_qty
            order.volume = total_volume

    @api.depends("order_line.product_id", "order_line.product_uom_qty")
    def _compute_weight(self):
        for order in self:
            order.weight = sum(
                line.product_id.weight * line.product_uom_qty
                for line in order.order_line
                if line.product_id
            )
