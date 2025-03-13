from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    sh_product_tag_ids = fields.Many2one("sh.product.tag", string="Tags", readonly=True)

    def _select_sale(self):
        select = super()._select_sale()

        select += "%s" % (", l.sh_product_tag_ids AS sh_product_tag_ids")
        return select

    def _group_by_sale(self):
        group_by = super()._group_by_sale()

        group_by += "%s" % (", l.sh_product_tag_ids")
        return group_by
