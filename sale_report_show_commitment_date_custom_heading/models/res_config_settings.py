from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_report_commitment_date_label = fields.Char(
        related="company_id.sale_report_commitment_date_label",
        readonly=False,
    )
