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

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component

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
        output_param=restapi.CerberusValidator(schema="_validator_return_report"),
    )
    def report(self):
        """
        GET: Get sale analysis data

        :return: JSON
        """
        rows = []
        records = self.env["sale.report"].search([])
        for rec in records:
            commercial = rec.commercial_partner_id
            rows.append({
                "id": rec.id,
                "name": rec.name,
                "line_count": rec.nbr or 0,
                "state": rec.state,
                "date": rec.date and rec.date.isoformat() or "",
                "confirmation_date": rec.confirmation_date and rec.confirmation_date or "",
                "commitment_date": rec.commitment_date and rec.commitment_date.isoformat() or "",
                "salesperson": rec.user_id and rec.user_id.name or "",
                "volume": rec.volume or 0.0,
                "weight": rec.weight or 0.0,
                "company": rec.company_id.name,
                "country": rec.country_id and rec.country_id.name or "",
                "commercial_partner": commercial and commercial.display_name or "",
                "margin": rec.margin or 0.0,
                "medium": rec.medium_id and rec.medium_id.name or "",
                "delay": rec.delay or 0.0,
                "partner": rec.partner_id and rec.partner_id.name or "",
                "pricelist": rec.pricelist_id.with_context(lang="fi_FI").name,
                "price_subtotal": rec.price_subtotal or 0.0,
                "price_total": rec.price_total or 0.0,
                "untaxed_amount_invoiced": rec.untaxed_amount_invoiced or 0.0,
                "untaxed_amount_to_invoice": rec.untaxed_amount_to_invoice or 0.0,
                "discount": rec.discount or 0.0,
                "discount_amount": rec.discount_amount or 0.0,
                "amt_invoiced": rec.amt_invoiced or 0.0,
                "amt_to_invoice": rec.amt_to_invoice or 0.0,
                "qty_delivered": rec.qty_delivered or 0.0,
                "qty_invoiced": rec.qty_invoiced or 0.0,
                "qty_to_invoice": rec.qty_to_invoice or 0.0,
                "source": rec.source_id.name or "",
                "product": rec.product_id and rec.product_id.with_context(
                    lang="fi_FI").display_name or "",
                "product_template": rec.product_tmpl_id and rec.product_tmpl_id.with_context(
                    lang="fi_FI").display_name or "",
                "category": rec.categ_id and rec.categ_id.with_context(lang="fi_FI").name or "",
                "uom": rec.product_uom.name or "",
                "quantity": rec.product_uom_qty or 0.0,
                "product_tag": rec.sh_product_tag_ids and rec.sh_product_tag_ids.name or "",
            })
        res = {
            "count": len(rows),
            "rows": rows,
        }
        _logger.info("Sale REST API: JSON with {} rows about sale reports".format(len(rows)))
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
                        "state": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "date": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "untaxed_amount_invoiced": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "untaxed_amount_to_invoice": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "salesperson": {
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
                        "qty_delivered": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "qty_invoiced": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "qty_to_invoice": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "commercial_partner": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "confirmation_date": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "commitment_date": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "discount": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "discount_amount": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "margin": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "medium": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "delay": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "partner": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "pricelist": {
                            "type": "string",
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
                        "amt_invoiced": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "amt_to_invoice": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "source": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "product": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "product": {
                            "type": "string",
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
                        "quantity": {
                            "type": "float",
                            "required": True,
                            "empty": False,
                        },
                        "product_tag": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                    },
                },
            },
        }
