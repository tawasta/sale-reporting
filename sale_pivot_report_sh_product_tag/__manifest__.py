##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021 Futural Oy (https://futural.fi)
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
    "name": "Sale Analysis - Group by SH product tags",
    "summary": "Group by SH product tags in Sale analysis pivot report",
    "version": "17.0.1.0.1",
    "category": "Reporting",
    "website": "https://github.com/tawasta/sale-reporting",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sh_product_variant_tags", "sale", "queue_job"],
    "data": ["data/ir_cron.xml", "views/sale_order.xml"],
}
