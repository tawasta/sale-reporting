from odoo import fields, models

from ..routers import sale_router

APP_NAME = "sale_rest"


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[(APP_NAME, "Sale Rest Endpoint")], ondelete={APP_NAME: "cascade"}
    )

    def _get_fastapi_routers(self):
        if self.app == APP_NAME:
            return [sale_router]
        return super()._get_fastapi_routers()
