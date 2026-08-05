from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_sale_report_price_name = fields.Boolean(
        related="company_id.use_sale_report_price_name",
        readonly=False,
    )
    sale_report_price_name = fields.Char(
        related="company_id.sale_report_price_name",
        readonly=False,
        translate=True,
    )
