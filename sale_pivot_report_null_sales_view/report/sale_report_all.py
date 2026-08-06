from odoo import fields, models, tools


class SaleReportAll(models.Model):
    _name = "sale.report.all"
    _description = "Sales Report of Products with or without Sales"
    _auto = False

    product_id = fields.Many2one("product.product", readonly=True)

    product_tmpl_id = fields.Many2one("product.template", readonly=True)

    price_subtotal = fields.Float(readonly=True)

    product_uom_qty = fields.Float(readonly=True)

    has_sales = fields.Boolean(readonly=True)

    no_sales = fields.Boolean(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, "sale_report_all")
        report = self.env["sale.report"]
        query = report._query()

        query_string = """
            CREATE OR REPLACE VIEW sale_report_all AS (
                SELECT
                    pp.id AS id,
                    pp.id AS product_id,
                    pt.id AS product_tmpl_id,

                    COALESCE(sr.price_subtotal, 0) AS price_subtotal,
                    COALESCE(sr.product_uom_qty, 0) AS product_uom_qty,

                    (sr.product_id IS NOT NULL) AS has_sales,
                    (sr.product_id IS NULL) AS no_sales

                FROM product_product pp
                    JOIN product_template pt ON (pt.id = pp.product_tmpl_id)

                LEFT JOIN (
                    SELECT
                        product_id,
                        SUM(price_subtotal) AS price_subtotal,
                        SUM(product_uom_qty) AS product_uom_qty
                    FROM (
                        {}
                    ) sale_report
                    GROUP BY product_id
                ) sr
                    ON sr.product_id = pp.id

                WHERE pp.active = TRUE
            )
        """

        self.env.cr.execute(query_string.format(query))  # pylint: disable=sql-injection
