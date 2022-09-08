from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    sale_report_decimal_precision = fields.Integer(
        related="company_id.sale_report_decimal_precision",
        readonly=False,
        default=2,
        store=True,
    )
