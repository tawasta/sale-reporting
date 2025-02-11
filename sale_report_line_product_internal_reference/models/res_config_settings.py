from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_report_line_internal_reference_position = fields.Selection(
        related="company_id.sale_report_line_internal_reference_position",
        readonly=False,
    )
