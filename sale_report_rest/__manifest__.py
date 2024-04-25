##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2023- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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

{
    "name": "Sale reports REST API",
    "summary": "REST API for sales analysis and invoice analysis",
    "version": "14.0.1.3.0",
    "category": "Reporting",
    "website": "https://gitlab.com/tawasta/odoo/sale-reporting",
    "author": "Tawasta",
    "license": "AGPL-3",
    "data": [],
    "depends": [
        "base_rest_auth_api_key",
        "sale_pivot_report_sh_product_tag",
        "account_invoice_pivot_report_delivery_address",
        "account_invoice_pivot_report_delivery_address_country",
        "account_invoice_pivot_report_product_template",
        "sales_agent",
    ],
    "application": False,
    "installable": True,
}
