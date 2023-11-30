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
    def report(self):
        """
        GET: Get invoice analysis data. No validator for return
        since it takes so long to validate with large amount.

        :return: JSON
        """
        rows = []
        sql_query = "select * from account_invoice_report"
        self.env.cr.execute(sql_query)
        records = self.env.cr.dictfetchall()
        _logger.info(
            "Started account.invoice.report REST API, {} records".format(len(records))
        )

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
        moves = self.env["account.move"].search([])
        move_dict = {move.id: move.name for move in moves}
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

        for rec in records:
            product_name = ""
            tmpl_name = ""
            product = product_dict.get(rec.get("product_id"), "")
            if product:
                product_name = product.display_name
                tmpl_name = product.product_tmpl_id.display_name

            rows.append(
                {
                    "id": rec.get("id"),
                    "name": rec.get("name"),
                    "line_count": rec.get("nbr_lines", 0),
                    "currency": currency_dict.get(rec.get("currency_id"), ""),
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
                    "residual": rec.get("residual", 0.0),
                    "type": rec.get("type"),
                    "company": company_dict.get(rec.get("company_id"), ""),
                    "country": country_dict.get(rec.get("country_id"), ""),
                    "journal": journal_dict.get(rec.get("journal_id"), ""),
                    "move": move_dict.get(rec.get("move_id"), ""),
                    "product": product_name,
                    "product_template": tmpl_name,
                    "quantity": rec.get("quantity", 0.0),
                    "category": category_dict.get(rec.get("product_categ_id"), ""),
                    "uom": uom_dict.get(rec.get("product_uom_id"), ""),
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
