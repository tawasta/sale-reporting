
from odoo import api, fields, models


class SaleReport(models.Model):

    _inherit = 'sale.report'

    product_no_sale_id = fields.Many2one(
        comodel_name='product.product', string="Product Variant ALL", readonly=True)

    def _from_sale(self):
        from_string = super()._from_sale()

#        from_string = from_string.replace(
#            "sale_order_line l",
#            "product_product p\nLEFT JOIN sale_order_line l ON l.product_id=p.id"
#        )
        #from_string = from_string.replace("LEFT JOIN product_product p ON l.product_id=p.id", "")
        #from_string = from_string.replace(
        #    "LEFT JOIN product_product p ON l.product_id=p.id",
        #    "LEFT JOIN product_product p ON 1=1"
        #)
        from_string = from_string.replace(
            "LEFT JOIN product_template t ON p.product_tmpl_id=t.id",
            "LEFT JOIN product_template t ON 1=1"
        )
        #from_string += " LEFT JOIN product_product pp_no_sale"
        #from_string += " LEFT JOIN product_product pp_no_sale ON (pp_no_sale.id != l.product_id)"
        from_string += " LEFT JOIN product_product pp_no_sale ON (1=1)"

        print("FROM STRING", from_string)

        return from_string

    def _group_by_sale(self):
        group_string = super()._group_by_sale()

        group_string = group_string.replace("l.product_id,", "pp_no_sale.id,\np.id,\nl.product_id,")

        return group_string

    def _where_sale(self):
        where_string = super()._where_sale()

        #where_string += " OR p.id IS NOT NULL"

        return where_string

    def _select_sale(self):
        select_string = super()._select_sale()

        select_string = select_string.replace("l.product_id AS product_id,", "p.id AS product_id,")
        select_string += ", pp_no_sale.id AS product_no_sale_id"

        return select_string

    #def _from_sale(self):
    #    return """
    #        product_product p
    #        LEFT JOIN sale_order_line l ON l.product_id=p.id
    #        LEFT JOIN sale_order s ON s.id=l.order_id
    #        JOIN res_partner partner ON s.partner_id = partner.id
    #        LEFT JOIN product_template t ON p.product_tmpl_id=t.id
    #        LEFT JOIN uom_uom u ON u.id=l.product_uom
    #        LEFT JOIN uom_uom u2 ON u2.id=t.uom_id
    #        JOIN {currency_table} ON currency_table.company_id = s.company_id
    #        """.format(
    #        currency_table=self.env['res.currency']._get_query_currency_table(self.env.companies.ids, fields.Date.today())
    #        )
