from odoo import fields, models

from ..routers import sale_report_router

APP_NAME = "sale_reports"


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[(APP_NAME, "Sale Reports")],
        ondelete={APP_NAME: "cascade"},
    )

    def _get_fastapi_routers(self):
        if self.app == APP_NAME:
            return [sale_report_router]
        return super()._get_fastapi_routers()
