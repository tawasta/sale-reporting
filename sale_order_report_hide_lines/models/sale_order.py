from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    report_line_mode = fields.Selection(
        selection=[
            ("normal", "Normal"),
            ("no_lines", "No Lines"),
            ("no_line_prices", "No Line Prices"),
        ],
        default=lambda self: self.env.company.sale_report_line_mode or "normal",
        required=True,
        help="Controls how product lines are shown on the PDF report for this order.",
    )
