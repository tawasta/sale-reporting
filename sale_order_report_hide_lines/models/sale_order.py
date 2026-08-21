from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    report_line_mode = fields.Selection(
        selection=[
            ("normal", "Normal"),
            ("no_line_prices", "No Line Prices"),
            ("only_headers", "Show only headers"),
        ],
        default=lambda self: self.env.company.sale_report_line_mode or "normal",
        required=True,
        help="Controls how product lines are shown on the PDF report for this order.",
    )

    @api.onchange("report_line_mode")
    def _onchange_report_line_mode(self):
        for line in self.order_line:
            if line.display_type == "line_section":
                if self.report_line_mode == "only_headers":
                    line.collapse_composition = True
                else:
                    line.collapse_composition = False

                if self.report_line_mode == "no_line_prices":
                    line.collapse_prices = True
                else:
                    line.collapse_prices = False
