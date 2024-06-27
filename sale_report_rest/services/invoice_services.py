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


class InvoiceService(Component):
    _inherit = "base.rest.service"
    _name = "invoice.service"
    _usage = "invoice"
    _collection = "sale.rest.services"
    _description = """
        Invoice Services<br/>
        Access to the invoice services is only allowed to authenticated users.
    """

    @restapi.method(
        [(["/report"], "GET")],
        input_param=restapi.CerberusValidator(schema="_validator_report"),
    )
    def report(self, start, end=None):
        """
        GET: Get invoice analysis data. No validator for return
        since it takes so long to validate with large amount.

        :param start: string, start date of return data
        :param end: string, end date of return data
        :return: JSON
        """
        _logger.info("Generating invoice report")
        rows = []

        move_domain = [
            ("create_date", ">=", start),
        ]
        if end:
            move_domain.append(("create_date", "<=", end))

        moves = self.env["account.move"].search(move_domain)
        _logger.info("Found {} moves".format(len(moves)))

        table_query = self.env["account.invoice.report"]._table_query
        # pylint: disable=E8103
        table_query = "{} AND move.id IN {}".format(table_query, tuple(moves.ids))

        self.env.cr.execute(table_query)
        records = self.env.cr.dictfetchall()
        _logger.info("Found {} records".format(len(records)))

        currencies = self.env["res.currency"].search([])
        currency_dict = {cur.id: cur.name for cur in currencies}
        partners = self.env["res.partner"].with_context(active_test=False).search([])
        partner_dict = {part.id: part.name for part in partners}
        users = self.env["res.users"].with_context(active_test=False).search([])
        user_dict = {user.id: user.name for user in users}
        partners = self.env["res.partner"].with_context(active_test=False).search([])
        partner_dict = {part.id: part.name for part in partners}
        countries = self.env["res.country"].search([])
        country_dict = {country.id: country.name for country in countries}
        companies = self.env["res.company"].search([])
        company_dict = {comp.id: comp.name for comp in companies}
        journals = self.env["account.journal"].search([])
        journal_dict = {journal.id: journal.name for journal in journals}

        _logger.info("Generating move dict")

        move_dict = {}
        for move in moves:
            move_dict[move.id] = {
                "name": move.name or "",
                "order_ref": move.sale_id.name or "",
                "partner": {
                    "name": move.sale_partner_id.name or "",
                    "street": move.sale_partner_id.street or "",
                    "city": move.sale_partner_id.city or "",
                    "zip": move.sale_partner_id.zip or "",
                    "country": move.sale_partner_id.country_id.name or "",
                },
                "invoice": {
                    "name": move.partner_id.name or "",
                    "street": move.partner_id.street or "",
                    "city": move.partner_id.city or "",
                    "zip": move.partner_id.zip or "",
                    "country": move.partner_id.country_id.name or "",
                },
                "shipping": {
                    "name": move.partner_shipping_id.name or "",
                    "street": move.partner_shipping_id.street or "",
                    "city": move.partner_shipping_id.city or "",
                    "zip": move.partner_shipping_id.zip or "",
                    "country": move.partner_shipping_id.country_id.name or "",
                },
                "carriers": [],
                "tags": [],
            }
            for car in move.stock_picking_ids:
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

                move_dict[move.id]["carriers"].append(
                    {
                        "id": carrier_id,
                        "name": carrier_name,
                    }
                )

            if not move.stock_picking_ids:
                move_dict[move.id]["carriers"].append(
                    {
                        "id": 0,
                        "name": "",
                    }
                )

            move_dict[move.id]["sales_agent"] = {
                "id": move.sales_agent.id or 0,
                "name": move.sales_agent.name or "",
                "invoicing": move.sales_agent.customer_default_invoice_address or "",
            }

            for tag in move.sale_id.tag_ids:
                move_dict[move.id]["tags"].append(
                    {
                        "id": tag.id,
                        "name": tag.name or "",
                    }
                )
            if not move.sale_id.tag_ids:
                move_dict[move.id]["tags"].append(
                    {
                        "id": 0,
                        "name": "",
                    }
                )

        _logger.info("Move dict generated")

        products = (
            self.env["product.product"].with_context(active_test=False).search([])
        )
        product_dict = {product.id: product for product in products}
        categories = (
            self.env["product.category"].with_context(active_test=False).search([])
        )
        category_dict = {categ.id: categ.name for categ in categories}
        uoms = self.env["uom.uom"].search([])
        uom_dict = {uom.id: uom.name for uom in uoms}

        _logger.info("Generating response")
        for rec in records:
            # Skip records that aren't in time range
            if not move_dict.get(rec.get("move_id")):
                continue

            product_name = ""
            tmpl_name = ""
            product = product_dict.get(rec.get("product_id"), "")
            if product:
                product_name = product.display_name
                tmpl_name = product.product_tmpl_id.display_name

            rows.append(
                {
                    "id": rec.get("id"),
                    "currency": currency_dict.get(rec.get("company_currency_id"), ""),
                    "date": rec.get("invoice_date")
                    and rec.get("invoice_date").isoformat()
                    or "",
                    "date_due": rec.get("invoice_date_due")
                    and rec.get("invoice_date_due").isoformat()
                    or "",
                    "state": rec.get("state"),
                    "commercial_partner": partner_dict.get(
                        rec.get("commercial_partner_id"), ""
                    ),
                    "partner": partner_dict.get(rec.get("partner_id"), ""),
                    "price_average": rec.get("price_average", 0.0),
                    "price_subtotal": rec.get("price_subtotal", 0.0),
                    "salesperson": user_dict.get(rec.get("invoice_user_id"), ""),
                    "type": rec.get("move_type"),
                    "company": company_dict.get(rec.get("company_id"), ""),
                    "country": country_dict.get(rec.get("country_id"), ""),
                    "journal": journal_dict.get(rec.get("journal_id"), ""),
                    "move": move_dict.get(rec.get("move_id"), {}).get("name", ""),
                    "product": product_name,
                    "product_template": tmpl_name,
                    "quantity": rec.get("quantity", 0.0),
                    "category": category_dict.get(rec.get("product_categ_id"), ""),
                    "uom": uom_dict.get(rec.get("product_uom_id"), ""),
                    "order_ref": move_dict.get(rec.get("move_id"), {}).get(
                        "order_ref", ""
                    ),
                    "addresses": {
                        "partner": move_dict.get(rec.get("move_id"), {}).get(
                            "partner", {}
                        ),
                        "invoice": move_dict.get(rec.get("move_id"), {}).get(
                            "invoice", {}
                        ),
                        "shipping": move_dict.get(rec.get("move_id"), {}).get(
                            "shipping", {}
                        ),
                    },
                    "carriers": move_dict.get(rec.get("move_id"), {}).get(
                        "carriers", []
                    ),
                    "sales_agent": move_dict.get(rec.get("move_id"), {}).get(
                        "sales_agent", {}
                    ),
                    "tags": move_dict.get(rec.get("move_id"), {}).get("tags", []),
                }
            )

        _logger.info("Response generated")

        res = {
            "count": len(rows),
            "rows": rows,
        }
        _logger.info(
            "Sale REST API: JSON with {} rows about invoice reports".format(len(rows))
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
