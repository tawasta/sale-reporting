from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_overdue_interest = fields.Boolean(
        string="Show overdue interest in sale report",
        config_parameter="sale_report_partner_overdue_interest.show_overdue_interest",
    )
