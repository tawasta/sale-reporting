
from odoo import api, fields, models
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
        if tags:
            self.sh_product_tag_ids = tags and tags[0].id or False

    def cron_compute_sh_product_tag_ids(self):
        """ Computes all Sale Order lines sh_product_tag_ids values """
        lines = self.env['sale.order.line'].search([]).filtered(
                lambda t: t.product_id.sh_product_tag_ids)
        for line in lines:
            tags = line.product_id.sh_product_tag_ids
            if tags:
                line.sh_product_tag_ids = tags and tags[0].id or False
        _logger.info("Cron Compute SH product tags completed")
