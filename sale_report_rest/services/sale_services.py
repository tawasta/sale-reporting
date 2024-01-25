##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2019- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:
import logging

# 3. Odoo imports (openerp):
from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class SaleService(Component):
    _inherit = "base.rest.service"
    _name = "sale.service"
    _usage = "sale"
    _collection = "sale.rest.services"
    _description = """
        Sale Services<br/>
        Access to the sale services is only allowed to authenticated users.
    """

    @restapi.method(
        [(["/report"], "GET")],
        input_param=restapi.CerberusValidator(schema="_validator_report"),
    )
    def report(self):
        """
        GET: Get sale analysis data. No validator for return
        since it takes so long to validate with large amount.

        :return: JSON
        """
        rows = []
        # Get data from view directly with SQL
        sql_query = "select * from sale_report"
        self.env.cr.execute(sql_query)
        records = self.env.cr.dictfetchall()
        _logger.info("Started sale.report REST API, {} records".format(len(records)))

        partners = self.env["res.partner"].with_context(active_test=False).search([])
        partner_dict = {part.id: part.name for part in partners}
        users = self.env["res.users"].with_context(active_test=False).search([])
        users_dict = {user.id: user.name for user in users}
        companies = self.env["res.company"].search([])
        company_dict = {comp.id: comp.name for comp in companies}
        countries = self.env["res.country"].search([])
        country_dict = {country.id: country.name for country in countries}
        pricelists = self.env["product.pricelist"].search([])
        pricelist_dict = {pricelist.id: pricelist.name for pricelist in pricelists}
        products = (
            self.env["product.product"].with_context(active_test=False).search([])
        )
        product_dict = {product.id: product.display_name for product in products}
        templates = (
            self.env["product.template"].with_context(active_test=False).search([])
        )
        template_dict = {tmpl.id: tmpl.display_name for tmpl in templates}
        categories = (
            self.env["product.category"].with_context(active_test=False).search([])
        )
        category_dict = {categ.id: categ.name for categ in categories}
        uoms = self.env["uom.uom"].search([])
        uom_dict = {uom.id: uom.name for uom in uoms}
        orders = self.env["sale.order"].search([])
        order_shipping_dict = {}
        for order in orders:
            order_shipping_dict[order.id] = {
                "name": order.partner_shipping_id.name or "",
                "street": order.partner_shipping_id.street or "",
                "city": order.partner_shipping_id.city or "",
                "zip": order.partner_shipping_id.zip or "",
                "country": order.partner_shipping_id.country_id.name or "",
            }

        for rec in records:
            rows.append(
                {
                    "id": rec.get("id"),
                    "name": rec.get("name"),
                    "line_count": rec.get("nbr") or 0,
                    "state": rec.get("state"),
                    "date": rec.get("date") and rec.get("date").isoformat() or "",
                    "commitment_date": rec.get("commitment_date")
                    and rec.get("commitment_date").isoformat()
                    or "",
                    "salesperson": users_dict.get(rec.get("user_id"), ""),
                    "volume": rec.get("volume"),
                    "weight": rec.get("weight"),
                    "company": company_dict.get(rec.get("company_id"), ""),
                    "country": country_dict.get(rec.get("country_id"), ""),
                    "commercial_partner": partner_dict.get(
                        rec.get("commercial_partner_id"), ""
                    ),
                    "margin": rec.get("margin"),
                    "delay": rec.get("delay"),
                    "partner": partner_dict.get(rec.get("partner_id"), ""),
                    "pricelist": pricelist_dict.get(rec.get("pricelist_id"), ""),
                    "price_subtotal": rec.get("price_subtotal") or 0.0,
                    "price_total": rec.get("price_total") or 0.0,
                    "untaxed_amount_invoiced": rec.get("untaxed_amount_invoiced")
                    or 0.0,
                    "untaxed_amount_to_invoice": rec.get("untaxed_amount_to_invoice")
                    or 0.0,
                    "discount": rec.get("discount") or 0.0,
                    "discount_amount": rec.get("discount_amount") or 0.0,
                    "qty_delivered": rec.get("qty_delivered") or 0.0,
                    "qty_invoiced": rec.get("qty_invoiced") or 0.0,
                    "qty_to_invoice": rec.get("qty_to_invoice") or 0.0,
                    "product": product_dict.get(rec.get("product_id"), ""),
                    "product_template": template_dict.get(
                        rec.get("product_tmpl_id"), ""
                    ),
                    "category": category_dict.get(rec.get("categ_id"), ""),
                    "uom": uom_dict.get(rec.get("product_uom"), ""),
                    "quantity": rec.get("product_uom_qty") or 0.0,
                    "shipping": order_shipping_dict.get(rec.get("order_id")),
                }
            )
        res = {
            "count": len(rows),
            "rows": rows,
        }
        _logger.info(
            "Sale REST API: JSON with {} rows about sale reports".format(len(rows))
        )
        return res

    # Validators
    def _validator_report(self):
        """Validator for report endpoint"""
        return {}
