from odoo import models


class SaleReport(models.Model):
    _inherit = "sale.report"

    def _from_sale(self):
        """Replaces currency condition to show sale orders with
        different currencies"""
        from_sale = super()._from_sale()

        replace_string = "ON currency_table.company_id = s.company_id"
        replace_with = "ON 1=1"

        from_sale = from_sale.replace(replace_string, replace_with)

        return from_sale
