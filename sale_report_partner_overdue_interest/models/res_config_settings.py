from odoo import fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_overdue_interest = fields.Boolean(
        string=_("Show overdue interest in sale report"),
        config_parameter='sale_report_partner_overdue_interest.show_overdue_interest'
    )