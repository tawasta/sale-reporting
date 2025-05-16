import logging
from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from odoo import fields
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

router = APIRouter()
_logger = logging.getLogger(__name__)

def parse_date(val: str) -> datetime:
    return datetime.strptime(val, DEFAULT_SERVER_DATE_FORMAT)

class ReportResponse(BaseModel):
    count: int
    rows: list[dict]

@router.get("/invoice/report", response_model=ReportResponse)
async def invoice_report(
    env: Annotated[Environment, Depends(odoo_env)],
    start: str = Query(...),
    end: Optional[str] = Query(None),
):
    _logger.info("Generating invoice report (view-based)")
    rows = []

    domain = [("invoice_date", ">=", start)]
    if end:
        domain.append(("invoice_date", "<=", end))
    domain += [("move_type", "in", ["out_invoice", "out_refund"])]

    records = env["account.invoice.report"].search(domain)
    if not records:
        return {"count": 0, "rows": []}

    move_ids = [rec.move_id.id for rec in records if rec.move_id]
    moves = env["account.move"].browse(move_ids)
    move_dict = {}
    for move in moves:
        move_dict[move.id] = {
            "name": move.name or "",
            "order_ref": move.sale_id.name or "",
            "partner": {
                "name": move.sale_partner_id.name or "",
                "street": move.sale_partner_id.street or "",
                "city": move.sale_partner_id.city or "",
                "zip": move.sale_partner_id.zip or "",
                "country": move.sale_partner_id.country_id.name or "",
            },
            "invoice": {
                "name": move.partner_id.name or "",
                "street": move.partner_id.street or "",
                "city": move.partner_id.city or "",
                "zip": move.partner_id.zip or "",
                "country": move.partner_id.country_id.name or "",
            },
            "shipping": {
                "name": move.partner_shipping_id.name or "",
                "street": move.partner_shipping_id.street or "",
                "city": move.partner_shipping_id.city or "",
                "zip": move.partner_shipping_id.zip or "",
                "country": move.partner_shipping_id.country_id.name or "",
            },
            "carriers": [],
            "tags": [],
            "sales_agent": {
                "id": move.sales_agent.id or 0,
                "name": move.sales_agent.name or "",
                "invoicing": move.sales_agent.customer_default_invoice_address or "",
            }
        }
        for pick in move.stock_picking_ids:
            carrier = pick.carrier_id or env["delivery.carrier"].search([("is_alternative_carrier", "=", True)], limit=1)
            if carrier:
                move_dict[move.id]["carriers"].append({"id": carrier.id, "name": carrier.name})
        if not move_dict[move.id]["carriers"]:
            move_dict[move.id]["carriers"].append({"id": 0, "name": ""})

        for tag in move.sale_id.tag_ids:
            move_dict[move.id]["tags"].append({"id": tag.id, "name": tag.name or ""})
        if not move.sale_id.tag_ids:
            move_dict[move.id]["tags"].append({"id": 0, "name": ""})

    for rec in records:
        move_info = move_dict.get(rec.move_id.id, {})
        rows.append({
            "id": rec.id,
            "currency": rec.currency_id.name or "",
            "date": rec.invoice_date.isoformat() if rec.invoice_date else "",
            "date_due": rec.invoice_date_due.isoformat() if rec.invoice_date_due else "",
            "state": rec.state,
            "commercial_partner": rec.commercial_partner_id.name or "",
            "partner": rec.partner_id.name or "",
            "price_average": rec.price_average or 0.0,
            "price_subtotal": rec.price_subtotal or 0.0,
            "price_total": rec.price_total or 0.0,
            "price_margin": rec.price_margin or 0.0,
            "salesperson": rec.invoice_user_id.name or "",
            "type": rec.move_type,
            "company": rec.company_id.name or "",
            "country": rec.country_id.name or "",
            "journal": rec.journal_id.name or "",
            "move": move_info.get("name", ""),
            "move_id": rec.move_id.id if rec.move_id else 0,
            "product": rec.product_id.display_name or "",
            "product_template": rec.product_id.product_tmpl_id.display_name or "",
            "quantity": rec.quantity or 0.0,
            "category": rec.product_categ_id.name or "",
            "uom": rec.product_uom_id.name or "",
            "order_ref": move_info.get("order_ref", ""),
            "addresses": {
                "partner": move_info.get("partner", {}),
                "invoice": move_info.get("invoice", {}),
                "shipping": move_info.get("shipping", {}),
            },
            "carriers": move_info.get("carriers", []),
            "sales_agent": move_info.get("sales_agent", {}),
            "tags": move_info.get("tags", []),
        })

    _logger.info("Invoice report generated with %d rows", len(rows))
    return {"count": len(rows), "rows": rows}


@router.get("/sale/report", response_model=ReportResponse)
async def sale_report(
    env: Annotated[Environment, Depends(odoo_env)],
    start: str = Query(...),
    end: Optional[str] = Query(None),
):
    _logger.info("Generating sale report (view-based)")
    rows = []

    domain = [("date", ">=", start)]
    if end:
        domain.append(("date", "<=", end))

    records = env["sale.report"].search(domain)

    for rec in records:
        rows.append({
            "id": rec.id,
            "name": rec.name,
            "date": rec.date.isoformat() if rec.date else "",
            "state": rec.state,
            "salesperson": rec.user_id.name or "",
            "volume": rec.volume,
            "weight": rec.weight,
            "company": rec.company_id.name or "",
            "country": rec.country_id.name or "",
            "commercial_partner": rec.commercial_partner_id.name or "",
            "margin": rec.untaxed_amount_invoiced - rec.inventory_value,
            "delay": "",
            "partner": rec.partner_id.name or "",
            "pricelist": rec.pricelist_id.name or "",
            "price_subtotal": rec.price_subtotal,
            "price_total": rec.price_total,
            "euro_total": rec.price_total,
            "untaxed_amount_invoiced": rec.untaxed_amount_invoiced,
            "untaxed_amount_to_invoice": rec.untaxed_amount_to_invoice,
            "discount": rec.discount,
            "discount_amount": rec.discount_amount,
            "qty_delivered": rec.qty_delivered,
            "qty_invoiced": rec.qty_invoiced,
            "qty_to_invoice": rec.qty_to_invoice,
            "product": rec.product_id.display_name or "",
            "product_template": rec.product_tmpl_id.display_name or "",
            "category": rec.categ_id.name or "",
            "uom": rec.product_uom.name or "",
            "quantity": rec.product_uom_qty,
            "sale_type": "",
            "line_count": rec.nbr,
            "commitment_date": "",
            "addresses": {},
            "carriers": [],
            "sales_agent": {},
        })

    _logger.info("Sale report generated with %d rows", len(rows))
    return {"count": len(rows), "rows": rows}
