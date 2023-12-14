from odoo import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.depends("order_line.margin", "amount_untaxed")
    def _compute_margin(self):
        for order in self:
            amount_untaxed = 0
            margin = 0
            for line in order.order_line:
                if not line.product_id.margin_ignore:
                    margin += line.margin
                    amount_untaxed += line.product_uom_qty * line.price_unit
            order.margin = margin
            order.margin_percent = amount_untaxed and margin / amount_untaxed
