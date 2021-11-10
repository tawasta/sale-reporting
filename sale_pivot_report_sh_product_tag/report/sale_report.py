
from odoo import fields, models


class SaleReport(models.Model):

    _inherit = 'sale.report'

    sh_product_tag_ids = fields.Many2one(
        'sh.product.tag', string="Tags")

    def _query(self, with_claus='', fields=None, groupby='', from_claus=''):
        if fields is None:
            fields = {}

        fields['sh_product_tag_ids'] = ", l.sh_product_tag_ids as sh_product_tag_ids"
        groupby += ', l.sh_product_tag_ids'

        return super(SaleReport, self)._query(
            with_claus, fields, groupby, from_claus
        )
