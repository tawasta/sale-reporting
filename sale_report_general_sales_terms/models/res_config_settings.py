from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    sale_report_general_sales_terms_text = fields.Text(
        related="company_id.sale_report_general_sales_terms_text",
        readonly=False,
        store=True,
    )

    sale_report_general_sales_terms_hyperlink_target = fields.Char(
        related="company_id.sale_report_general_sales_terms_hyperlink_target",
        readonly=False,
        store=True,
    )
