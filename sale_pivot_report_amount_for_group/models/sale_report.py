
from odoo import fields, models


class SaleReport(models.Model):

    _inherit = 'sale.report'

    untaxed_amount_to_invoice = fields.Float(
        groups="sale_pivot_report_amount_for_group.group_sale_pivot_amounts")

    untaxed_amount_invoiced = fields.Float(
        groups="sale_pivot_report_amount_for_group.group_sale_pivot_amounts")

    discount = fields.Float(
        groups="sale_pivot_report_amount_for_group.group_sale_pivot_amounts")

    discount_amount = fields.Float(
        groups="sale_pivot_report_amount_for_group.group_sale_pivot_amounts")

    price_total = fields.Float(
        groups="sale_pivot_report_amount_for_group.group_sale_pivot_amounts")

    price_subtotal = fields.Float(
        groups="sale_pivot_report_amount_for_group.group_sale_pivot_amounts")

    margin = fields.Float(
        groups="sale_pivot_report_amount_for_group.group_sale_pivot_amounts")
