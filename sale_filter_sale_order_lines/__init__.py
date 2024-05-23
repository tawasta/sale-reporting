from . import models

def create_cron_job(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['order.book.log'].create_cron_job()