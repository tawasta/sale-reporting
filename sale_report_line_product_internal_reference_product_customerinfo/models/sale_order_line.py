from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_customer_name = fields.Char(
        compute="_compute_product_customer_name",
    )

    @api.depends("product_id")
    def _compute_product_customer_name(self):
        # Compute a customerrinfo-based helper field to indicate the name shown
        # to the customer
        for line in self:
            if line.product_id:
                supplierinfo = line.product_id._select_customerinfo(
                    partner=line.order_partner_id
                )
                name = supplierinfo.product_name
            else:
                name = ""
            line.product_customer_name = name
