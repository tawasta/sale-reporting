##############################################################################
#
#    Author: Futural Oy
#    Copyright 2024 Futural Oy (https://futural.fi)
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
    "name": "Sale Report: Information Section Width Fix",
    "summary": "Adds wrapping support for the 'informations' section on SO print",
    "version": "17.0.1.2.2",
    "category": "Reporting",
    "website": "https://github.com/tawasta/sale-reporting",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": ["report/sale_report_templates.xml"],
    "assets": {
        "web.report_assets_common": [
            "sale_report_informations_section_width_fix/static/src/scss/style.scss"
        ],
    },
}
