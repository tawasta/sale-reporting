from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_report_commitment_date_label = fields.Char(
        string="Sale Report: Commitment Date Label",
        translate=True,
        default="Promised Date",
        help="Label used for the commitment date field on the sales order PDF print.",
    )
