from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_report_line_mode = fields.Selection(
        related="company_id.sale_report_line_mode",
        readonly=False,
        help="Default display mode for product lines on sale order PDF reports.",
    )
