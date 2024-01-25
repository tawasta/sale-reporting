import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    has_late_payments = fields.Boolean(
        string="Payments are late",
        store=True,
        copy=False,
    )

    def _cron_has_late_payments(self, batch):
        orders = self.env["sale.order"].search([("id", "in", batch)])
        for order in orders:
            order.onchange_has_late_payments()
        return batch, "Success"

    def cron_has_late_payments(self, sales=None):
        if sales:
            orders = sales.ids
        else:
            orders = self.env["sale.order"].search([]).ids
        batch_orders = list()
        interval = 50
        for x in range(0, len(orders), interval):
            batch_orders.append(orders[x : x + interval])

        for batch in batch_orders:
            job_desc = _("Update late payment info for orders: {}").format(batch)
            self.with_delay(description=job_desc)._cron_has_late_payments(batch)

        _logger.info("Cron late payment info completed")

    @api.onchange("partner_id")
    def onchange_has_late_payments(self):
        """Check for each order if their customer has any payments due"""
        partner = self.partner_id
        now_date = fields.Datetime.now().date()

        difference = 0
        late_payments = False

        for invoice in partner.invoice_ids.filtered(
            lambda o: o.state == "posted"
        ).filtered(lambda o: o.payment_state not in ["paid", "reversed"]):
            date_due = invoice.invoice_date_due
            if date_due:
                difference = date_due - now_date

            if difference and difference.days < 0:
                late_payments = True

        if late_payments:
            self.has_late_payments = True
        else:
            self.has_late_payments = False

    @api.model
    def create(self, vals):

        partner = vals.get("partner_id", False)
        partner = self.env["res.partner"].browse(partner)

        if partner:
            now_date = fields.Datetime.now().date()

            difference = 0
            late_payments = False

            for invoice in partner.invoice_ids.filtered(
                lambda o: o.state == "posted"
            ).filtered(lambda o: o.payment_state not in ["paid", "reversed"]):
                date_due = invoice.invoice_date_due
                if date_due:
                    difference = date_due - now_date

                if difference and difference.days < 0:
                    late_payments = True

            if late_payments:
                vals["has_late_payments"] = True
            else:
                vals["has_late_payments"] = False

        return super().create(vals)
