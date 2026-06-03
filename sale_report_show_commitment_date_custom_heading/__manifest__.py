##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (http://www.futural.fi)
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
    "name": "Sale Report Commitment Date - Configurable Heading",
    "summary": "Makes the PDF's 'Promised Date' text configurable in settings",
    "version": "17.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/tawasta/sale-reporting",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_report_show_commitment_date"],
    "data": [
        "views/res_config_settings_views.xml",
        "report/sale_report_templates.xml",
    ],
}
