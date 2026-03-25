from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hide_overdue_interest = fields.Boolean(
        string="Hide overdue interest in sale order report",
        config_parameter="sale_report_partner_overdue_interest.hide_overdue_interest",
    )
