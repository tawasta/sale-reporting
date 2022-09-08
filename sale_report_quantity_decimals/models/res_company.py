from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    sale_report_decimal_precision = fields.Integer(
        string="Product quantity's Decimal precision on Sale report",
        help="Choose the number of decimal's shown on product quantities",
    )
