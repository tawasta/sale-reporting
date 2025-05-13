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
    _logger.info("Generating invoice report (FastAPI)")
    rows = []

    domain = [
        ("date_invoice", ">=", start),
        ("exclude_from_invoice_tab", "=", False),
        ("move_id.move_type", "in", ["out_invoice", "out_refund"]),
    ]
    if end:
        domain.append(("date_invoice", "<=", end))

    lines = env["account.move.line"].search(domain)
    if not lines:
        return {"count": 0, "rows": []}

    other_carrier = env["delivery.carrier"].search([("is_alternative_carrier", "=", True)], limit=1)
    euro = env.ref("base.EUR")

    for line in lines:
        product_name = line.product_id.display_name or ""
        tmpl_name = line.product_tmpl_id.display_name or ""
        invoice_currency = line.currency_id
        company_currency = line.company_id.currency_id
        converted_amount = line.price_subtotal

        if invoice_currency != company_currency:
            converted_amount = invoice_currency._convert(
                converted_amount, company_currency, line.company_id, line.date or fields.Date.today(), round=True
            )

        if company_currency != euro:
            converted_amount = company_currency._convert(
                converted_amount, euro, line.company_id, line.date or fields.Date.today(), round=True
            )

        tag_ids = [{"id": tag.id, "name": tag.name} for tag in line.sale_order_id.tag_ids]
        if not tag_ids:
            tag_ids.append({"id": 0, "name": ""})

        carriers = []
        for pick in line.move_id.picking_ids:
            carrier = pick.carrier_id
            if carrier:
                carriers.append({"id": carrier.id, "name": carrier.name})
            elif other_carrier:
                carriers.append({"id": other_carrier.id, "name": other_carrier.name})
        if not carriers:
            carriers = [{"id": 0, "name": ""}]

        quantity = -line.quantity if line.move_id.move_type == "out_refund" else line.quantity or 0.0

        rows.append({
            "id": line.id,
            "currency": invoice_currency.name,
            "date": line.date and line.date.isoformat() or "",
            "date_invoice": line.date_invoice and line.date_invoice.isoformat() or "",
            "date_due": line.date_maturity and line.date_maturity.isoformat() or "",
            "state": line.state,
            "commercial_partner": line.commercial_partner_id.name,
            "partner": line.move_partner_id.name,
            "price_unit": line.price_unit or 0.0,
            "price_subtotal": line.price_subtotal or 0.0,
            "price_total": line.price_total or 0.0,
            "euro_total": converted_amount,
            "original_sale_id": (
                line.move_id.sale_id.original_sale_id.name
                if line.move_id.sale_id and line.move_id.sale_id.original_sale_id
                else False
            ),
            "salesperson": line.move_id.invoice_user_id.name or "",
            "type": line.move_id.move_type or "",
            "company": line.company_id.name or "",
            "country": line.move_id.src_dest_country_id.name or "",
            "journal": line.journal_id.name or "",
            "move": line.move_id.name or "",
            "move_id": line.move_id.id or 0,
            "product": product_name,
            "product_template": tmpl_name,
            "quantity": quantity,
            "category": line.product_categ_id.name or "",
            "uom": line.product_uom_id.name or "",
            "order_ref": line.sale_order_id and line.sale_order_id.name or "",
            "addresses": {
                "partner": {
                    "name": line.move_id.sale_partner_id.name or "",
                    "street": line.move_id.sale_partner_id.street or "",
                    "city": line.move_id.sale_partner_id.city or "",
                    "zip": line.move_id.sale_partner_id.zip or "",
                    "country": line.move_id.sale_partner_id.country_id.name or "",
                },
                "invoice": {
                    "name": line.move_id.partner_id.name or "",
                    "street": line.move_id.partner_id.street or "",
                    "city": line.move_id.partner_id.city or "",
                    "zip": line.move_id.partner_id.zip or "",
                    "country": line.move_id.partner_id.country_id.name or "",
                },
                "shipping": {
                    "name": line.move_id.partner_shipping_id.name or "",
                    "street": line.move_id.partner_shipping_id.street or "",
                    "city": line.move_id.partner_shipping_id.city or "",
                    "zip": line.move_id.partner_shipping_id.zip or "",
                    "country": line.move_id.partner_shipping_id.country_id.name or "",
                },
            },
            "carriers": carriers,
            "sales_agent": {
                "id": line.sales_agent.id or 0,
                "name": line.sales_agent.name or "",
                "invoicing": line.sales_agent.customer_default_invoice_address or "",
            },
            "tags": tag_ids,
            "sale_type": (
                line.sale_order_id.sale_type.code
                if line.sale_order_id and line.sale_order_id.sale_type
                else ""
            ),
        })

    _logger.info("Invoice report generated with %d rows", len(rows))
    return {"count": len(rows), "rows": rows}


@router.get("/sale/report", response_model=ReportResponse)
async def sale_report(
    env: Annotated[Environment, Depends(odoo_env)],
    start: str = Query(...),
    end: Optional[str] = Query(None),
):
    _logger.info("Generating sale report (FastAPI)")
    rows = []

    domain = [("create_date", ">=", start)]
    if end:
        domain.append(("create_date", "<=", end))

    orders = env["sale.order"].search(domain)
    if not orders:
        return {"count": 0, "rows": []}

    order_ids = tuple(orders.ids) or (0,)
    env.cr.execute(f"""
        SELECT *
        FROM sale_report
        WHERE order_id IN {order_ids}
    """)
    records = env.cr.dictfetchall()

    # Dictionaries for resolving names
    partner_dict = {p.id: p.name for p in env["res.partner"].with_context(active_test=False).search([])}
    users_dict = {u.id: u.name for u in env["res.users"].with_context(active_test=False).search([])}
    company_dict = {c.id: c.name for c in env["res.company"].search([])}
    country_dict = {c.id: c.name for c in env["res.country"].search([])}
    pricelist_dict = {pl.id: pl.name for pl in env["product.pricelist"].search([])}
    product_dict = {p.id: p.display_name for p in env["product.product"].with_context(active_test=False).search([])}
    template_dict = {t.id: t.display_name for t in env["product.template"].with_context(active_test=False).search([])}
    category_dict = {c.id: c.name for c in env["product.category"].with_context(active_test=False).search([])}
    uom_dict = {u.id: u.name for u in env["uom.uom"].search([])}

    order_dict = {}
    alt_carrier = env["delivery.carrier"].search([("is_alternative_carrier", "=", True)], limit=1)

    for order in orders:
        carriers = []
        for pick in order.picking_ids:
            if pick.carrier_id:
                if pick.carrier_id.is_default_carrier:
                    carriers.append({"id": pick.carrier_id.id, "name": pick.carrier_id.name})
                elif alt_carrier:
                    carriers.append({"id": alt_carrier.id, "name": alt_carrier.name})
            elif alt_carrier:
                carriers.append({"id": alt_carrier.id, "name": alt_carrier.name})

        if not carriers:
            carriers = [{"id": 0, "name": ""}]

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
            "carriers": carriers,
            "sales_agent": {
                "id": order.sales_agent.id or 0,
                "name": order.sales_agent.name or "",
                "invoicing": order.sales_agent.customer_default_invoice_address or "",
            },
        }

    euro = env.ref("base.EUR")

    for rec in records:
        if rec.get("order_id") not in order_dict:
            continue

        company = env["res.company"].browse(rec["company_id"])
        currency = env["res.currency"].browse(rec["currency_id"])
        company_currency = company.currency_id
        amount = rec.get("price_subtotal") or 0.0

        if currency and currency != company_currency:
            amount = currency._convert(amount, company_currency, company, rec["date"] or fields.Date.today(), round=True)
        if company_currency != euro:
            amount = company_currency._convert(amount, euro, company, rec["date"] or fields.Date.today(), round=True)

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
            "margin": rec.get("margin"),
            "delay": rec.get("delay"),
            "partner": partner_dict.get(rec.get("partner_id"), ""),
            "pricelist": pricelist_dict.get(rec.get("pricelist_id"), ""),
            "price_subtotal": rec.get("price_subtotal") or 0.0,
            "price_total": rec.get("price_total") or 0.0,
            "euro_total": amount,
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
            "sale_type": env["sale.order"].browse(rec.get("order_id")).sale_type.name
                if rec.get("order_id") and env["sale.order"].browse(rec.get("order_id")).sale_type else None,
            "uom": uom_dict.get(rec.get("product_uom"), ""),
            "quantity": rec.get("product_uom_qty") or 0.0,
            "original_sale_id": env["sale.order"].sudo().browse(rec["original_sale_id"]).name
                if rec.get("original_sale_id") else "",
            "addresses": {
                "partner": order_dict[rec["order_id"]]["partner"],
                "invoice": order_dict[rec["order_id"]]["invoice"],
                "shipping": order_dict[rec["order_id"]]["shipping"],
            },
            "carriers": order_dict[rec["order_id"]]["carriers"],
            "sales_agent": order_dict[rec["order_id"]]["sales_agent"],
        })

    _logger.info("Sale report generated with %d rows", len(rows))
    return {"count": len(rows), "rows": rows}
