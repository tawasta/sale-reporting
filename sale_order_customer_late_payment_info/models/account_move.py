from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def action_post(self):
        partner = self.partner_id
        sale_model = self.env["sale.order"]
        sale_ids = sale_model.search([("partner_id", "=", partner.id)])
        if sale_ids:
            sale_model.cron_has_late_payments(sales=sale_ids)

        return super().action_post()
