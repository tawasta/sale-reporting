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
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


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
        output_param=restapi.CerberusValidator(schema="_validator_return_report"),
    )
    def report(self):
        """
        GET: Get invoice analysis data

        :return: JSON
        """
        rows = []
        records = self.env["account.invoice.report"].search([])
        for rec in records:
            tmpl = rec.product_template_id
            commercial = rec.commercial_partner_id
            rows.append(
                {
                    "id": rec.id,
                    "name": rec.name,
                    "line_count": rec.nbr or 0,
                    "currency_id": rec.currency_id and rec.currency_id.name or "",
                    "date": rec.invoice_date and rec.invoice_date.isoformat() or "",
                    "date_due": rec.invoice_date_due
                    and rec.invoice_date_due.isoformat()
                    or "",
                    "state": rec.state,
                    "commercial_partner": commercial and commercial.display_name or "",
                    "partner": rec.partner_id and rec.partner_id.name or "",
                    "partner_shipping": rec.partner_shipping_id
                    and rec.partner_shipping_id.name
                    or "",
                    "price_average": rec.price_average or 0.0,
                    "price_subtotal": rec.price_subtotal or 0.0,
                    "price_total": rec.price_total or 0.0,
                    "salesperson": rec.invoice_user_id
                    and rec.invoice_user_id.name
                    or "",
                    "residual": rec.residual or 0.0,
                    "sales_agent": rec.sales_agent and rec.sales_agent.name or "",
                    "shipping_country": rec.shipping_country_id
                    and rec.shipping_country_id.name
                    or "",
                    "user_currency_price_average": rec.user_currency_price_average
                    or 0.0,
                    "user_currency_price_total": rec.user_currency_price_total or 0.0,
                    "user_currency_residual": rec.user_currency_residual or 0.0,
                    "type": rec.type,
                    "volume": rec.volume or 0.0,
                    "weight": rec.weight or 0.0,
                    "company": rec.company_id.name,
                    "country": rec.country_id and rec.country_id.name or "",
                    "journal": rec.journal_id and rec.journal_id.name or "",
                    "move": rec.move_id and rec.move_id.name or "",
                    "move_type": rec.move_type or "",
                    "payment_state": rec.payment_state or "",
                    "payment_term": rec.payment_term and rec.payment_term.name or "",
                    "product": rec.product_id
                    and rec.product_id.with_context(lang="fi_FI").display_name
                    or "",
                    "quantity": rec.quantity or 0.0,
                    "product_template": tmpl
                    and tmpl.with_context(lang="fi_FI").display_name
                    or "",
                    "category": rec.categ_id
                    and rec.categ_id.with_context(lang="fi_FI").name
                    or "",
                    "uom": rec.uom_name or "",
                }
            )
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
        return {}

    def _validator_return_search(self):
        """Validator for report return endpoint"""
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "id": {
                            "type": "integer",
                            "coerce": to_int,
                            "required": True,
                            "empty": False,
                        },
                        "name": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "line_count": {
                            "type": "integer",
                            "coerce": to_int,
                            "required": True,
                            "empty": False,
                        },
                        "currency_id": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "date": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "date_due": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "state": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "commercial_partner": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "partner": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "partner_shipping": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "price_average": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "price_subtotal": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "price_total": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "salesperson": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "residual": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "sales_agent": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "shipping_country": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "user_currency_price_average": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "user_currency_price_total": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "user_currency_residual": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "type": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "volume": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "weight": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "company": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "country": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "journal": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "move": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "move_type": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "payment_state": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "payment_term": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "product": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "quantity": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "product_template": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "category": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "uom": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                    },
                },
            },
        }
