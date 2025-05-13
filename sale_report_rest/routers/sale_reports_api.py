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
    _logger.info("Generating sale report (ORM fallback)")
    rows = []

    domain = [("date_order", ">=", start)]
    if end:
        domain.append(("date_order", "<=", end))

    orders = env["sale.order"].search(domain)
    if not orders:
        return {"count": 0, "rows": []}

    euro = env.ref("base.EUR")
    alt_carrier = env["delivery.carrier"].search([("is_alternative_carrier", "=", True)], limit=1)

    for order in orders:
        carriers = []
        for pick in order.picking_ids:
            carrier = pick.carrier_id
            if carrier:
                carriers.append({"id": carrier.id, "name": carrier.name})
            elif alt_carrier:
                carriers.append({"id": alt_carrier.id, "name": alt_carrier.name})
        if not carriers:
            carriers = [{"id": 0, "name": ""}]

        addresses = {
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
        }

        for line in order.order_line:
            currency = order.currency_id
            company = order.company_id
            company_currency = company.currency_id
            amount = line.price_subtotal

            if currency != company_currency:
                amount = currency._convert(amount, company_currency, company, order.date_order or fields.Date.today(), round=True)
            if company_currency != euro:
                amount = company_currency._convert(amount, euro, company, order.date_order or fields.Date.today(), round=True)

            rows.append({
                "id": line.id,
                "name": order.name,
                "state": order.state,
                "date": order.date_order.isoformat(),
                "salesperson": order.user_id.name or "",
                "volume": line.product_id.volume * line.product_uom_qty,
                "weight": line.product_id.weight * line.product_uom_qty,
                "company": company.name,
                "country": order.partner_id.country_id.name or "",
                "commercial_partner": order.partner_id.commercial_partner_id.name or "",
                "margin": 0.0,  # Täydennä jos tarvitaan
                "delay": 0.0,   # Täydennä jos tarvitaan
                "partner": order.partner_id.name or "",
                "pricelist": order.pricelist_id.name or "",
                "price_subtotal": line.price_subtotal,
                "price_total": line.price_total,
                "euro_total": amount,
                "untaxed_amount_invoiced": line.qty_invoiced * line.price_unit,
                "untaxed_amount_to_invoice": line.qty_to_invoice * line.price_unit,
                "discount": line.discount,
                "discount_amount": line.price_unit * line.product_uom_qty * line.discount / 100.0,
                "qty_delivered": line.qty_delivered,
                "qty_invoiced": line.qty_invoiced,
                "qty_to_invoice": line.qty_to_invoice,
                "product": line.product_id.display_name,
                "product_template": line.product_id.product_tmpl_id.display_name,
                "category": line.product_id.categ_id.name,
                "sale_type": order.sale_type.name if order.sale_type else "",
                "uom": line.product_uom.name,
                "quantity": line.product_uom_qty,
                "original_sale_id": order.original_sale_id.name if order.original_sale_id else "",
                "addresses": addresses,
                "carriers": carriers,
                "sales_agent": {
                    "id": order.sales_agent.id or 0,
                    "name": order.sales_agent.name or "",
                    "invoicing": order.sales_agent.customer_default_invoice_address or "",
                },
                "line_count": len(order.order_line),
                "commitment_date": order.commitment_date.isoformat() if order.commitment_date else "",
            })

    _logger.info("Sale report generated with %d rows (ORM version)", len(rows))
    return {"count": len(rows), "rows": rows}

