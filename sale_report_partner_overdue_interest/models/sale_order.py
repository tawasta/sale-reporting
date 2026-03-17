from odoo import models

#  This model is used to pass the value of the toggle to
#  relay the information to the qweb template.


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def show_overdue_interest_flag(self):
        # Read the toggle from settings
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_report_partner_overdue_interest.show_overdue_interest",
                default="False",
            )
            == "True"
        )
