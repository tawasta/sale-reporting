from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_order_product_barcodes = fields.Boolean(
        config_parameter="sale_report_product_barcodes.sale_order_product_barcodes",
    )
