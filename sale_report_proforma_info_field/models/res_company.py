from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    proforma_info = fields.Text("Proforma information")
