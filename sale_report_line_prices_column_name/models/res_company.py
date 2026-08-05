from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    use_sale_report_price_name = fields.Boolean(default=False, store=True, copy=False)
    sale_report_price_name = fields.Char(
        string="Price column name in Sale PDF print",
        default="Amount",
        translate=True,
        copy=False,
    )
