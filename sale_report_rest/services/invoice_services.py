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
            ("exclude_from_invoice_tab", "=", False),
            ("move_id.move_type", "in", ["out_invoice", "out_refund"]),
        ]
        if end:
            move_domain.append(("create_date", "<=", end))

        move_lines = self.env["account.move.line"].search(move_domain)
        _logger.info("Found {} move lines".format(len(move_lines)))

        if not move_lines:
            return {"error": "No invoice lines found"}

        other_carrier = self.env["delivery.carrier"].search(
            [("is_alternative_carrier", "=", True)], limit=1
        )
        _logger.info("Generating response")
        for line in move_lines:
            product_name = line.product_id.display_name or ""
            tmpl_name = line.product_tmpl_id.display_name or ""

            tag_ids = []
            for tag in line.sale_order_id.tag_ids:
                tag_ids.append(
                    {
                        "id": tag.id,
                        "name": tag.name,
                    }
                )
            if not line.sale_order_id.tag_ids:
                tag_ids.append(
                    {
                        "id": 0,
                        "name": "",
                    }
                )

            carriers = []
            for car in line.move_id.picking_ids:
                if car.carrier_id:
                    if car.carrier_id.is_default_carrier:
                        carrier_id = car.carrier_id.id
                        carrier_name = car.carrier_id.name
                    elif other_carrier:
                        carrier_name = other_carrier.name
                        carrier_id = other_carrier.id
                elif other_carrier:
                    carrier_name = other_carrier.name
                    carrier_id = other_carrier.id

                carriers.append(
                    {
                        "id": carrier_id,
                        "name": carrier_name,
                    }
                )

            if not line.move_id.picking_ids:
                carriers.append(
                    {
                        "id": 0,
                        "name": "",
                    }
                )

            rows.append(
                {
                    "id": line.id,
                    "currency": line.currency_id.name,
                    "date": line.create_date.date().isoformat() or "",
                    "date_due": line.date_invoice
                    and line.date_invoice.isoformat()
                    or "",
                    "state": line.state,
                    "commercial_partner": line.commercial_partner_id.name,
                    "partner": line.move_partner_id.name,
                    "price_unit": line.price_unit or 0.0,
                    "price_subtotal": line.price_unit or 0.0,
                    "price_total": line.price_total or 0.0,
                    "salesperson": line.move_id.invoice_user_id.name or "",
                    "type": line.move_id.move_type or "",
                    "company": line.company_id.name or "",
                    "country": line.move_id.src_dest_country_id.name or "",
                    "journal": line.journal_id.name or "",
                    "move": line.move_id.name or "",
                    "move_id": line.move_id.id or 0,
                    "product": product_name,
                    "product_template": tmpl_name,
                    "quantity": line.quantity or 0.0,
                    "category": line.product_categ_id.name or "",
                    "uom": line.product_uom_id.name or "",
                    "order_ref": line.sale_order_id and line.sale_order_id.name or "",
                    "addresses": {
                        "partner": {
                            "name": line.move_id.sale_partner_id.name or "",
                            "street": line.move_id.sale_partner_id.street or "",
                            "city": line.move_id.sale_partner_id.city or "",
                            "zip": line.move_id.sale_partner_id.zip or "",
                            "country": line.move_id.sale_partner_id.country_id.name
                            or "",
                        },
                        "invoice": {
                            "name": line.move_id.partner_id.name or "",
                            "street": line.move_id.partner_id.street or "",
                            "city": line.move_id.partner_id.city or "",
                            "zip": line.move_id.partner_id.zip or "",
                            "country": line.move_id.partner_id.country_id.name or "",
                        },
                        "shipping": {
                            "name": line.move_id.partner_shipping_id.name or "",
                            "street": line.move_id.partner_shipping_id.street or "",
                            "city": line.move_id.partner_shipping_id.city or "",
                            "zip": line.move_id.partner_shipping_id.zip or "",
                            "country": line.move_id.partner_shipping_id.country_id.name
                            or "",
                        },
                    },
                    "carriers": carriers,
                    "sales_agent": {
                        "id": line.sales_agent.id or 0,
                        "name": line.sales_agent.name or "",
                        "invoicing": line.sales_agent.customer_default_invoice_address
                        or "",
                    },
                    "tags": tag_ids,
                    "sale_type": line.sale_order_id
                    and line.sale_order_id.sale_type
                    or "",
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
