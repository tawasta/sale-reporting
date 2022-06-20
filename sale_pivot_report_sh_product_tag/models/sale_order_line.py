import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    # Field needs to be stored so that SO lines can be grouped by it
    sh_product_tag_ids = fields.Many2one(
        comodel_name="sh.product.tag",
        store=True,
    )

    @api.model
    def create(self, vals):
        product = vals.get("product_id", False)
        if product:
            prod = self.sudo().env["product.product"].search([("id", "=", product)])
            tags = prod.sh_product_tag_ids
            vals["sh_product_tag_ids"] = tags and tags[0].id or False
        return super(SaleOrderLine, self).create(vals)

    @api.onchange("product_id")
    def onchange_sh_product_tag_ids(self):
        tags = self.product_id.sh_product_tag_ids
        self.sh_product_tag_ids = tags and tags[0].id or False

    def _cron_sale_order_sh_product_tags(self, batch):
        lines = self.env["sale.order.line"].search([("id", "in", batch)])
        for line in lines:
            tags = line.product_id.sh_product_tag_ids
            line.sh_product_tag_ids = tags and tags[0].id or False
        return batch, "Success"

    def cron_compute_sh_product_tag_ids(self):
        """Computes all Sale Order lines sh_product_tag_ids values"""
        lines = (
            self.env["sale.order.line"]
            .search([])
            .filtered(lambda t: t.product_id.sh_product_tag_ids)
            .ids
        )

        batch_lines = list()
        interval = 50

        for x in range(0, len(lines), interval):
            batch_lines.append(lines[x : x + interval])

        for batch in batch_lines:
            job_desc = _("Assign SH product tags to lines: {}").format(batch)
            self.with_delay(description=job_desc)._cron_sale_order_sh_product_tags(
                batch
            )

        _logger.info(_("Cron Compute SH product tags completed"))
