
from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    # Field needs to be stored so that SO lines can be grouped by it
    sh_product_tag_ids = fields.Many2one(
        comodel_name='sh.product.tag',
        compute=lambda self: self._compute_sh_product_tag_ids(),
        search=lambda self: self._search_sh_product_tag_ids(),
        store=True,
    )

    @api.multi
    def _search_sh_product_tag_ids(self, operator, value):
        """ A search function just in case """
        recs = self.search([]).filtered(
            lambda x: x.sh_product_tag_ids)
        if recs:
            return [('id', 'in', [x.id for x in recs])]

    @api.multi
    @api.depends('product_id.sh_product_tag_ids', 'product_id')
    def _compute_sh_product_tag_ids(self):
        """ Just computes all Sale Order lines sh_product_tag_ids values """
        for order in self.env['sale.order'].search([]):
            for line in order.order_line:
                tags = line.product_id.sh_product_tag_ids
                line.sh_product_tag_ids = tags and tags[0].id or False
