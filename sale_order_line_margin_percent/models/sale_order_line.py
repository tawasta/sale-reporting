from odoo import fields, models

from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    margin_percent = fields.Float(
        string="Margin (%)",
        digits=dp.get_precision("Margin"),
        compute="_compute_margin_percent",
    )

    def _compute_margin_percent(self):
        for record in self:
            margin_percent = 0
            if record.price_subtotal:
                margin_percent = (record.margin / record.price_subtotal) * 100

            record.margin_percent = margin_percent
