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
    _logger.info("Generating invoice report (BaseREST-compatible)")
    rows = []

    move_domain = [("create_date", ">=", start)]
    if end:
        move_domain.append(("create_date", "<=", end))

    moves = env["account.move"].search(move_domain)
    move_ids = moves.ids

    if not move_ids:
        return {"count": 0, "rows": []}

    report_domain = [("move_id", "in", move_ids)]
    records = env["account.invoice.report"].search(report_domain)

    if not records:
        return {"count": 0, "rows": []}

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
    _logger.info("Generating sale report using SQL from sale.report._table_query")
    rows = []

    order_domain = [("create_date", ">=", start)]
    if end:
        order_domain.append(("create_date", "<=", end))

    orders = env["sale.order"].search(order_domain)
    order_ids = orders.ids
    if not order_ids:
        return {"count": 0, "rows": []}

    # Get the dynamically generated SQL for the sale_report view
    table_query = env["sale.report"]._table_query
    sql_query = f"""
        SELECT * FROM ({table_query}) AS sale_report
        WHERE order_id IN %s
    """
    env.cr.execute(sql_query, (tuple(order_ids),))
    records = env.cr.dictfetchall()

    # Dictionaries for lookup
    partners = env["res.partner"].with_context(active_test=False).search([])
    partner_dict = {p.id: p.name for p in partners}
    users = env["res.users"].with_context(active_test=False).search([])
    users_dict = {u.id: u.name for u in users}
    companies = env["res.company"].search([])
    company_dict = {c.id: c.name for c in companies}
    countries = env["res.country"].search([])
    country_dict = {c.id: c.name for c in countries}
    pricelists = env["product.pricelist"].search([])
    pricelist_dict = {pl.id: pl.name for pl in pricelists}
    products = env["product.product"].with_context(active_test=False).search([])
    product_dict = {p.id: p.display_name for p in products}
    templates = env["product.template"].with_context(active_test=False).search([])
    template_dict = {t.id: t.display_name for t in templates}
    categories = env["product.category"].with_context(active_test=False).search([])
    category_dict = {c.id: c.name for c in categories}
    uoms = env["uom.uom"].search([])
    uom_dict = {u.id: u.name for u in uoms}

    # Order-related metadata
    order_dict = {}
    for order in orders:
        order_dict[order.id] = {
            "partner": {
                "name": order.partner_id.name or "",
                "street": order.partner_id.street or "",
                "city": order.partner_id.city or "",
                "zip": order.partner_id.zip or "",
                "country": order.partner_id.country_id.name or "",
            },
            "invoice": {
                "name": order.partner_invoice_id.name or "",
                "street": order.partner_invoice_id.street or "",
                "city": order.partner_invoice_id.city or "",
                "zip": order.partner_invoice_id.zip or "",
                "country": order.partner_invoice_id.country_id.name or "",
            },
            "shipping": {
                "name": order.partner_shipping_id.name or "",
                "street": order.partner_shipping_id.street or "",
                "city": order.partner_shipping_id.city or "",
                "zip": order.partner_shipping_id.zip or "",
                "country": order.partner_shipping_id.country_id.name or "",
            },
            "carriers": [],
            "sales_agent": {
                "id": order.sales_agent.id or 0,
                "name": order.sales_agent.name or "",
                "invoicing": order.sales_agent.customer_default_invoice_address or "",
            }
        }

        for pick in order.picking_ids:
            carrier = pick.carrier_id or env["delivery.carrier"].search([("is_alternative_carrier", "=", True)], limit=1)
            if carrier:
                order_dict[order.id]["carriers"].append({"id": carrier.id, "name": carrier.name})
        if not order_dict[order.id]["carriers"]:
            order_dict[order.id]["carriers"].append({"id": 0, "name": ""})

    # Final result rows
    for rec in records:
        oid = rec.get("order_id")
        if not order_dict.get(oid):
            continue

        rows.append({
            "id": rec.get("id"),
            "name": rec.get("name"),
            "line_count": rec.get("nbr") or 0,
            "state": rec.get("state"),
            "date": rec.get("date") and rec.get("date").isoformat() or "",
            "commitment_date": rec.get("commitment_date") and rec.get("commitment_date").isoformat() or "",
            "salesperson": users_dict.get(rec.get("user_id"), ""),
            "volume": rec.get("volume"),
            "weight": rec.get("weight"),
            "company": company_dict.get(rec.get("company_id"), ""),
            "country": country_dict.get(rec.get("country_id"), ""),
            "commercial_partner": partner_dict.get(rec.get("commercial_partner_id"), ""),
            "margin": rec.get("untaxed_amount_invoiced", 0.0) - rec.get("inventory_value", 0.0),
            "delay": rec.get("delay", ""),
            "partner": partner_dict.get(rec.get("partner_id"), ""),
            "pricelist": pricelist_dict.get(rec.get("pricelist_id"), ""),
            "price_subtotal": rec.get("price_subtotal") or 0.0,
            "price_total": rec.get("price_total") or 0.0,
            "euro_total": rec.get("price_total") or 0.0,
            "untaxed_amount_invoiced": rec.get("untaxed_amount_invoiced") or 0.0,
            "untaxed_amount_to_invoice": rec.get("untaxed_amount_to_invoice") or 0.0,
            "discount": rec.get("discount") or 0.0,
            "discount_amount": rec.get("discount_amount") or 0.0,
            "qty_delivered": rec.get("qty_delivered") or 0.0,
            "qty_invoiced": rec.get("qty_invoiced") or 0.0,
            "qty_to_invoice": rec.get("qty_to_invoice") or 0.0,
            "product": product_dict.get(rec.get("product_id"), ""),
            "product_template": template_dict.get(rec.get("product_tmpl_id"), ""),
            "category": category_dict.get(rec.get("categ_id"), ""),
            "uom": uom_dict.get(rec.get("product_uom"), ""),
            "quantity": rec.get("product_uom_qty") or 0.0,
            "addresses": order_dict[oid].get("addresses", {}),
            "carriers": order_dict[oid].get("carriers", []),
            "sales_agent": order_dict[oid].get("sales_agent", {}),
        })

    _logger.info("Sale report generated with %d rows", len(rows))
    return {"count": len(rows), "rows": rows}
