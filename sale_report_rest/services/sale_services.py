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
from datetime import datetime

# 3. Odoo imports (openerp):
from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


def to_date(val):
    if datetime.strptime(val, "%Y-%m-%d"):
        return val
    return None


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
    def report(self, start, end=None):
        """
        GET: Get sale analysis data. No validator for return
        since it takes so long to validate with large amount.

        :param start: string, start date of return data
        :param end: string, end date of return data
        :return: JSON
        """
        _logger.info("Generating sale report")
        rows = []

        order_domain = [
            ("create_date", ">=", start),
        ]
        if end:
            order_domain.append(("create_date", "<=", end))

        orders = self.env["sale.order"].search(order_domain)
        _logger.info("Found {} orders".format(len(orders)))

        if not orders:
            return {"error": "No sale orders found"}

        # Get data from view directly with SQL
        # pylint: disable=E8103
        sql_query = """
            SELECT *
            FROM sale_report
            WHERE order_id IN {}
        """.format(
            tuple(orders.ids)
        )
        self.env.cr.execute(sql_query)
        records = self.env.cr.dictfetchall()
        _logger.info("Found {} records".format(len(records)))

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

        _logger.info("Generating order dict")

        order_dict = {}
        for order in orders:
            order_dict[order.id] = {
                "partner": {
                    "name": order.partner_id.name or "",
                    "street": order.partner_id.street or "",
                    "city": order.partner_id.city or "",
                    "zip": order.partner_id.zip or "",
                    "country": order.partner_id.country_id.name or "",
                },
                "invoice": {
                    "name": order.partner_invoice_id.name or "",
                    "street": order.partner_invoice_id.street or "",
                    "city": order.partner_invoice_id.city or "",
                    "zip": order.partner_invoice_id.zip or "",
                    "country": order.partner_invoice_id.country_id.name or "",
                },
                "shipping": {
                    "name": order.partner_shipping_id.name or "",
                    "street": order.partner_shipping_id.street or "",
                    "city": order.partner_shipping_id.city or "",
                    "zip": order.partner_shipping_id.zip or "",
                    "country": order.partner_shipping_id.country_id.name or "",
                },
                "carriers": [],
            }
            for car in order.picking_ids:
                if car.carrier_id:
                    if car.carrier_id.is_default_carrier:
                        carrier_id = car.carrier_id.id
                        carrier_name = car.carrier_id.name
                    else:
                        other_carrier = self.env["delivery.carrier"].search(
                            [("is_alternative_carrier", "=", True)], limit=1
                        )
                        if other_carrier:
                            carrier_name = other_carrier.name
                            carrier_id = other_carrier.id

                else:
                    other_carrier = self.env["delivery.carrier"].search(
                        [("is_alternative_carrier", "=", True)], limit=1
                    )
                    if other_carrier:
                        carrier_name = other_carrier.name
                        carrier_id = other_carrier.id

                order_dict[order.id]["carriers"].append(
                    {
                        "id": carrier_id,
                        "name": carrier_name,
                    }
                )
            if not order.picking_ids:
                order_dict[order.id]["carriers"].append(
                    {
                        "id": 0,
                        "name": "",
                    }
                )

            order_dict[order.id]["sales_agent"] = {
                "id": order.sales_agent.id or 0,
                "name": order.sales_agent.name or "",
                "invoicing": order.sales_agent.customer_default_invoice_address or "",
            }

        _logger.info("Order dict generated")

        _logger.info("Generating response")
        for rec in records:
            # Skip records that aren't in time range
            if not order_dict.get(rec.get("order_id")):
                continue

            # Valuutan käsittely: Tarkistetaan ja muunnetaan tarvittaessa
            order_currency = self.env["res.currency"].browse(rec.get("currency_id"))  # Tilauksenrivin valuutta
            company_currency = self.env["res.company"].browse(rec.get("company_id")).currency_id  # Yrityksen valuutta
            euro_currency = self.env.ref("base.EUR")  # Kohdevaluutta EUR

            converted_amount = rec.get("price_subtotal") or 0.0  # Oletusarvo: alkuperäinen summa

            # Jos tilauksenrivin valuutta != yrityksen valuutta, muunna yrityksen valuuttaan
            if order_currency and order_currency != company_currency:
                converted_amount = order_currency._convert(
                    converted_amount, 
                    company_currency,  
                    self.env["res.company"].browse(rec.get("company_id")),  
                    rec.get("date") or fields.Date.today(),  
                    round=True
                )

            # Jos yrityksen valuutta != EUR, muunna EUR:ksi
            if company_currency and company_currency != euro_currency:
                converted_amount = company_currency._convert(
                    converted_amount,  
                    euro_currency,  
                    self.env["res.company"].browse(rec.get("company_id")),  
                    rec.get("date") or fields.Date.today(),  
                    round=True
                )

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
                    "euro_total": converted_amount,
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
                    "original_sale_id": self.env["sale.order"].sudo().browse(rec["original_sale_id"]).name if rec.get("original_sale_id") else "",
                    "addresses": {
                        "partner": order_dict.get(rec.get("order_id"), {}).get(
                            "partner", {}
                        ),
                        "invoice": order_dict.get(rec.get("order_id"), {}).get(
                            "invoice", {}
                        ),
                        "shipping": order_dict.get(rec.get("order_id"), {}).get(
                            "shipping", {}
                        ),
                    },
                    "carriers": order_dict.get(rec.get("order_id"), {}).get(
                        "carriers", []
                    ),
                    "sales_agent": order_dict.get(rec.get("order_id"), {}).get(
                        "sales_agent", {}
                    ),
                }
            )

        _logger.info("Response generated")

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
        schema = {
            "start": {
                "type": "string",
                "nullable": False,
                "required": True,
                "coerce": to_date,
            },
            "end": {
                "type": "string",
                "nullable": True,
                "required": False,
                "coerce": to_date,
            },
        }
        return schema
