from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, vals):
        res = super().write(vals)
        order_id = vals.get("order_id", False)
        display_type = vals.get("display_type", False)
        if order_id:
            sale = self.env["sale.order"].browse(order_id)
            if display_type and display_type == "line_section":
                if sale.report_line_mode == "only_headers":
                    vals["collapse_composition"] = True
                else:
                    vals["collapse_composition"] = False

                if sale.report_line_mode == "no_line_prices":
                    vals["collapse_prices"] = True
                else:
                    vals["collapse_prices"] = False
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            order_id = vals.get("order_id", False)
            display_type = vals.get("display_type", False)
            if order_id:
                sale = self.env["sale.order"].browse(order_id)
                if display_type and display_type == "line_section":
                    if sale.report_line_mode == "only_headers":
                        vals["collapse_composition"] = True
                    else:
                        vals["collapse_composition"] = False

                    if sale.report_line_mode == "no_line_prices":
                        vals["collapse_prices"] = True
                    else:
                        vals["collapse_prices"] = False

            display_type = vals.get("display_type", False)

        return super().create(vals_list)
