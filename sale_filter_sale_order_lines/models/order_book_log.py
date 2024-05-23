from datetime import datetime

from odoo import api, fields, models


class OrderBookLog(models.Model):

    _name = "order.book.log"

    datetime = fields.Datetime(string="Date", required=True, readonly=True, store=True)

    sale_order_line = fields.Many2one(
        string="Sale Order Line",
        comodel_name="sale.order.line",
        required=True,
        readonly=True,
        store=True,
    )

    def filter_order_lines(self):
        domain = [
            ("untaxed_amount_to_invoice", ">", 0),
            ("order_partner_id.name", "not ilike", "Forecast"),
            ("qty_to_invoice", ">", 0),
            ("order_id.invoice_status", "=", "to invoice"),
            ("invoice_status", "=", "to invoice"),
            "|",
            ("state", "=", "sale"),
            ("state", "=", "done"),
        ]
        sale_order_lines = self.env["sale.order.line"].search(domain)

        for sale_order_line in sale_order_lines:
            vals = {"datetime": datetime.now(), "sale_order_line": sale_order_line.id}
            self.create(vals)

    @api.model
    def create(self, vals):
        res = super(OrderBookLog, self).create(vals)
        return res

    @api.model
    def create_cron_job(self):
        current_date = datetime.now()

        cron_data = {
            "name": "Create Order Book Log",
            "model_id": self.env.ref(
                "sale_filter_sale_order_lines.model_order_book_log"
            ).id,
            "state": "code",
            "code": "model.filter_order_lines()",
            "user_id": self.env.ref("base.user_root").id,
            "interval_number": 1,
            "interval_type": "days",
            "numbercall": -1,
            "nextcall": current_date,
        }

        existing_cron = self.env["ir.cron"].search([("code", "=", cron_data["code"])])
        if not existing_cron:
            self.env["ir.cron"].create(cron_data)
