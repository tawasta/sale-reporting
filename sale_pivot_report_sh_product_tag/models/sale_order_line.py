
from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job
import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    # Field needs to be stored so that SO lines can be grouped by it
    sh_product_tag_ids = fields.Many2one(
        comodel_name='sh.product.tag',
        store=True,
    )

    @api.onchange('product_id')
    def onchange_sh_product_tag_ids(self):
        tags = self.product_id.sh_product_tag_ids
        self.sh_product_tag_ids = tags and tags[0].id or False

    @api.multi
    @job
    def _cron_sale_order_sh_product_tags(self, batch):
        lines = self.env['sale.order.line'].search([('id', 'in', batch)])
        for line in lines:
            tags = line.product_id.sh_product_tag_ids
            line.sh_product_tag_ids = tags and tags[0].id or False
        return batch, 'Success'

    @api.multi
    @job
    def cron_compute_sh_product_tag_ids(self):
        """ Computes all Sale Order lines sh_product_tag_ids values """
        lines = self.env['sale.order.line'].search([]).filtered(
                lambda t: t.product_id.sh_product_tag_ids).ids

        batch_lines = list()
        interval = 50

        for x in range(0, len(lines), interval):
            batch_lines.append(lines[x:x+interval])

        for batch in batch_lines:
            job_desc = _(
                "Assign SH product tags to lines: {}".format(batch)
            )
            self.with_delay(description=job_desc)._cron_sale_order_sh_product_tags(batch)

        _logger.info("Cron Compute SH product tags completed")
