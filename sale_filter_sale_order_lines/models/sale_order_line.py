from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def unlink(self):
        for line in self:
            log_lines = self.env["order.book.log"].search(
                [("sale_order_line", "=", line.id)]
            )
            log_lines.unlink()

        return super().unlink()
