import logging
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel

from odoo import fields
from odoo.api import Environment
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.fastapi_auth_api_key.dependencies import (
    authenticated_env_by_auth_api_key,
)
from odoo.addons.fastapi_rest_log.services.rest_logger import log_fastapi_call

router = APIRouter(dependencies=[Depends(authenticated_env_by_auth_api_key)])
_logger = logging.getLogger(__name__)


def parse_date(val: str) -> datetime:
    return datetime.strptime(val, DEFAULT_SERVER_DATE_FORMAT)


def _get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else ""


class ReportResponse(BaseModel):
    count: int
    rows: list[dict]


@router.get("/invoice/report", response_model=ReportResponse)
async def invoice_report(
    request: Request,
    env: Annotated[Environment, Depends(authenticated_env_by_auth_api_key)],
    start: str = Query(...),  # noqa
    end: Optional[str] = Query(None),  # noqa
):
    rows = []
    client_ip = _get_client_ip(request)

    move_domain = [
        ("date_invoice", ">=", start),
        ("move_id.move_type", "in", ["out_invoice", "out_refund"]),
    ]
    if end:
        move_domain.append(("date_invoice", "<=", end))

    move_lines = env["account.move.line"].search(move_domain)

    if not move_lines:
        result = {"count": 0, "rows": []}
        log_fastapi_call(
            env,
            method="GET",
            path="/sale_rest_api/invoice/report",
            payload={"start": start, "end": end},
            response=result,
            status_code=200,
            ip_address=client_ip,
        )
        return result

    other_carrier = env["delivery.carrier"].search(
        [("is_alternative_carrier", "=", True)], limit=1
    )
    euro_currency = env.ref("base.EUR")

    for line in move_lines:
        product = line.product_id
        tmpl = line.product_tmpl_id

        invoice_currency = line.currency_id
        company_currency = line.company_id.currency_id
        converted_amount = line.price_subtotal

        if invoice_currency != company_currency:
            converted_amount = invoice_currency._convert(
                converted_amount,
                company_currency,
                line.company_id,
                line.date or fields.Date.today(),
                round=True,
            )
        if company_currency != euro_currency:
            converted_amount = company_currency._convert(
                converted_amount,
                euro_currency,
                line.company_id,
                line.date or fields.Date.today(),
                round=True,
            )

        tag_ids = [
            {"id": tag.id, "name": tag.name} for tag in line.sale_order_id.tag_ids
        ] or [{"id": 0, "name": ""}]

        carriers = []
        for pick in line.move_id.picking_ids:
            carrier = pick.carrier_id or other_carrier
            if carrier:
                carriers.append({"id": carrier.id, "name": carrier.name})
        if not carriers:
            carriers.append({"id": 0, "name": ""})

        quantity = (
            -line.quantity
            if line.move_id.move_type == "out_refund"
            else line.quantity or 0.0
        )

        rows.append(
            {
                "id": line.id,
                "currency": line.currency_id.name,
                "date": line.date.isoformat() if line.date else "",
                "date_invoice": line.date_invoice.isoformat()
                if line.date_invoice
                else "",
                "date_due": line.date_maturity.isoformat()
                if line.date_maturity
                else "",
                "state": line.state,
                "commercial_partner": line.commercial_partner_id.name,
                "partner": line.move_partner_id.name,
                "discount": line.discount or 0.0,
                "discount_amount_currency": line.discount_amount_currency or 0.0,
                "price_unit": line.price_unit or 0.0,
                "price_subtotal": line.price_subtotal or 0.0,
                "price_total": line.price_total or 0.0,
                "euro_total": converted_amount,
                "original_sale_id": line.move_id.sale_id.original_sale_id.name
                if line.move_id.sale_id.original_sale_id
                else False,
                "salesperson": line.move_id.invoice_user_id.name or "",
                "type": line.move_id.move_type or "",
                "company": line.company_id.name or "",
                "country": line.move_id.src_dest_country_id.name or "",
                "journal": line.journal_id.name or "",
                "move": line.move_id.name or "",
                "move_id": line.move_id.id or 0,
                "product": product.display_name if product else "",
                "product_template": tmpl.display_name if tmpl else "",
                "quantity": quantity,
                "category": line.product_categ_id.name or "",
                "uom": line.product_uom_id.name or "",
                "order_ref": line.sale_order_id.name or "",
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
                        "country": line.move_id.partner_shipping_id.country_id.name
                        or "",
                    },
                },
                "carriers": carriers,
                "sales_agent": {
                    "id": line.sales_agent.id if line.sales_agent else 0,
                    "name": line.sales_agent.name if line.sales_agent else "",
                    "invoicing": line.sales_agent.customer_default_invoice_address
                    if line.sales_agent
                    else "",
                },
                "tags": tag_ids,
                "sale_type": line.sale_order_id.sale_type.code
                if line.sale_order_id and line.sale_order_id.sale_type
                else "",
            }
        )

    result = {"count": len(rows), "rows": rows}
    log_fastapi_call(
        env,
        method="GET",
        path="/sale_rest_api/invoice/report",
        payload={"start": start, "end": end},
        response=result,
        status_code=200,
        ip_address=client_ip,
    )
    return result


@router.get("/sale/report", response_model=ReportResponse)
async def sale_report(
    request: Request,
    env: Annotated[Environment, Depends(authenticated_env_by_auth_api_key)],
    start: str = Query(...),
    end: Optional[str] = Query(None),  # noqa
):
    rows = []
    client_ip = _get_client_ip(request)

    order_domain = [("create_date", ">=", start)]
    if end:
        order_domain.append(("create_date", "<=", end))

    orders = env["sale.order"].search(order_domain)
    if not orders:
        result = {"count": 0, "rows": []}
        log_fastapi_call(
            env,
            method="GET",
            path="/sale_rest_api/sale/report",
            payload={"start": start, "end": end},
            response=result,
            status_code=200,
            ip_address=client_ip,
        )
        return result

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
    categories = env["product.category"].with_context(active_test=False).search([])
    category_dict = {c.id: c.name for c in categories}
    uoms = env["uom.uom"].search([])
    uom_dict = {u.id: u.name for u in uoms}
    products = env["product.product"].with_context(active_test=False).search([])
    product_dict = {p.id: p for p in products}

    for order in orders:
        for line in order.order_line:
            product = product_dict.get(line.product_id.id)
            template = product.product_tmpl_id if product else None
            category = template.categ_id if template else None

            carriers = [
                {"id": pick.carrier_id.id, "name": pick.carrier_id.name}
                for pick in order.picking_ids
                if pick.carrier_id
            ] or [{"id": 0, "name": ""}]

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

            sales_agent = order.sales_agent
            sales_agent_data = {
                "id": sales_agent.id if sales_agent else 0,
                "name": sales_agent.name if sales_agent else "",
                "invoicing": sales_agent.customer_default_invoice_address
                if sales_agent
                else "",
            }

            discount_amount = (line.price_unit * line.product_uom_qty) * (
                line.discount / 100
            )

            rows.append(
                {
                    "id": order.id,
                    "name": order.name,
                    "line_count": len(order.order_line),
                    "state": order.state,
                    "date": order.date_order.isoformat() if order.date_order else "",
                    "commitment_date": order.commitment_date.isoformat()
                    if order.commitment_date
                    else "",
                    "salesperson": users_dict.get(order.user_id.id, ""),
                    "volume": order.volume,
                    "weight": order.weight,
                    "company": company_dict.get(order.company_id.id, ""),
                    "country": country_dict.get(order.partner_id.country_id.id, ""),
                    "commercial_partner": partner_dict.get(
                        order.partner_id.commercial_partner_id.id, ""
                    ),
                    "margin": (
                        line.price_subtotal - line.purchase_price * line.product_uom_qty
                    )
                    if line.purchase_price
                    else 0.0,
                    "delay": (order.date_order - order.create_date).days
                    if order.create_date and order.date_order
                    else "",
                    "partner": partner_dict.get(order.partner_id.id, ""),
                    "pricelist": pricelist_dict.get(order.pricelist_id.id, ""),
                    "price_subtotal": line.price_subtotal,
                    "price_total": line.price_total,
                    "euro_total": line.price_total,
                    "untaxed_amount_invoiced": line.untaxed_amount_invoiced,
                    "untaxed_amount_to_invoice": line.untaxed_amount_to_invoice,
                    "discount": line.discount,
                    "discount_amount": discount_amount,
                    "qty_delivered": line.qty_delivered,
                    "qty_invoiced": line.qty_invoiced,
                    "qty_to_invoice": line.qty_to_invoice,
                    "product": product.display_name if product else "",
                    "product_template": template.display_name if product else "",
                    "category": category_dict.get(category.id, "") if category else "",
                    "uom": uom_dict.get(line.product_uom.id, ""),
                    "quantity": line.product_uom_qty,
                    "addresses": addresses,
                    "carriers": carriers,
                    "sales_agent": sales_agent_data,
                }
            )

    result = {"count": len(rows), "rows": rows}
    log_fastapi_call(
        env,
        method="GET",
        path="/sale_rest_api/sale/report",
        payload={"start": start, "end": end},
        response=result,
        status_code=200,
        ip_address=client_ip,
    )
    return result
