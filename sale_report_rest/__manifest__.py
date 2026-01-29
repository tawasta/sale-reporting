##############################################################################
#
#    Author: Futural Oy
#    Copyright 2023- Futural Oy (http://www.futural.fi)
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
    "name": "Sale Report REST (FastAPI)",
    "summary": "FastAPI endpoints for sales & invoice reporting (API key protected)",
    "version": "17.0.1.0.0",
    "category": "Reporting",
    "author": "Futural",
    "website": "https://github.com/tawasta/sale-reporting",
    "license": "AGPL-3",
    "depends": [
        "fastapi",
        "fastapi_auth_api_key",
        "auth_api_key",
        "sale_pivot_report_sh_product_tag",
        "account_invoice_pivot_report_delivery_address",
        "account_invoice_pivot_report_delivery_address_country",
        "account_invoice_pivot_report_product_template",
        "sales_agent",
        "stock_picking_invoice_link",
        "fastapi_rest_log",
    ],
    "data": [
        "data/fastapi_endpoint_data.xml",
        "views/carrier.xml",
    ],
    "external_dependencies": {"python": ["fastapi", "pydantic"]},
    "installable": True,
    "application": False,
}
