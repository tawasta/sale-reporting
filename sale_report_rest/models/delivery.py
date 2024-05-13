from odoo import fields, models, api
from odoo.exceptions import ValidationError

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    is_default_carrier = fields.Boolean("Is Default Carrier", default=False,
        help="Check this if the carrier is the default carrier for standard deliveries.")
    is_alternative_carrier = fields.Boolean("Is Alternative Carrier", default=False,
        help="Check this if the carrier should be used as an alternative in specific cases.")

    @api.constrains('is_default_carrier', 'is_alternative_carrier')
    def _check_unique_default_alternative(self):
        if self.is_default_carrier:
            existing_default = self.search([('is_default_carrier', '=', True), ('id', '!=', self.id)], limit=1)
            if existing_default:
                raise ValidationError("A default carrier has already been set. Only one carrier can be the default at a time.")

        if self.is_alternative_carrier:
            existing_alternative = self.search([('is_alternative_carrier', '=', True), ('id', '!=', self.id)], limit=1)
            if existing_alternative:
                raise ValidationError("An alternative carrier has already been set. Only one carrier can be the alternative at a time.")
