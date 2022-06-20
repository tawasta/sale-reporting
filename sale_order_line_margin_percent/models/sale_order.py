##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models

from odoo.addons import decimal_precision as dp

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class SaleOrderLine(models.Model):
    # 1. Private attributes
    _inherit = "sale.order.line"

    # 2. Fields declaration
    margin_percent = fields.Float(
        string="Margin (%)",
        digits=dp.get_precision("Margin"),
        compute="_compute_margin_percent",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_margin_percent(self):
        for record in self:
            margin_percent = 0
            if record.price_subtotal:
                margin_percent = (record.margin / record.price_subtotal) * 100

            record.margin_percent = margin_percent

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class SaleOrder(models.Model):
    # 1. Private attributes
    _inherit = "sale.order"

    # 2. Fields declaration
    margin_percent = fields.Float(
        string="Margin (%)",
        digits=dp.get_precision("Margin"),
        compute="_compute_margin_percent",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_margin_percent(self):
        # Computes margin percent from SO lines
        # If sale_order_margin_ignore is in use
        margin_ignore = hasattr(self.env["product.template"], "margin_ignore")

        for record in self:
            margin_percent = 0
            if record.amount_untaxed:
                amount_untaxed = record.amount_untaxed

                if margin_ignore:
                    # Subtract ignored lines from margin percent
                    for line in record.order_line.filtered(
                        lambda l: l.product_id.margin_ignore
                    ):
                        amount_untaxed -= line.price_subtotal

                margin_percent = (
                    amount_untaxed and (record.margin / amount_untaxed) * 100 or 0.00
                )

            record.margin_percent = margin_percent

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
