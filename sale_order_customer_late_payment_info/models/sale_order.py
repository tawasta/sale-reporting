from odoo import _, api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    has_late_payments = fields.Boolean(
        string="Payments are late",
        compute=lambda self: self._compute_has_late_payments(),
        store=True,
    )

    late_payments_dates = fields.Text(
        string="Late payment dates",
        compute=lambda self: self._compute_has_late_payments(),
    )

    @api.depends("partner_id")
    def _compute_has_late_payments(self):
        """Check for each order if their customer has any payments due"""
        for order in self:
            partner = order.partner_id
            now_date = fields.Datetime.now().date()

            payment_dates = ""
            difference = 0
            late_payments = False

            for invoice in partner.invoice_ids:
                date_due = invoice.invoice_date_due
                if date_due:
                    difference = date_due - now_date

                if difference and difference.days < 0:
                    late_payments = True
                    if payment_dates:
                        payment_dates += "\n{} {}".format(
                            abs(difference.days), _("days")
                        )
                    else:
                        payment_dates += "{} {}".format(abs(difference.days), _("days"))

            order.late_payments_dates = payment_dates

            if late_payments:
                order.has_late_payments = True
            else:
                order.has_late_payments = False
