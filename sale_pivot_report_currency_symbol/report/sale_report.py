from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    currency_symbol = fields.Char(string="Currency", readonly=True)

    def _from_sale(self):
        """Adds currency symbol to sales analysis"""
        from_sale = super()._from_sale()

        from_sale += (
            f"\nLEFT JOIN res_currency rc ON rc.id={self.env.company.currency_id.id}"
        )

        return from_sale

    def _select_sale(self):
        select = super()._select_sale()

        select += "{}".format("\n, rc.symbol AS currency_symbol")

        return select

    def _group_by_sale(self):
        group_by = super()._group_by_sale()

        group_by += "{}".format("\n, rc.symbol")

        return group_by
