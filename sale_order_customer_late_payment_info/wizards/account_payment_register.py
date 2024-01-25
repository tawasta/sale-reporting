from odoo import models


class AccountPaymentRegister(models.TransientModel):

    _inherit = "account.payment.register"

    def action_create_payments(self):
        partner = self.partner_id

        sale_model = self.env["sale.order"]
        sale_ids = sale_model.search([("partner_id", "=", partner.id)])

        sale_model.cron_has_late_payments(sales=sale_ids)

        return super().action_create_payments()
