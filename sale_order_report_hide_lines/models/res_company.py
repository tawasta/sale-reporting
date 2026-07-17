from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_report_line_mode = fields.Selection(
        selection=[
            ("normal", "Normal"),
            ("no_lines", "No Lines"),
            ("no_line_prices", "No Line Prices"),
        ],
        string="Default Sale Report Line Mode",
        default="normal",
        help="Default display mode for product lines on sale order PDF reports.",
    )
