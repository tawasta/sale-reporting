from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_report_line_internal_reference_position = fields.Selection(
        selection=[
            ("separate_columns", "Separate Columns"),
            ("single_column", "Single Column"),
        ],
        string="Internal Reference Column Position on Sale Order Print",
        help="With 'Single column' the field will be positioned above Description, "
        "saving horizontal space.",
        default="separate_columns",
    )
