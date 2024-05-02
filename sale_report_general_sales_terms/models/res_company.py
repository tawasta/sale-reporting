from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    sale_report_general_sales_terms_text = fields.Text(
        string="General Sales Terms text for PDFs", translate=True
    )

    sale_report_general_sales_terms_hyperlink_target = fields.Char(
        string="General Sales Terms hyperlink target for PDFs"
    )
